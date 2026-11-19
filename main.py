import telebot
from telebot import types
import os
import time
import threading
import urllib.request
from flask import Flask
from threading import Thread
import psycopg2
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==========================================
# 1. إعدادات السيرفر والتنشيط
# ==========================================
app = Flask('')
@app.route('/')
def home(): return "Forge is lit. Bot is alive."
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def self_ping():
    while True:
        try:
            time.sleep(60)
            url = "https://forge-bot-8m1e.onrender.com"
            urllib.request.urlopen(url, timeout=15)
        except Exception:
            pass

def keep_alive():
    t = Thread(target=run)
    t.start()
    Thread(target=self_ping, daemon=True).start()

# ==========================================
# 2. إعدادات البوت والقناة
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "9299875540:AAGklBiqDgoiqsMoKtQjxomSGo4WRL8rDQM")
ADMIN_ID = 7118133252
CHANNEL_USERNAME = "@htpphhh" # تم تحديث القناة الجديدة هنا

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres.fjuvxbwnhdwikzsajboa:qetuoadgjl2007@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres")

bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# 3. قاعدة البيانات
# ==========================================
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id BIGINT PRIMARY KEY, username TEXT, first_name TEXT, joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()
        logging.info("DB connected")
    except Exception as e:
        logging.error(f"DB error: {e}")

def add_user(user_id, username, first_name):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO users (user_id, username, first_name) VALUES (%s, %s, %s) ON CONFLICT (user_id) DO NOTHING",
                  (user_id, username, first_name))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"add_user error: {e}")

def get_all_users():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT user_id FROM users")
        users = c.fetchall()
        conn.close()
        return [u[0] for u in users]
    except Exception:
        return []

# ==========================================
# 4. المنتجات
# ==========================================
PRODUCTS = {
    "tg_0.50": {"name": "حساب تليجرام", "price": 0.50, "stock": "متوفر 10", "category": "telegram"},
    "tg_1": {"name": "حساب تليجرام", "price": 1.00, "stock": "متوفر 10", "category": "telegram"},
    "tg_2": {"name": "حساب تليجرام", "price": 2.00, "stock": "متوفر 10", "category": "telegram"},
    "tg_3": {"name": "حساب تليجرام", "price": 3.00, "stock": "متوفر 10", "category": "telegram"},
    "tg_ma": {"name": "رقم تليجرام المغرب 🇲🇦", "price": 0.70, "stock": "متوفر 1", "category": "telegram"},

    "wa_ye": {"name": "رقم واتساب اليمن 🇾🇪", "price": 1.00, "stock": "متوفر كمية", "category": "whatsapp"},
    "wa_us": {"name": "رقم واتساب أمريكا 🇺🇸", "price": 0.75, "stock": "متوفر كمية", "category": "whatsapp"},
    "wa_eg": {"name": "رقم واتساب مصر 🇪🇬", "price": 0.90, "stock": "متوفر كمية", "category": "whatsapp"},
    "wa_jo": {"name": "رقم واتساب الأردن 🇯🇴", "price": 1.00, "stock": "متوفر كمية", "category": "whatsapp"},
    "wa_iq": {"name": "رقم واتساب العراق 🇮🇶", "price": 1.00, "stock": "متوفر كمية", "category": "whatsapp"},
    "wa_rand": {"name": "رقم واتساب عشوائي", "price": 0.70, "stock": "متوفر كمية", "category": "whatsapp"},

    "stars_50": {"name": "نجوم تليجرام 50 ⭐", "price": 1.20, "stock": "متوفر 5", "category": "stars"},
    "stars_75": {"name": "نجوم تليجرام 75 ⭐", "price": 1.70, "stock": "متوفر 5", "category": "stars"},
    "stars_100": {"name": "نجوم تليجرام 100 ⭐", "price": 2.35, "stock": "متوفر 5", "category": "stars"},

    "visa_1": {"name": "بطاقة فيزا 1$", "price": 2.00, "stock": "متوفر", "category": "other"},
    "tiktok_2k": {"name": "حساب تيك توك (3k متابع)", "price": 7.00, "stock": "متوفر 1", "category": "other"},
    "tiktok_1k": {"name": "حساب تيك توك (1017 متابع)", "price": 3.00, "stock": "متوفر 1", "category": "other"},
    "insta_1200": {"name": "حساب انستجرام (1200 متابع)", "price": 4.00, "stock": "متوفر 1", "category": "other"},
    "remote_format": {"name": "فرمتة الهاتف عن بعد", "price": 5.00, "stock": "متوفر", "category": "other"},
}

# ==========================================
# 5. التحقق من الاشتراك
# ==========================================
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.warning(f"sub check failed: {e}")
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
        # تم تحديث الرابط هنا ليفتح قناتك الجديدة
        markup.add(types.InlineKeyboardButton("📢 اشترك في القناة أولاً", url="https://t.me/htpphhh"))
        markup.add(types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub"))
        bot.reply_to(message, "عشان تستخدم البوت والمتجر، لازم تشترك في قناتنا أولاً:", reply_markup=markup)
        return

    show_main_menu(message.chat.id)

def show_main_menu(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🚀 خدمات الرشق", callback_data="cat_rush")
    )
    markup.add(
        types.InlineKeyboardButton("🟢 أرقام واتساب", callback_data="cat_whatsapp"),
        types.InlineKeyboardButton("🔵 حسابات تليجرام", callback_data="cat_telegram")
    )
    markup.add(
        types.InlineKeyboardButton("⭐ نجوم تليجرام", callback_data="cat_stars"),
        types.InlineKeyboardButton("🛒 منتجات أخرى", callback_data="cat_other")
    )
    markup.add(types.InlineKeyboardButton("🔄 تبادل (ببجي / بيس)", callback_data="trade"))
    bot.send_message(chat_id, "أهلاً بك في المتجر! اختر القسم اللي تبيه:", reply_markup=markup)

def show_category(chat_id, message_id, category):
    markup = types.InlineKeyboardMarkup()
    
    # قسم الرشق
    if category == "rush":
        markup.add(types.InlineKeyboardButton("رشق تيك توك", callback_data="rush_tiktok"))
        markup.add(types.InlineKeyboardButton("رشق انستجرام", callback_data="rush_insta"))
        markup.add(types.InlineKeyboardButton("رشق واتساب", callback_data="rush_wa"))
        markup.add(types.InlineKeyboardButton("رشق تليجرام", callback_data="rush_tg"))
        markup.add(types.InlineKeyboardButton("رشق فيسبوك", callback_data="rush_fb"))
        
        markup.add(types.InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_main"))
        
        bot.delete_message(chat_id, message_id)
        bot.send_photo(chat_id, "https://i.postimg.cc/V6kGbFGw/20261118-210921.jpg", caption="اختر المنصة لرشقها:", reply_markup=markup)
        return
        
    for key, prod in PRODUCTS.items():
        if prod["category"] == category:
            text = f"{prod['name']} — {prod['price']}$ ({prod['stock']})"
            markup.add(types.InlineKeyboardButton(text=text, callback_data=f"buy:{key}"))
            
    markup.add(types.InlineKeyboardButton("🔙 رجوع للأقسام", callback_data="back_main"))
    bot.edit_message_text("اختر المنتج اللي تبيه:", chat_id, message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def handle_back_main(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    show_main_menu(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))
def handle_category(call):
    category = call.data.split("_")[1]
    show_category(call.message.chat.id, call.message.message_id, category)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def handle_check_sub(call):
    if check_subscription(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ تم التحقق بنجاح!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_main_menu(call.message.chat.id)
    else:
        bot.answer_callback_query(call.id, "❌ أنت لم تشترك في القناة بعد!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy:'))
def handle_buy(call):
    product_key = call.data.split(":")[1]
    product = PRODUCTS.get(product_key)
    if not product:
        return
    bot.answer_callback_query(call.id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💵 شراء (تواصل مع المالك)", callback_data="contact_owner"))
    markup.add(types.InlineKeyboardButton("🔄 تبادل (ببجي / بيس)", callback_data="trade"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")) 
    
    bot.send_message(
        call.message.chat.id,
        f"اخترت: {product['name']}\nالسعر: {product['price']}$\n\nهل تبغى تشتري هذا المنتج، أو تتبادله؟",
        reply_markup=markup
    )

# --- أزرار الرشق ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('rush_'))
def handle_rush(call):
    platform = call.data.split('_')[1]
    
    rush_images = {
        "tiktok": "https://i.postimg.cc/V6kGbFGw/20261118-210921.jpg",
        "insta": "https://i.postimg.cc/FKHF1M4k/20261118-212111.jpg",
        "wa": "https://i.postimg.cc/pTnHFxck/20261118-212035.jpg",
        "tg": "https://i.postimg.cc/hPnBfkLr/20261118-212014.jpg",
        "fb": "https://i.postimg.cc/qB3Jtc92/20261118-212051.jpg"
    }
    
    names = {
        "tiktok": "تيك توك", "insta": "انستجرام", "wa": "واتساب", 
        "tg": "تليجرام", "fb": "فيسبوك"
    }
    
    bot.answer_callback_query(call.id)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع لقسم الرشق", callback_data="cat_rush"))
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    bot.send_photo(
        call.message.chat.id,
        rush_images.get(platform, rush_images["tiktok"]),
        caption=f"اخترت: رشق {names.get(platform, platform)}\n\nلإتمام الطلب، تواصل مع المالك مباشرة:\n👤 @Hanialakhali",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "contact_owner")
def handle_contact_owner(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "لإتمام الطلب، تواصل مع المالك مباشرة على تيليجرام:\n👤 @Hanialakhali")

@bot.callback_query_handler(func=lambda call: call.data == "trade")
def handle_trade(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎮 ببجي (PUBG)", callback_data="trade_pubg"))
    markup.add(types.InlineKeyboardButton("⚽ بيس (PES)", callback_data="trade_pes"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_main"))
    
    bot.edit_message_text("اختر اللعبة اللي تبغى تتبادل مقابلها:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "trade_pubg")
def handle_trade_pubg(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "🎮 *تبادل ببجي (PUBG)*\n\nتقدر تبدل أي منتج من منتجاتنا مقابل حساب ببجي.\n\nللتفاهم، تواصل مع المالك مباشرة:\n👤 @Hanialakhali", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "trade_pes")
def handle_trade_pes(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "⚽ *تبادل بيس (PES)*\n\nتقدر تبدل أي منتج من منتجاتنا مقابل حساب بيس.\n\nللتفاهم، تواصل مع المالك مباشرة:\n👤 @Hanialakhali", parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if str(message.from_user.id) == str(ADMIN_ID):
        bot.reply_to(message, "⏳ جاري الفحص الدقيق للمستخدمين (قد يأخذ دقيقة)...")
        users = get_all_users()
        active_count = 0
        
        for uid in users:
            try:
                bot.send_message(uid, ".", disable_notification=True)
                active_count += 1
            except Exception:
                pass
                
        bot.reply_to(message, f"📊 العدد الحقيقي للمستخدمين النشطين: {active_count}")
    else:
        bot.reply_to(message, "هذا الأمر خاص بصاحب المتجر فقط.")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if str(message.from_user.id) != str(ADMIN_ID):
        bot.reply_to(message, "هذا الأمر خاص بصاحب المتجر فقط.")
        return
    msg = bot.reply_to(message, "✍️ اكتب الرسالة اللي تبغى ترسلها لكل المستخدمين:")
    bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(message):
    text = message.text
    users = get_all_users()
    bot.reply_to(message, f"⏳ جاري إرسال الإشعار لـ {len(users)} مستخدم...")
    success = 0
    failed = 0
    for user_id in users:
        try:
            bot.send_message(user_id, f"📢 إشعار من المتجر:\n\n{text}")
            success += 1
            time.sleep(0.05)
        except Exception as e:
            failed += 1
            logging.warning(f"فشل الإرسال للمستخدم {user_id}: {e}")
    bot.reply_to(message, f"✅ تم إرسال الإشعار لـ {success} مستخدم.\n❌ فشل الإرسال لـ {failed} مستخدم.")

# ==========================================
# 7. التشغيل
# ==========================================
if __name__ == "__main__":
    init_db()
    keep_alive()
    logging.info("Bot starting...")
    bot.infinity_polling(timeout=30, long_polling_timeout=25)