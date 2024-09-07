
import telebot
import requests
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz
from apscheduler.triggers.date import DateTrigger

bot = telebot.TeleBot("6854395221:AAHCbDQEV6ZgCw6F-Z_K6hrBHgOYF1pn0FQ")

API_URL = 'http://127.0.0.1:8000/api'  # Django API endpoint

scheduler = BackgroundScheduler()
scheduler.start()

user_payment_requests = {}

# /start command to register user
@bot.message_handler(commands=['start'])
def start(message):
    telegram_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name if message.from_user.last_name else ""
    username = message.from_user.username if message.from_user.username else ""

    # Check if the user exists in the database
    response = requests.get(f"{API_URL}/users/{telegram_id}/")
    
    if response.status_code == 404:
        # User not found, register them
        data = {
            'telegram_id': telegram_id,
            'first_name': first_name,
            'last_name': last_name,
            'username': username
        }
        requests.post(f"{API_URL}/users/", data=data)

    # Send greeting message and payment button
    markup = InlineKeyboardMarkup()
    pay_button = InlineKeyboardButton(text="To'lov qilish", callback_data='payer')
    markup.add(pay_button)

    caption_1 = f"{first_name} yaxshimisiz?\n\n😊Bu joyda sizni ko'rib turganimdan xursandman!\n\n" \
                "Rosti, hamma ham bu joygacha kela olmayapti. Chunki biznes tavakkal qilishga undaydi! Maqsadga, " \
                "millionlarga ega faqatgina tavakkal qilibgina erishilinadi.🏆\n\n" \
                "O'zim ham Uzumda savdo qilishdan oldin juda ko'p o'ylandim, pulimga kuyib qolmaymanmi, " \
                "eplay olamanmi? Savdo bo'masachi?\n\n"
    
    caption_2 = "Hammasini bir chetga surdimda, shunchaki boshladim!\nQiyinchiliklar, o'zim bilmaydigan yo'nalishlar, " \
                "analizlarsiz va yana bir qancha xatolarim evaziga kutganimdek savdoyim bolmadi.🤦\n\n" \
                "Lekin, ko'proq o'rganib, marketpleysda savdo qilish ilmlarini o'rganib, yana tavakkal qilib savdoni davom ettirdim.\n\n" \
                "💸Hozirda esa 1 mlrdan ko'proq aylanmani boshqaraman. 1000 ga yaqin shogirtlarni o'qitdim. " \
                "Ular orasida 50, 100, 200 mln aylanma qilayotganlari juda ham ko'p.\n\n"
    
    caption_3 = "Shu paytgacha bo'lgan tajribam, xatolarim, o'rganganlarim asosida 3 kunlik Workshop tayyorladim.\n\n" \
                "Workshopdan keyin Siz uzumda savdo qila olamanmi? Savdoyim o'xshaydimi? Pulimga kuyib qolmaydimi? " \
                "degan savollarizga 100% javob olasiz va Uzumda xatolarsiz muvaffaqiyatli savdoyizi yo'lga qo'yasiz!\n\n" \
                "❗️Workshop pullik bo'ladi! Bu Siz hozir 47 ming so'm to'lab risk qila olishizi sinovdan o'tkazish uchun!\n\n" \
                "Agar, Uzumda xatolarsiz, tezroq daromadga chiqib, muvaffaqiyatli savdoyizi yo'lga qo'yishni istasez " \
                "hoziroq pastdagi tugmani bosib, to'lovni amalga oshiring va Workshopga qo'shiling!"

    with open('home.jpg', 'rb') as image:
        bot.send_photo(message.chat.id, photo=image, caption=caption_1)

    bot.send_message(message.chat.id, caption_2)
    bot.send_message(message.chat.id, caption_3, reply_markup=markup)

    # Schedule follow-up message 15 minutes later
    scheduler.add_job(
        send_follow_up_message,
        DateTrigger(run_date=datetime.now(pytz.utc) + timedelta(minutes=0)),
        args=[message.chat.id, first_name] 
    )


def send_follow_up_message(chat_id, first_name):
    markup = InlineKeyboardMarkup()
    join_button = InlineKeyboardButton(text="YOPIQ KANALGA O'TISH", url="https://t.me/uzum_challange")
    markup.add(join_button)
    message_text = (
        f"{first_name}, qareng, men bitta yopiq hamjamiyat tashkil qilyapman....\n\n"
        "🔥U yerda nimalar bo'ladi:n"
        "- Bepul darslar\n"
        "- Savol javob sessiyalar\n"
        "- Va qo'shimchasiga foydalanish qo'llanmalar, Bepul analiz darslar, "
        "Uzumda sotuvchilar uchun do'konlar tahlili bo'lib turadi!\n\n"
        "✅Faqatgina bu yerga qo'shilish atigi 3 kun davom etadi.\n\n"
        "Vaqt tugamsidan pastdagi tugmani bosib qo'shilib oling👇"
    )
    bot.send_message(chat_id, message_text, reply_markup=markup)

# Payment button callback
@bot.callback_query_handler(func=lambda call: call.data == 'payer')
def payer(call):
    first_name = call.from_user.first_name
    markup = InlineKeyboardMarkup()
    pay_button = InlineKeyboardButton(text="Chekni yuborish", callback_data='pay_chek')
    adminga_button = InlineKeyboardButton(text="Admin orqali", url="https://t.me/uzumda_savdo_uz")
    markup.add(pay_button)
    markup.add(adminga_button)

    bot.send_message(call.message.chat.id, f"{first_name} Risk qilishdan qo'rqmasligizdan xursandman.\n\nWorkshop darslarini boshlashiz uchun quyidagi karta raqamga 47 ming so'm o'tkazing.\n\nKarta raqam: 8600 5729 4713 8587\n\nTo'lovni amalga oshirganingizdan keyin, to'lov chekini pastdagi 'Chekni yuborish' tugmani bosib shu yerga yuboring yoki 'Adminga yuborish' tugmasini bosib adminga yuboring!\n\nSizga Yopiq Workshoga qo'shilish uchun Kanal linkini yuboraman!", reply_markup=markup)
    
    # Track payment request
    user_payment_requests[call.from_user.id] = {
        'chat_id': call.message.chat.id,
        'timestamp': datetime.now(pytz.utc)
    }

# Callback for sending the receipt
@bot.callback_query_handler(func=lambda call: call.data == 'pay_chek')
def ask_for_receipt(call):
    first_name = call.from_user.first_name
    bot.send_message(call.message.chat.id, f"To'lov chekini skreenshot qilib, shu yerga yuboring!👇\n\n{first_name}, 10 daqiqa ichida chekingizni tekshirib, Sizga Workshop uchun dostup beraman!\n\nIltimos, faqat haqiqiy chekni rasmni yuboring!")

    # Set up a reminder
    scheduler.add_job(
        remind_user,
        DateTrigger(run_date=datetime.now(pytz.utc) + timedelta(minutes=30)),
        args=[call.from_user.id]
    )
    
def remind_user(user_id):
    chat_id = user_payment_requests.get(user_id, {}).get('chat_id')

    if chat_id:
        user = bot.get_chat_member(chat_id, user_id)
        first_name = user.user.first_name
        
        markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton(text="JOY BAND QILISH", callback_data='payer')
        markup.add(button)

        bot.send_message(
            chat_id,
            f"{first_name}, Hali ham Workshopga qo'shilmadingizmi?\n\n"
            "Workshopga qo'shilib siz quyidagi bilimlarni o'rganasiz!\n\n"
            "✅Uzumda noldan savdoni boshlashni\n"
            "✅Tovar topishni, tovar analiz qilishni\n"
            "✅Infografikalar bilan ishlashni\n"
            "✅Raqobatchilarni analiz qilishni\n"
            "✅Savdolarni oshirish strategiyalarini\n"
            "✅Savdolar tushib ketish sabablarini\n"
            "va bir qancha yana muhim mavzularni o'rganasiz!\n\n"
            "Ishoning, bu hali hammasi emas!\n\n"
            "Tez orada biz guruhga ishtirokchilarni qo'shishni boshlaymiz!\n\n"
            "Shoshiling! Hoziroq o'z joyingizni Band qilib qo'ying!",
            reply_markup=markup
        )
    else:
        print(f"User {user_id} uchun chat_id `user_payment_requests` ichida topilmadi.")

@bot.callback_query_handler(func=lambda call: call.data == 'pay')
def ask_for_receipt(call):
    first_name = call.from_user.first_name
    bot.send_message(call.message.chat.id, f"To'lov chekini skreenshot qilib, shu yerga yuboring!👇\n\n{first_name}, 10 daqiqa ichida chekingizni tekshirib, Sizga Workshop uchun dostup beraman!\n\nIltimos, faqat haqiqiy chekni rasmni yuboring!")

    # Set up a reminder
    scheduler.add_job(
        remind_user,
        DateTrigger(run_date=datetime.now(pytz.utc) + timedelta(minutes=30)),
        args=[call.from_user.id]
    )
    

# Save receipt image
import requests

@bot.message_handler(content_types=['photo'])
def save_receipt(message):
    first_name = message.from_user.first_name
    if message.photo:
        # Get the file info from Telegram
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Get the telegram_id from the message
        telegram_id = message.from_user.id
        
        # Prepare the files and data to send to the Django API
        files = {'chek': ('receipt.jpg', downloaded_file, 'image/jpeg')}
        data = {'telegram_id': telegram_id}
        
        # Make the POST request to your Django API
        response = requests.post(f"{API_URL}/payments/{telegram_id}/", files=files, data=data)
        
        # Respond based on the success or failure of the API request
        if response.status_code == 201:
            bot.send_message(message.chat.id, f"{first_name}, To'lovingizni tekshiruvda.🔍\n\nTez orada Chekni tekshirib, Sizga Workshop uchun Dostup ochib beraman!😊\n\n📌Botni yo'qotib qo'ymaslik uchun 'PIN' qilib qo'ying!")
        else:
            bot.send_message(message.chat.id, "To'lovda xatolik.")
    else:
        bot.send_message(message.chat.id, "Iltimos, faqat rasm yuboring.")

# Handle arbitrary messages and save to Django
@bot.message_handler(func=lambda message: True)
def save_message(message):
    telegram_id = message.from_user.id
    data = {}
    files = None

    # Handling different message types
    if message.text:
        data = {'text': message.text}
    elif message.photo:
        # Handle photo message
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("photo.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)
        files = {'image': open("photo.jpg", 'rb')}
    elif message.video:
        # Handle video message
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("video.mp4", 'wb') as new_file:
            new_file.write(downloaded_file)
        files = {'video': open("video.mp4", 'rb')}
    
    # Send the message data to Django API
    try:
        response = requests.post(f"{API_URL}/messages/{telegram_id}/", data=data, files=files)
        
        # Check for successful response
        if response.status_code == 201:
            bot.send_message(message.chat.id, "Xabaringiz yuborildi, admin javobini kuting.")
        else:
            bot.send_message(message.chat.id, "Xabarni yuborishda xatolik yuz berdi, iltimos qaytadan urinib ko'ring.")
    
    except Exception as e:
        # Handle any exceptions during the request
        bot.send_message(message.chat.id, "Xabarni yuborishda muammo yuz berdi.")
        print(e)
    
    finally:
        # Close files if opened
        if files:
            for file in files.values():
                file.close()

bot.polling()
