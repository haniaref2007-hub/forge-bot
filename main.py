import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# ==========================================
# 1. إعدادات السيرفر
# ==========================================
app = Flask('')
@app.route('/')
def home(): return "Forge is lit. Bot is alive."
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# ==========================================
# 2. إعدادات البوت
# ==========================================
BOT_TOKEN = "9299875540:AAGklBiqDgoiqsMoKtQjxomSGo4WRL8rDQM" 
ADMIN_ID = 7118133252  

bot = telebot.TeleBot(BOT_TOKEN)

# 🔥 المنتجات الجديدة (التسليم يدوي بالكامل)
PRODUCTS = {
    "tiktok_2k": {"name": "حساب تيك توك (2.8k متابع)", "price": 7, "stock": 1},
    "tiktok_1k": {"name": "حساب تيك توك (1017 متابع)", "price": 3, "stock": 1},
    "insta_1200": {"name": "حساب انستجرام (1200 متابع)", "price": 4, "stock": 1},
    "whatsapp_sa": {"name": "رقم واتساب السعودية 🇸🇦", "price": 1, "stock": 10},
}

user_selections = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    for key, prod in PRODUCTS.items():
        text = f"{prod['name']} — {prod['price']}$ (متوفر: {prod['stock']})"
        markup.add(types.InlineKeyboardButton(text=text, callback_data=f"buy:{key}"))
    
    bot.reply_to(message, "اختر المنتج اللي تبيه:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy:'))
def handle_buy(call):
    try:
        product_key = call.data.split(":")[1]
        product = PRODUCTS.get(product_key)
        
        if not product or product["stock"] <= 0:
            bot.answer_callback_query(call.id, "نفد المخزون.", show_alert=True)
            return
        
        user_selections[call.from_user.id] = product_key
        bot.answer_callback_query(call.id)
        
        bot.send_message(
            call.message.chat.id, 
            f"اخترت: {product['name']}\nالسعر: {product['price']}$\n\n"
            "لإتمام الطلب، تواصل مع المالك مباشرة على تيليجرام:\n"
            "👤 @Hanialakhali\n\n"
            "بعد الاتفاق والدفع، اطلب منه يفعّل طلبك.",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"خطأ في اختيار المنتج: {e}")

# ==========================================
# 3. تشغيل البوت
# ==========================================
if __name__ == "__main__":
    keep_alive()
    print("البوت شغال الحين...")
    bot.infinity_polling()