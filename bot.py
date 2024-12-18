import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton,InputMediaPhoto,ReplyKeyboardRemove
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import requests

BOT_TOKEN = "7631105546:AAGszQFEoWOGX2mOOjd4LIsXL433MGLiLfc"
API_BASE_URL = "https://9b14-95-214-210-167.ngrok-free.app/api/" 

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Holatlar
class PostCreation(StatesGroup):
    category = State()
    model = State()
    year = State()
    price = State()
    image = State()
    location = State()
    post = State()


async def fetch_api(url, method="GET", data=None):
    try:
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                async with session.get(url) as response:
                    return await response.json() if response.status == 200 else None
            elif method == "POST":
                async with session.post(url, data=data) as response:
                    return await response.json() if response.status in [200, 201] else None
    except Exception as e:
        print(f"API bilan bog'liq xatolik: {e}")
        return None

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    telegram_id = message.from_user.id
    response = requests.get(f"{API_BASE_URL}users/?telegram_id={telegram_id}")
    if response.status_code == 200 and response.json():
        await message.answer("Botga xush kelibsiz")
    else:
        data = {
            "telegram_id": telegram_id,
            "first_name": message.from_user.first_name or "",
            "last_name": message.from_user.last_name or "",
            "username": message.from_user.username or "",
        }
        user_response = requests.post(f"{API_BASE_URL}users/", data=data)
        if user_response.status_code == 201:
            await message.answer("Botga xush kelibsiz")
        else:
            await message.answer(f"Ro'yxatdan o'tishda xatolik: {user_response.text}")

    # Inline keyboard for menu options
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("📜 E'lon berish", callback_data="start_posting"),
        InlineKeyboardButton("💳 Sotib olish", callback_data="start_buying")
    )

    await message.answer("E'lon joylashtirish yoki sotib olish uchun quyidagi tugmalardan birini tanlang:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "start_buying")
async def buying_handler(callback_query: types.CallbackQuery):
    """Handle the 'Sotib olish' option."""
    categories = await fetch_api(f"{API_BASE_URL}categories/")
    if categories:
        keyboard = InlineKeyboardMarkup()
        for category in categories:
            keyboard.add(InlineKeyboardButton(category['name'], callback_data=f"category_{category['id']}"))
        await bot.send_message(callback_query.from_user.id, "Kategoriya tanlang:", reply_markup=keyboard)
    else:
        await bot.send_message(callback_query.from_user.id, "Hozirda kategoriya mavjud emas.")


@dp.callback_query_handler(lambda c: c.data.startswith("category_"))
async def category_handler(callback_query: types.CallbackQuery):
    category_id = callback_query.data.split("_")[1]
    url = f"{API_BASE_URL}models/?category_id={category_id}"
    models = await fetch_api(url)
    if models:
        keyboard = InlineKeyboardMarkup()
        for model in models:
            keyboard.add(InlineKeyboardButton(model['name'], callback_data=f"model_{model['id']}"))
        await bot.send_message(callback_query.from_user.id, "Modelni tanlang:", reply_markup=keyboard)
    else:
        await bot.send_message(callback_query.from_user.id, "Bu kategoriya uchun model mavjud emas.")

@dp.callback_query_handler(lambda c: c.data.startswith("model_"))
async def model_handler(callback_query: types.CallbackQuery):
    model_id = callback_query.data.split("_")[1]
    url = f"{API_BASE_URL}posts/?model_id={model_id}"
    posts = await fetch_api(url)

    if posts:
        for post in posts:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("🗺 Locatsani olish", callback_data=f"location_{post['id']}"))

            # Ensure image is valid
            photo = post.get('image', "https://via.placeholder.com/300")  # Fallback to a placeholder

            try:
                await bot.send_photo(
                    callback_query.from_user.id,
                    photo=photo,
                    caption=f"{post['model']['name']}\nNarx: {post['price']}\nYil: {post['year']['year']}",
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"Error sending photo: {e}")
                await bot.send_message(callback_query.from_user.id, "Rasmni yuborishda xatolik yuz berdi.")
    else:
        await bot.send_message(callback_query.from_user.id, "Bu model uchun e'lonlar mavjud emas.")

@dp.callback_query_handler(lambda c: c.data.startswith("location_"))
async def location_handler(callback_query: types.CallbackQuery):
    post_id = callback_query.data.split("_")[1]
    url = f"{API_BASE_URL}posts/{post_id}/"
    post = await fetch_api(url)
    
    if post:
        # Extract location coordinates (latitude, longitude)
        location = post['location']
        latitude, longitude = map(float, location.split(","))
        
        # Send the location as a map
        await bot.send_location(callback_query.from_user.id, latitude, longitude)
    else:
        await bot.send_message(callback_query.from_user.id, "Locatsiyani olishda xatolik yuz berdi.")



####################Sotish olish uchun#####################

# Callback query handler for starting the post creation process
@dp.callback_query_handler(lambda c: c.data == "start_posting")
async def start_post_creation(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)  # Acknowledge the callback query

    # Fetch categories from the API
    response = requests.get(f"{API_BASE_URL}categories/")
    if response.status_code == 200:
        categories = response.json()
    else:
        await bot.send_message(callback_query.from_user.id, "Kategoriyalarni yuklashda xatolik yuz berdi.")
        return

    # Create an inline keyboard for categories
    keyboard = InlineKeyboardMarkup()
    for category in categories:
        keyboard.add(InlineKeyboardButton(category['name'], callback_data=f"category_{category['id']}"))

    await bot.send_message(callback_query.from_user.id, "Kategoriyani tanlang:", reply_markup=keyboard)

    # Set the FSM state
    await PostCreation.category.set()

# Kategoriya tanlash
@dp.callback_query_handler(lambda c: c.data.startswith('category_'), state=PostCreation.category)
async def choose_category(callback_query: types.CallbackQuery, state: FSMContext):
    category_id = callback_query.data.split('_')[1]
    categories = await fetch_api(f"{API_BASE_URL}categories/")
    category_name = next((cat['name'] for cat in categories if str(cat['id']) == category_id), "Noma'lum kategoriya")
    
    await state.update_data(category_id=category_id, category_name=category_name)

    models = await fetch_api(f"{API_BASE_URL}models/?category={category_id}")
    if not models:
        await bot.send_message(callback_query.from_user.id, "Model ma'lumotlarini yuklashda xatolik yuz berdi.")
        return

    keyboard = InlineKeyboardMarkup()
    for model in models:
        keyboard.add(InlineKeyboardButton(model['name'], callback_data=f"model_{model['id']}"))
    await bot.send_message(callback_query.from_user.id, "Modelni tanlang:", reply_markup=keyboard)
    await PostCreation.model.set()

# Model tanlash
@dp.callback_query_handler(lambda c: c.data.startswith('model_'), state=PostCreation.model)
async def choose_model(callback_query: types.CallbackQuery, state: FSMContext):
    model_id = callback_query.data.split('_')[1]
    models = await fetch_api(f"{API_BASE_URL}models/")
    model_name = next((model['name'] for model in models if str(model['id']) == model_id), "Noma'lum model")
    
    await state.update_data(model_id=model_id, model_name=model_name)

    years = await fetch_api(f"{API_BASE_URL}years/")
    if not years:
        await bot.send_message(callback_query.from_user.id, "Yillarni yuklashda xatolik yuz berdi.")
        return

    keyboard = InlineKeyboardMarkup()
    for year in years:
        keyboard.add(InlineKeyboardButton(year['year'], callback_data=f"year_{year['id']}"))
    await bot.send_message(callback_query.from_user.id, "Yilni tanlang:", reply_markup=keyboard)
    await PostCreation.year.set()

# Yil tanlash
@dp.callback_query_handler(lambda c: c.data.startswith('year_'), state=PostCreation.year)
async def choose_year(callback_query: types.CallbackQuery, state: FSMContext):
    year_id = callback_query.data.split('_')[1]
    years = await fetch_api(f"{API_BASE_URL}years/")
    year_name = next((year['year'] for year in years if str(year['id']) == year_id), "Noma'lum yil")
    
    await state.update_data(year_id=year_id, year_name=year_name)
    await bot.send_message(callback_query.from_user.id, "Narxni kiriting:")
    await PostCreation.price.set()

# Narxni kiritish
@dp.message_handler(state=PostCreation.price)
async def enter_price(message: types.Message, state: FSMContext):
    price = message.text
    await state.update_data(price=price)
    await message.answer("Rasmni yuboring:")
    await PostCreation.image.set()

# Rasmni yuklash
@dp.message_handler(content_types=['photo'], state=PostCreation.image)
async def upload_image(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    async with aiohttp.ClientSession() as session:
        async with session.get(photo_url) as response:
            if response.status != 200:
                await message.answer("Rasmni yuklab olishda xatolik yuz berdi.")
                return
            
            # Rasmdan olingan ma'lumotlarni saqlash
            photo_data = await response.read()

            # Faylni API'ga jo'natish uchun saqlash
            await state.update_data(image=photo_data)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
        KeyboardButton("📍 Joylashuvni yuborish", request_location=True)
    )
    await message.answer("Joylashuvni tanlang:", reply_markup=keyboard)

    await PostCreation.location.set()

# Location selection and displaying confirmation details
@dp.message_handler(content_types=['location'], state=PostCreation.location)
async def choose_location(message: types.Message, state: FSMContext):
    location = f"{message.location.latitude}, {message.location.longitude}"
    await state.update_data(location=location)

    data = await state.get_data()

    # Inline tugmalar yaratish
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_post"),
        InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_post")
    )

    # Foydalanuvchiga ma'lumotlarni yuborish
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=data.get("image"),
        caption=(f"Ma'lumotlaringiz:\n\n"
                 f"Kategoriya: {data.get('category_name')}\n"
                 f"Model: {data.get('model_name')}\n"
                 f"Yil: {data.get('year_name')}\n"
                 f"Narx: {data.get('price')}\n"
                 f"Joylashuv: {data.get('location')}\n\n"
                 "Tasdiqlash yoki bekor qilish uchun tugmani bosing."),
        reply_markup=keyboard
    )

    # Joylashuv tugmasini o‘chirish
    await bot.send_message(message.chat.id, "Joylashuv qabul qilindi.", reply_markup=ReplyKeyboardRemove())
# Confirm post handler
@dp.callback_query_handler(lambda c: c.data == "confirm_post", state=PostCreation.location)
async def confirm_post_callback(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()

        form_data = aiohttp.FormData()
        form_data.add_field('telegram_id', str(callback_query.from_user.id))
        form_data.add_field('model', str(data.get('model_id', '')))
        form_data.add_field('year', str(data.get('year_id', '')))
        form_data.add_field('price', str(data.get('price', '')))
        form_data.add_field('location', data.get('location', ''))
        form_data.add_field('image', data.get('image'), filename="image.jpg", content_type="image/jpeg")

        api_url = f"{API_BASE_URL}posts/"
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, data=form_data) as response:
                if response.status == 201:
                    await bot.send_message(callback_query.from_user.id, "E'loningiz muvaffaqiyatli saqlandi!")
                else:
                    error_msg = await response.text()
                    await bot.send_message(callback_query.from_user.id, f"Xatolik yuz berdi: {error_msg}")

    except Exception as e:
        await bot.send_message(callback_query.from_user.id, f"Xatolik yuz berdi: {str(e)}")

    await state.finish()


# Cancel post handler
@dp.callback_query_handler(lambda c: c.data == "cancel_post", state=PostCreation.location)
async def cancel_post_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    # Xabarni o‘chirish
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, "E'lon berish jarayoni bekor qilindi.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
