import telebot
from telebot import types
import os
import time
import threading
import urllib.request
from flask import Flask
from threading import Thread
import sqlite3

# ==========================================
# 1. إعدادات السيرفر والتنشيط
# ==========================================
app = Flask('')
@app.route('/')
def home(): return "Forge is lit. Bot is alive."
def run(): app.run(host='0.0.0.0', port=8080)

def self_ping():
    while True:
        try:
            time.sleep(60)
            url = "https://forge-bot-8m1e.onrender.com" 
            urllib.request.urlopen(url, timeout=10)
        except Exception:
            pass

def keep_alive():
    t = Thread(target=run)
    t.start()
    Thread(target=self_ping, daemon=True).start()

# ==========================================
# 2. إعدادات البوت والقناة
# ==========================================
BOT_TOKEN = "9299875540:AAGklBiqDgoiqsMoKtQjxomSGo4WRL8rDQM" 
ADMIN_ID = 7118133252  
CHANNEL_USERNAME = "@gsishshsshd"

bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# 3. قاعدة البيانات
# ==========================================
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, joined_at TEXT)''')
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, joined_at) VALUES (?, ?, ?, datetime('now'))", 
              (user_id, username, first_name))
    conn.commit()
    conn.close()

def get_users_count():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    conn.close()
    return count

# ==========================================
# 4. المنتجات
# ==========================================
PRODUCTS = {
    "visa_1": {"name": "بطاقة فيزا 1$", "price": 2.00, "stock": "متوفر"},
    "stars_50": {"name": "نجوم تليجرام 50 ⭐", "price": 1.20, "stock": "متوفر 5"},
    "stars_75": {"name": "نجوم تليجرام 75 ⭐", "price": 1.70, "stock": "متوفر 5"},
    "stars_100": {"name": "نجوم تليجرام 100 ⭐", "price": 2.35, "stock": "متوفر 5"},
    "tiktok_2k": {"name": "حساب تيك توك (2.8k متابع)", "price": 7.00, "stock": "متوفر 1"},
    "tiktok_1k": {"name": "حساب تيك توك (1017 متابع)", "price": 3.00, "stock": "متوفر 1"},
    "insta_1200": {"name": "حساب انستجرام (1200 متابع)", "price": 4.00, "stock": "متوفر 1"},
    "whatsapp_sa": {"name": "رقم واتساب السعودية 🇸🇦", "price": 1.00, "stock": "متوفر 10"},
}

# ==========================================
# 5. التحقق من الاشتراك
# ==========================================
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        return False

# ==========================================
# 6. أوامر البوت
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    add_user(user_id, message.from_user.username, message.from_user.first_name)
    
    if not check_subscription(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 اشترك في القناة أولاً", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub"))
        bot.reply_to(message, "عشان تستخدم البوت والمتجر، لازم تشترك في قناتنا أولاً:", reply_markup=markup)
        return

    show_products(message.chat.id)

def show_products(chat_id):
    markup = types.InlineKeyboardMarkup()
    for key, prod in PRODUCTS.items():
        text = f"{prod['name']} — {prod['price']}$ ({prod['stock']})"
        markup.add(types.InlineKeyboardButton(text=text, callback_data=f"buy:{key}"))
    
    bot.send_message(chat_id, "اختر المنتج اللي تبيه:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def handle_check_sub(call):
    if check_subscription(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ تم التحقق بنجاح!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_products(call.message.chat.id)
    else:
        bot.answer_callback_query(call.id, "❌ أنت لم تشترك في القناة بعد!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy:'))
def handle_buy(call):
    product_key = call.data.split(":")[1]
    product = PRODUCTS.get(product_key)
    
    if not product:
        return
        
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id, 
        f"اخترت: {product['name']}\nالسعر: {product['price']}$\n\n"
        "لإتمام الطلب، تواصل مع المالك مباشرة على تيليجرام:\n"
        "👤 @Hanialakhali\n\n"
        "بعد الاتفاق والدفع، اطلب منه يفعّل طلبك."
    )

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if str(message.from_user.id) == str(ADMIN_ID):
        count = get_users_count()
        bot.reply_to(message, f"📊 عدد المستخدمين الكلي للبوت: {count}")
    else:
        bot.reply_to(message, "هذا الأمر خاص بصاحب المتجر فقط.")

# ==========================================
# 7. التشغيل
# ==========================================
if __name__ == "__main__":
    init_db()
    keep_alive()
    print("البوت شغال الحين...")
    bot.infinity_polling()