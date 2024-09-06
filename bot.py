API_TOKEN = '7189070743:AAEYh_q9VKtGwT9yVZEodB1hmQrkzGmbx9g'
import telebot
import requests

bot = telebot.TeleBot(API_TOKEN)

# Global variable to store user data
user_data = {}

# Start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    telegram_id = message.from_user.id

    # Check if the user is already registered
    response = requests.get(f'https://uzum-production.up.railway.app/api/check_user/{telegram_id}/')

    if response.status_code == 200 and response.json().get('registered'):
        # Check payment status
        payment_status_response = requests.get(f'https://uzum-production.up.railway.app/api/check_payment/{telegram_id}/')
        payment_status = payment_status_response.json().get('payment_made', False)

        if payment_status:
            bot.send_message(message.chat.id, "Assalom!\nSiz ro'yxatdan o'tgansiz va to'lov qilgansiz.")
        else:
            bot.send_message(message.chat.id, "Siz to'lov qilmagansiz. To'lovni amalga oshirishingiz kerak.", reply_markup=payment_button())
    else:
        # If not registered, send registration prompt with photo and button
        with open('bot/a.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="Xush kelibsiz! Ro'yxatdan o'tish uchun tugmani bosing.", reply_markup=registration_button())

# Inline keyboard with registration button
def registration_button():
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton("Ro'yxatdan o'tish", callback_data='register')
    markup.add(btn)
    return markup

# Callback handler for registration button
@bot.callback_query_handler(func=lambda call: call.data == 'register')
def process_registration(call):
    bot.send_message(call.message.chat.id, "Ismingizni kiriting:")
    bot.register_next_step_handler(call.message, process_name_step)

def process_name_step(message):
    user_data['name'] = message.text
    bot.send_message(message.chat.id, "Familiyangizni kiriting:")
    bot.register_next_step_handler(message, process_lastname_step)

def process_lastname_step(message):
    user_data['lastname'] = message.text
    bot.send_message(message.chat.id, "Telefon raqamingizni kiriting:")
    bot.register_next_step_handler(message, process_phone_step)

def process_phone_step(message):
    user_data['phone'] = message.text
    user_data['telegram_id'] = message.from_user.id

    response = requests.post('https://uzum-production.up.railway.app/api/register/', json=user_data)

    if response.status_code == 201:
        bot.send_message(message.chat.id, "Ro'yxatdan o'tdingiz. Endi kurs uchun to'lov qiling.", reply_markup=payment_button())
    else:
        bot.send_message(message.chat.id, "Ro'yxatdan o'tishda xatolik yuz berdi.")

# Payment button
def payment_button():
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton("To'lov qilish", callback_data='payment')
    markup.add(btn)
    return markup

# Callback handler for payment button
@bot.callback_query_handler(func=lambda call: call.data == 'payment')
def process_payment(call):
    response = requests.get('https://uzum-production.up.railway.app/api/cards/')
    cards = response.json().get('cards', [])

    if cards:
        markup = telebot.types.InlineKeyboardMarkup()
        for card in cards:
            card_name = card['card_name']
            markup.add(telebot.types.InlineKeyboardButton(card_name, callback_data=f'card_{card_name}'))
        
        bot.send_message(call.message.chat.id, "Quyidagi kartalardan birini tanlang:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "To'lov uchun hech qanday karta mavjud emas.")

# Handle card selection
@bot.callback_query_handler(func=lambda call: call.data.startswith('card_'))
def handle_card_selection(call):
    selected_card_name = call.data.split('_')[1]

    response = requests.get('https://uzum-production.up.railway.app/api/cards/')
    cards = response.json().get('cards', [])

    for card in cards:
        if card['card_name'] == selected_card_name:
            card_user = card['card_user']
            card_number = card['card_number']

            bot.send_message(call.message.chat.id, f"Karta ma'lumotlari:\n"
                                                   f"Karta nomi: {selected_card_name}\n"
                                                   f"Foydalanuvchi: {card_user}\n"
                                                   f"Karta raqami: {card_number}")

            # Store selected card in user_data
            user_data['selected_card'] = selected_card_name

            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("To'lovni amalga oshirish", callback_data='enter_payment_description'))
            bot.send_message(call.message.chat.id, "To'lovni amalga oshirish uchun quyidagi tugmani bosing:", reply_markup=markup)
            break

# Handle payment description input
@bot.callback_query_handler(func=lambda call: call.data == 'enter_payment_description')
def enter_payment_description(call):
    bot.send_message(call.message.chat.id, "To'lov izohini kiriting:")
    bot.register_next_step_handler(call.message, process_payment_description)

def process_payment_description(message):
    user_data['payment_description'] = message.text
    bot.send_message(message.chat.id, "To'lov chekini yuklang:")
    bot.register_next_step_handler(message, process_payment_receipt)

# Handle payment receipt input
def process_payment_receipt(message):
    chat_id = message.chat.id
    telegram_id = message.from_user.id

    if message.content_type == 'photo':
        receipt_image = message.photo[-1].file_id

        # Download the image
        file_info = bot.get_file(receipt_image)
        downloaded_file = bot.download_file(file_info.file_path)

        # Save the image
        with open(f'receipts/{telegram_id}.jpg', 'wb') as new_file:
            new_file.write(downloaded_file)

        # Send the payment data to Django API
        files = {'receipt_image': open(f'receipts/{telegram_id}.jpg', 'rb')}
        data = {
            'payment_description': user_data.get('payment_description', 'No description')
        }

        # Make the request to the Django API
        response = requests.post(f'https://uzum-production.up.railway.app/api/payment/{telegram_id}/', data=data, files=files)

        if response.status_code == 201:
            bot.send_message(chat_id, "To'lov muvaffaqiyatli amalga oshirildi!\nTasdiqlanishini kuting ...")
        else:
            bot.send_message(chat_id, "To'lovni amalga oshirishda xatolik yuz berdi.")
    else:
        bot.send_message(chat_id, "Iltimos, to'lov chekini yuklang.")

bot.polling()
