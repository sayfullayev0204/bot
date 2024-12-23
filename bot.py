import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import urllib
import logging

API_TOKEN = '7828651431:AAELpI8DuJFcq-M3B6nhPQv_xhJ41QnkeQI'
web_url = "https://cargobot-production.up.railway.app"

bot = telebot.TeleBot(API_TOKEN)

def get_user_photo_url(user_id):
    """Fetches the user's profile photo URL."""
    try:
        photos = bot.get_user_profile_photos(user_id)
        if photos.total_count > 0:
            file_id = photos.photos[0][0].file_id
            file = bot.get_file(file_id)
            photo_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file.file_path}"
            return photo_url
    except Exception as e:
        logging.error(f"Profile photo could not be fetched: {e}")
    return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    tg_id = message.from_user.id  
    username = message.from_user.username  
    first_name = message.from_user.first_name  # Get first_name
    last_name = message.from_user.last_name  # Get last_name

    profile_photo = get_user_photo_url(tg_id)
    
    profile_photo_encoded = urllib.parse.quote(profile_photo or '')
    web_app_url = f"{web_url}/?tg_id={tg_id}&username={username}&first_name={first_name}&last_name={last_name}&profile_photo={profile_photo_encoded}"

    web_app_button = InlineKeyboardButton(
        text="Web App ni ochish",
        url=web_app_url
    )

    keyboard = InlineKeyboardMarkup()
    keyboard.add(web_app_button)

    bot.send_message(
        message.chat.id,
        f"Assalomu alaykum, {message.from_user.first_name}! Botga xush kelibsiz.\n"
        f"Web App yoki bot orqali e'lon berish uchun tugmalardan birini tanlang:",
        reply_markup=keyboard
    )

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        bot.polling()
    except Exception as e:
        logging.error(f"Xatolik yuz berdi: {e}")
