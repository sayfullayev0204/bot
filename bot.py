import telebot
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '6804578580:AAERsmhp1i41HKevntUYo2v9lS8-m3oiLeg'
CHANNEL_ID = -1002072810007
PRIVATE_CHANNEL_LINK = "https://t.me/your_private_channel"
DATA_FILE = "referral_data.json"


bot = telebot.TeleBot(TOKEN)

# Ma'lumotlarni yuklash yoki bo'sh lug'at yaratish
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Ma'lumotlarni saqlash
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Kanalga a'zolikni tekshirish
def is_subscribed(user_id):
    try:
        member_status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return member_status in ["member", "administrator", "creator"]
    except Exception:
        return False

# Start komandasi
@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.chat.id)
    data = load_data()

    # Referal ID ni tekshirish
    args = message.text.split()
    if len(args) > 1:
        referrer_id = args[1]
        if referrer_id != user_id:  # Foydalanuvchi o'zini referal qila olmaydi
            if referrer_id in data:
                if user_id not in data[referrer_id]["referrals"]:
                    data[referrer_id]["referrals"].append(user_id)

    # Foydalanuvchini qo'shish
    if user_id not in data:
        data[user_id] = {"referrals": [], "invited_by": None}

    save_data(data)

    # Foydalanuvchi kanalga a'zo bo'lsa
    if is_subscribed(message.chat.id):
        # Taklif qilingan do'stlar soni 10 dan ko'p bo'lsa, faqat xabar yuborish
        if len(data[user_id]["referrals"]) >= 5:
            bot.send_message(
                message.chat.id,
                f"Tabriklaymiz! Siz 10 do‘stni taklif qildingiz! Mana yopiq kanal havolasi:\n{PRIVATE_CHANNEL_LINK}"
            )
        else:
            # Agar foydalanuvchi 10 ta do'stni taklif qilmagan bo'lsa, hech qanday xabar yubormaslik
            pass
    else:
        markup = InlineKeyboardMarkup()
        check_button = InlineKeyboardButton("Aʼzolikni tekshirish", callback_data="check_subscription")
        markup.add(check_button)

        bot.send_message(
            message.chat.id,
            f"Salom! Botdan foydalanish uchun ushbu kanalga a'zo bo'ling:\n\n"
            f"https://t.me/{bot.get_chat(CHANNEL_ID).username}\n\n"
            "A'zo bo'lganingizdan so'ng, \"Aʼzolikni tekshirish\" tugmasini bosing.",
            reply_markup=markup
        )

# Callbackni qayta ishlash
@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_subscription(call):
    user_id = str(call.message.chat.id)
    data = load_data()

    if is_subscribed(call.message.chat.id):
        # Agar a'zo bo'lsa
        referral_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
        bot.send_message(
            call.message.chat.id,
            f"Tabriklaymiz! Siz kanalga aʼzo bo‘lgansiz.\n\n"
            f"Do‘stlaringizni taklif qilish uchun ushbu xabarni ulashing\n\n"
        )
        bot.send_message(
            call.message.chat.id,
            f"Assalomu aleykum kunkursda g'alaba qozonishingiz uchun botga start bering\n\n"
            f"{referral_link}\n\n"
        )
    else:
        bot.send_message(
            call.message.chat.id,
            "Kechirasiz, siz hali kanalga aʼzo bo‘lmadingiz. Iltimos, kanalga aʼzo bo‘ling va qaytadan tekshiring."
        )

# Yangi xabarlar uchun ishlov beruvchi
@bot.message_handler(func=lambda message: True)
def check_referrals(message):
    user_id = str(message.chat.id)
    data = load_data()

    # 10 do'st taklif qilganini tekshirish
    if user_id in data and len(data[user_id]["referrals"]) >= 10:
        bot.send_message(
            message.chat.id,
            f"Tabriklaymiz! Siz 10 do‘stni taklif qildingiz! Mana yopiq kanal havolasi:\n{PRIVATE_CHANNEL_LINK}"
        )


# Botni ishga tushirish
bot.polling()
