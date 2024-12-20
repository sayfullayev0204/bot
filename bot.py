import telebot
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '7992250612:AAFztka-pZKIa4E9suGNIHSIbkB9tE-Mn-E'
CHANNEL_ID = -1001673432975
PRIVATE_CHANNEL_LINK = "https://t.me/your_private_channel"
DATA_FILE = "referral_data.json"


bot = telebot.TeleBot(TOKEN)

def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def is_subscribed(user_id):
    try:
        member_status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return member_status in ["member", "administrator", "creator"]
    except Exception:
        return False

@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.chat.id)
    data = load_data()

    args = message.text.split()
    if len(args) > 1:
        referrer_id = args[1]
        if referrer_id != user_id:  
            if referrer_id in data:
                if user_id not in data[referrer_id]["referrals"]:
                    data[referrer_id]["referrals"].append(user_id)

    if user_id not in data:
        data[user_id] = {"referrals": [], "invited_by": None}

    save_data(data)

    if is_subscribed(message.chat.id):
        referral_link = f"https://t.me/{bot.get_me().username}?start={user_id}"

        if len(data[user_id]["referrals"]) >= 10:
            bot.send_message(
                message.chat.id,
                f"Tabriklaymiz! Siz 10 do‘stni taklif qildingiz! \n\nMana yopiq kanal havolasi:\n\n{PRIVATE_CHANNEL_LINK}"
            )
        else:
            with open("img2.jpg", "rb") as photo:
                bot.send_photo(
                message.chat.id,
                    photo,
                    caption=(
                        "📢 Assalomu alaykum, hurmatli arab tili ixlosmandlari!\n\n"
                        "Sizni Luqmonjon Muftillayev tomonidan tashkil etilgan “Muammoga yechim” "
                        "nomli yopiq mentorlik guruhiga qo‘shilishga taklif qilamiz! 🌟\n\n"
                        "Bu guruh sizning arab tilida duch keladigan har qanday muammolaringiz uchun yechim topadigan joy! 🧠✅\n\n"
                        "🎯 Siz bu yerda: \n"
                        "🔹Tilni o‘rganishda yuzaga keladigan savollarga aniq javoblar;\n"
                        "🔹Foydali maslahatlar va strategiyalar;\n"
                        "🔹Eksklyuziv bilimlar va tajribalarni olish imkoniyatiga ega bo‘lasiz.\n\n"
                        "Qo‘shilish shartlari juda oddiy:\n"
                        "1️⃣ Bizning kanalga obuna bo‘ling.\n"
                        "2️⃣ 10 nafar do‘stingizni taklif qiling.\n"
                        "3️⃣ Taklif qilgan 10 nafar do‘stingiz orqali kanalga qo‘shilganingiz tasdiqlangach, "
                        "sizga yopiq guruhning maxfiy havolasi taqdim etiladi.\n\n"
                        "🌟 “Muammoga yechim” – arab tili o‘rganishda sizning ishonchli yo‘lboshchingiz bo‘ladi! "
                        "💡Imkoniyatni qo‘ldan boy bermang! Darhol obuna bo‘ling va o‘z do‘stlaringizni ham qo‘shiling. "
                        "Birgalikda o‘sish uchun ajoyib imkoniyat!\n\n"
                        f"📌 Havola ⤵️\n\n{referral_link}"
                    )
            )
            
            
            bot.send_message(
                message.chat.id,
                f"Taklif qilingan do'stlaringiz soni: {len(data[user_id]['referrals'])}/10"
            )
    else:
        markup = InlineKeyboardMarkup()
        check_button = InlineKeyboardButton("Aʼzolikni tekshirish", callback_data="check_subscription")
        markup.add(check_button)
        with open("img1.jpg", "rb") as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption=(
                    f"Muftillayev Luqmonjon kim?📝\n\n"
                    f"📌O'zbekiston xalqaro islom akademiyasi 4/4\n"
                    f"📌Arab tili eksperti\n"
                    f"📌At Tanaldan <a href=\"https://t.me/c/1673432975/2104\">C2 (muhovara-Nahv-Balog'at)</a>\n"
                    f"📌Cefrdan C1\n"
                    f"📌Sinxron Tarjimon\n"
                    f"📌400 dan ortiq B2-C1 natijali talabalar\n"
                    f"📌Dublajor\n"
                    f"📌Mudarris\n"
                    f"📌10 ta kitob va qo'llanma muallifi\n"
                    f"📌<a href=\"https://t.me/cefrnatijalar\">Natijalar</a>\n"
                    f"📌<a href=\"https://t.me/+uVgkeG2kv2dmMjAy\">Bituvchilar fikri</a>\n"
                    f"📌Qisqacha qilib aytganda arab tili sohasini O'zbekistondagi rivojiga oz bo'lsada hissasini qo'shishga harakat qilayotgan talaba.\n\n"
                ),
                parse_mode='HTML'
                )

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
        referral_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
        with open("img2.jpg", "rb") as photo:
                bot.send_photo(
                call.message.chat.id,
                    photo,
                    caption=(
                        "📢 Assalomu alaykum, hurmatli arab tili ixlosmandlari!\n\n"
                        "Sizni Luqmonjon Muftillayev tomonidan tashkil etilgan “Muammoga yechim” "
                        "nomli yopiq mentorlik guruhiga qo‘shilishga taklif qilamiz! 🌟\n\n"
                        "Bu guruh sizning arab tilida duch keladigan har qanday muammolaringiz uchun yechim topadigan joy! 🧠✅\n\n"
                        "🎯 Siz bu yerda: \n"
                        "🔹Tilni o‘rganishda yuzaga keladigan savollarga aniq javoblar;\n"
                        "🔹Foydali maslahatlar va strategiyalar;\n"
                        "🔹Eksklyuziv bilimlar va tajribalarni olish imkoniyatiga ega bo‘lasiz.\n\n"
                        "Qo‘shilish shartlari juda oddiy:\n"
                        "1️⃣ Bizning kanalga obuna bo‘ling.\n"
                        "2️⃣ 10 nafar do‘stingizni taklif qiling.\n"
                        "3️⃣ Taklif qilgan 10 nafar do‘stingiz orqali kanalga qo‘shilganingiz tasdiqlangach, "
                        "sizga yopiq guruhning maxfiy havolasi taqdim etiladi.\n\n"
                        "🌟 “Muammoga yechim” – arab tili o‘rganishda sizning ishonchli yo‘lboshchingiz bo‘ladi! "
                        "💡Imkoniyatni qo‘ldan boy bermang! Darhol obuna bo‘ling va o‘z do‘stlaringizni ham qo‘shiling. "
                        "Birgalikda o‘sish uchun ajoyib imkoniyat!\n\n"
                        f"📌 Havola ⤵️\n\n{referral_link}"
                    )
            )
            
        bot.send_message(
                call.message.chat.id,
                f"Taklif qilingan do'stlaringiz soni: {len(data[user_id]['referrals'])}/10"
            )
    else:
        bot.send_message(
            call.message.chat.id,
            "Kechirasiz, siz hali kanalga aʼzo bo‘lmadingiz. Iltimos, kanalga aʼzo bo‘ling va qaytadan tekshiring."
        )

@bot.message_handler(func=lambda message: True)
def check_referrals(message):
    user_id = str(message.chat.id)
    data = load_data()

    if user_id in data and len(data[user_id]["referrals"]) >= 10:
        bot.send_message(
            message.chat.id,
            f"Tabriklaymiz! Siz 10 do‘stni taklif qildingiz! Mana yopiq kanal havolasi:\n{PRIVATE_CHANNEL_LINK}"
        )


bot.polling()
