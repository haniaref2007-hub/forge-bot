import telebot
from telebot import types
import os

# --- الإعدادات الأساسية (جاهزة لك) ---
BOT_TOKEN = "9299875540:AAGklBiqDgoiqsMoKtQjxomSGo4WRL8rDQM"
ADMIN_ID = 7118133252  

bot = telebot.TeleBot(BOT_TOKEN)

PRODUCTS = {
    "tiktok_acc": {"name": "حساب تيك توك", "price": 5, "stock": 10, "data": "user:tiktok123\npass:Abc123!@#"},
    "insta_acc": {"name": "حساب انستقرام", "price": 7, "stock": 8, "data": "user:insta456\npass:Xyz789!"},
    "phone_num": {"name": "رقم وهمي", "price": 2, "stock": 50, "data": "+15551234567"},
    "py_tool": {"name": "أداة بايثون", "price": 15, "stock": 5, "data": "رابط التحميل: https://your-link.com/tool.zip"},
}

user_selections = {}
pending_orders = {}

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
            "حوّل المبلغ للمحفظة:\n`UQ...your_wallet...`\n\n"
            "بعد التحويل، ارفع صورة الإيصال هنا.",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"خطأ في اختيار المنتج: {e}")

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    try:
        user_id = message.from_user.id
        
        if user_id not in user_selections:
            bot.reply_to(message, "الرجاء اختيار منتج من القائمة أولاً عبر /start")
            return
        
        product_key = user_selections[user_id]
        product = PRODUCTS[product_key]
        
        pending_orders[message.message_id] = {
            "user_id": user_id,
            "product_key": product_key
        }
        
        markup = types.InlineKeyboardMarkup()
        approve_btn = types.InlineKeyboardButton("✅ موافق، سلمه", callback_data=f"approve:{message.message_id}")
        reject_btn = types.InlineKeyboardButton("❌ مرفوض", callback_data=f"reject:{message.message_id}")
        markup.add(approve_btn, reject_btn)
        
        bot.send_message(ADMIN_ID, 
            f"📥 طلب جديد!\nالعميل: `{user_id}`\nالمنتج: {product['name']}\nالسعر: {product['price']}$\n\n"
            "راجع الإيصال في الصورة المرفقة، واختر:",
            reply_markup=markup, parse_mode="Markdown")
        
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id)
        
        bot.reply_to(message, "✅ تم استلام الإيصال. جاري المراجعة، انتظر لحظات...")
    except Exception as e:
        print(f"خطأ في رفع الإيصال: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve:') or call.data.startswith('reject:'))
def handle_admin_action(call):
    try:
        action, msg_id = call.data.split(":")
        msg_id = int(msg_id)
        
        if msg_id not in pending_orders:
            bot.answer_callback_query(call.id, "الطلب غير موجود أو تم معالجته.", show_alert=True)
            return
        
        order = pending_orders[msg_id]
        user_id = order["user_id"]
        product_key = order["product_key"]
        product = PRODUCTS[product_key]
        
        if action == "approve":
            PRODUCTS[product_key]["stock"] -= 1
            bot.send_message(user_id, 
                f"✅ تم تأكيد الدفع!\n\n📦 منتجك:\n`{product['data']}`", 
                parse_mode="Markdown")
            bot.edit_message_text("✅ تم التسليم بنجاح.", call.message.chat.id, call.message.message_id)
        else:
            bot.send_message(user_id, "❌ عذراً، الإيصال غير صحيح. تواصل مع الدعم.")
            bot.edit_message_text("❌ تم رفض الطلب.", call.message.chat.id, call.message.message_id)
        
        del pending_orders[msg_id]
    except Exception as e:
        print(f"خطأ في معالجة الأدمن: {e}")

print("البوت شغال الحين...")
bot.infinity_polling()