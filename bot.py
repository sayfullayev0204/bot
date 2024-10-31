import telebot
import requests
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz
from apscheduler.triggers.date import DateTrigger

bot = telebot.TeleBot("7378803947:AAHqiED0UWIGg9icBpIYKAmkyiokfd6nlmg")

API_URL = 'http://45.138.158.200/api'  # Django API endpoint

scheduler = BackgroundScheduler()
scheduler.start()

user_payment_requests = {}
user_registration_state = {}
# /start command to register user
@bot.message_handler(commands=['start'])
def start(message):
    telegram_id = message.from_user.id

    # Check if the user is already registered
    response = requests.get(f"{API_URL}/users/{telegram_id}/")
    
    if response.status_code == 404:  # User is not registered
        bot.send_message(message.chat.id, "Assalomu alaykum!\n\nKeling, hammasini boshlashdan oldin tanishib olaylik😊\n\nIsmingiz?")
        user_registration_state[telegram_id] = {"step": "first_name"}
    else:  # User exists
        user_data = response.json()
        first_name = user_data.get('first_name', '')  # Retrieve the first name
        
        # Check payment status
        payment_response = requests.get(f"{API_URL}/payments/{telegram_id}/")
        
        if payment_response.status_code == 200:
            payment_data = payment_response.json()
            if payment_data['is_confirmed']:
                markup = InlineKeyboardMarkup()
                button = InlineKeyboardButton(text="Adminga yozish", url="https://t.me/uzumsavdoga")
                markup.add(button)
                bot.send_message(
                    message.chat.id,
                    "Siz to'lov qilib ro'yxatdan o'tgansiz. Agar yordam kerak bo'lsa, adminga yozing.",
                    reply_markup=markup
                )
            else:
                markup = InlineKeyboardMarkup()
                button = InlineKeyboardButton(text="Adminga yozish", url="https://t.me/uzumsavdoga")
                markup.add(button)
                bot.send_message(
                    message.chat.id,
                    "To'lov qilgansiz. Tasdiqlanishini kuting!",
                    reply_markup=markup
                )
        else:
            # User is registered but hasn't paid
            send_payment_prompt(message, first_name)

def send_payment_prompt(message, first_name=""):
    bot.send_message(message.chat.id, f"{first_name}, iltimos, to'lovni amalga oshiring.")

@bot.message_handler(func=lambda message: message.from_user.id in user_registration_state)
def registration_handler(message):
    telegram_id = message.from_user.id
    state = user_registration_state[telegram_id]

    if state["step"] == "first_name":
        user_registration_state[telegram_id]["first_name"] = message.text
        bot.send_message(message.chat.id, "Telefon raqamingizni kiriting:")
        state["step"] = "phone"

    elif state["step"] == "phone":
        user_registration_state[telegram_id]["phone"] = message.text
        # Save the user data to the API
        data = {
            'telegram_id': telegram_id,
            'first_name': user_registration_state[telegram_id]["first_name"],
            'phone': user_registration_state[telegram_id]["phone"],
            'username': message.from_user.username or ""
        }
        response = requests.post(f"{API_URL}/users/", data=data)

        if response.status_code == 201:
            send_payment_prompt(message, data['first_name'])
        else:
            bot.send_message(message.chat.id, "Ro'yxatdan o'tishda xatolik yuz berdi. Qaytadan urinib ko'ring.")
        
        # Clear the registration state
        del user_registration_state[telegram_id]

def send_payment_prompt(message, first_name):
    markup = InlineKeyboardMarkup()
    pay_button = InlineKeyboardButton(text="To'lov qilish", callback_data='payer')
    markup.add(pay_button)

    caption_1 = f"Assalomu alaykum, {first_name} Men Komilxon Ashurov Uzumda savdo qilish bo'yicha mutaxassisman!\n\n" \
                "23-Sentabrdan boshlab 6 kunlik Yopiq Workshopim bo'lib o'tadi!\n" \
                "Workshopda siz:\n" \
                "✅Uzumda to'g'ri savdoni boshlashni\n" \
                "✅Tovar topishni, tovar analiz qilishni\n" \
                "✅Infografikalar bilan ishlashni\n" \
                "✅Savdolarni oshirish strategiyalarini\n" \
                "✅Savdolar tushib ketish sabablarini\n" \
                "va bir qancha yana muhim mavzularni o'rganasiz!\n\n" \
                "Workshop yopiq guruhda bo'lib o'tadi va Guruhga qo'shilish narxi 47 ming so'm!\n\n" \
                "❗️Muhim: Workshop faqat saralangan ishtirokchilar uchun!\n\n" \
                "Workshopga qo'shilish uchun pastdagi 'To'lov qilish' tugmasini bosing!"
    
    with open('home.jpg', 'rb') as image:
        send_safe_photo(message.chat.id, image, caption_1, markup)

    # Schedule follow-up message 15 minutes later
    scheduler.add_job(
        send_follow_up_message,
        DateTrigger(run_date=datetime.now(pytz.utc) + timedelta(minutes=15)),
        args=[message.chat.id, first_name] 
    )

def send_follow_up_message(chat_id, first_name):
    markup = InlineKeyboardMarkup()
    join_button = InlineKeyboardButton(text="YOPIQ KANALGA O'TISH", url="https://t.me/uzum_challange")
    markup.add(join_button)
    message_text = (
        f"{first_name}, qareng, men bitta yopiq hamjamiyat tashkil qilyapman....\n\n"
        "🔥U yerda nimalar bo'ladi:\n"
        "- Bepul darslar\n"
        "- Savol-javob sessiyalar\n"
        "- Va qo'shimchasiga foydalanish qo'llanmalar, Bepul analiz darslar, "
        "Uzumda sotuvchilar uchun do'konlar tahlili bo'lib turadi!\n\n"
        "✅Faqatgina bu yerga qo'shilish atigi 3 kun davom etadi.\n\n"
        "Vaqt tugamsidan pastdagi tugmani bosib qo'shilib oling👇"
    )
    send_safe_message(chat_id, message_text, markup)

# Safe message sending with 403 error handling
def send_safe_message(chat_id, text, reply_markup=None):
    try:
        bot.send_message(chat_id, text, reply_markup=reply_markup)
    except telebot.apihelper.ApiTelegramException as e:
        if e.error_code == 403:
            print(f"Error: User {chat_id} has blocked the bot or is unavailable.")
        else:
            print(f"Error: {e}")

# Safe photo sending with 403 error handling
def send_safe_photo(chat_id, photo, caption, reply_markup=None):
    try:
        bot.send_photo(chat_id, photo=photo, caption=caption, reply_markup=reply_markup)
    except telebot.apihelper.ApiTelegramException as e:
        if e.error_code == 403:
            print(f"Error: User {chat_id} has blocked the bot or is unavailable.")
        else:
            print(f"Error: {e}")

# Payment button callback
@bot.callback_query_handler(func=lambda call: call.data == 'payer')
def payer(call):
    first_name = call.from_user.first_name
    markup = InlineKeyboardMarkup()
    pay_button = InlineKeyboardButton(text="Chekni yuborish", callback_data='pay_chek')
    adminga_button = InlineKeyboardButton(text="Admin orqali", url="https://t.me/uzumsavdogar")
    markup.add(pay_button)
    markup.add(adminga_button)

    send_safe_message(call.message.chat.id, f"{first_name} Risk qilishdan qo'rqmasligizdan xursandman.\n\nWorkshop darslarini boshlashiz uchun quyidagi karta raqamga 47 ming so'm o'tkazing.\n\nKarta raqam: 8600 5729 4713 8587\n\nTo'lovni amalga oshirganingizdan keyin, to'lov chekini pastdagi 'Chekni yuborish' tugmasini bosib shu yerga yuboring yoki 'Adminga yuboring' tugmasini bosib adminga yuboring!", reply_markup=markup)
    
    # Track payment request
    user_payment_requests[call.from_user.id] = {
        'chat_id': call.message.chat.id,
        'timestamp': datetime.now(pytz.utc)
    }

# Callback for sending the receipt
@bot.callback_query_handler(func=lambda call: call.data == 'pay_chek')
def ask_for_receipt(call):
    first_name = call.from_user.first_name
    send_safe_message(call.message.chat.id, f"To'lov chekini skreenshot qilib, shu yerga yuboring!👇\n\n{first_name}, 10 daqiqa ichida chekingizni tekshirib, Sizga Workshop uchun dostup beraman!\n\nIltimos, faqat haqiqiy chekni rasmini yuboring!")

    # Set up a reminder
    scheduler.add_job(
        remind_user,
        DateTrigger(run_date=datetime.now(pytz.utc) + timedelta(minutes=30)),
        args=[call.from_user.id]
    )

# Reminder for payment
def remind_user(user_id):
    chat_id = user_payment_requests.get(user_id, {}).get('chat_id')

    if chat_id:
        user = bot.get_chat_member(chat_id, user_id)
        first_name = user.user.first_name
        
        markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton(text="JOY BAND QILISH", callback_data='payer')
        markup.add(button)

        send_safe_message(
            chat_id,
            f"{first_name}, Hali ham Workshopga qo'shilmadingizmi?\n\n"
            "Workshopga qo'shilib siz quyidagi bilimlarni o'rganasiz!\n\n"
            "✅Uzumda noldan savdoni boshlashni\n"
            "✅Tovar topishni, tovar analiz qilishni\n"
            "✅Savdolarni oshirish strategiyalarini va yana ko'p narsalarni\n\n"
            "Joy band qilishni istasangiz pastdagi tugmani bosing 👇",
            markup
        )

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
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    if user_payment_requests.get(user_id, False):  # Only accept photos if user pressed "To'lov qilish"
        if message.photo:
            # Get the file info from Telegram
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # Prepare the files and data to send to the Django API
            files = {'chek': ('receipt.jpg', downloaded_file, 'image/jpeg')}
            data = {'telegram_id': user_id}
            
            # Make the POST request to your Django API
            response = requests.post(f"{API_URL}/payments/{user_id}/", files=files, data=data)
            
            # Respond based on the success or failure of the API request
            if response.status_code == 201:
                bot.send_message(message.chat.id, f"{first_name}, To'lovingizni tekshiruvda.🔍\n\nTez orada Chekni tekshirib, Sizga Workshop uchun Dostup ochib beraman!😊\n\n📌Botni yo'qotib qo'ymaslik uchun 'PIN' qilib qo'ying!")
                user_payment_requests[user_id] = False  # Reset the payment state after successful receipt
            else:
                bot.send_message(message.chat.id, "To'lovda xatolik.")
        else:
            bot.send_message(message.chat.id, "Iltimos, faqat rasm yuboring.")
    else:
        markup = InlineKeyboardMarkup() 
        button = InlineKeyboardButton(text="Adminga yozish", url="https://t.me/uzumsavdogar")
        markup.add(button)
        bot.send_message(message.chat.id, "Iltimos, faqat 'To'lov qilish' tugmasini bosganingizdan keyin rasm yuboring.\n\nMuammo bor bo'lsa adminga yozing", reply_markup=markup)

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
