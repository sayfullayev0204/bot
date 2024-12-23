from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
import logging
import asyncio
import urllib
API_TOKEN = '6804578580:AAHJhUTXbOaajQjzURNnT_xXuQQV3smwKC8'
web_url = "https://cargobot-production.up.railway.app"



bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

data_storage = {}

async def get_user_photo_url(user_id: int) -> str:
    """Fetches the user's profile photo URL."""
    photos = await bot.get_user_profile_photos(user_id)
    if photos.total_count > 0:
        file_id = photos.photos[0][0].file_id
        file = await bot.get_file(file_id)
        photo_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file.file_path}"
        return photo_url
    return None

@router.message(Command(commands=["start"]))
async def send_welcome(message: Message):
    tg_id = message.from_user.id  
    username = message.from_user.username  
    first_name = message.from_user.first_name  # Get first_name
    last_name = message.from_user.last_name  # Get last_name

    profile_photo = await get_user_photo_url(tg_id)
    
    profile_photo_encoded = urllib.parse.quote(profile_photo or '')
    web_app_url = f"{web_url}/?tg_id={tg_id}&username={username}&first_name={first_name}&last_name={last_name}&profile_photo={profile_photo_encoded}"

    web_app_button = InlineKeyboardButton(
        text="Web App ni ochish",
        web_app={"url": f"{web_app_url}"}  # Replace with your actual Web App URL
    )


    keyboard = InlineKeyboardMarkup(inline_keyboard=[[web_app_button]])

    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}! Botga xush kelibsiz.\n"
        f"Web App yoki bot orqali e'lon berish uchun tugmalardan birini tanlang:",
        reply_markup=keyboard
    )

# @router.callback_query(lambda c: c.data == "start_ad")
# async def handle_start_ad(callback: CallbackQuery):
#     ad_type_buttons = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="Jo'natma ber yuboraman", callback_data="ad_type_1")],
#         [InlineKeyboardButton(text="Jo'natma olib ketaman", callback_data="ad_type_2")]
#     ])
#     await callback.message.edit_text("E'lon turini tanlang:", reply_markup=ad_type_buttons)

# @router.callback_query(lambda c: c.data.startswith("ad_type_"))
# async def handle_ad_type(callback: CallbackQuery):
#     user_id = callback.from_user.id
#     ad_type = callback.data.replace("ad_type_", "")  # ad_type_1 yoki ad_type_2 ni chiqaramiz

#     # Matnni saqlash
#     ad_type_text = "Jo'natma ber yuboraman" if ad_type == "1" else "Jo'natma olib ketaman"
#     data_storage[user_id] = {"type": ad_type, "type_text": ad_type_text}

#     ad_type_buttons = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="Yaponiyadan 🇯🇵  ➡️  O`zbekistonga  🇺🇿", callback_data="direction_1")],
#         [InlineKeyboardButton(text="O`zbekistonga  🇺🇿  ➡️  Yaponiyadan 🇯🇵", callback_data="direction_2")]
#     ])
#     await callback.message.edit_text("Yo'nalishni tanlang:", reply_markup=ad_type_buttons)

# @router.callback_query(lambda c: c.data.startswith("direction_"))
# async def handle_direction(callback: CallbackQuery):
#     user_id = callback.from_user.id
#     direction = callback.data.replace("direction_", "")

#     # Matnni saqlash
#     direction_text = "Yaponiyadan 🇯🇵  ➡️  O`zbekistonga  🇺🇿" if direction == "1" else "O`zbekistonga  🇺🇿  ➡️  Yaponiyadan 🇯🇵"
#     data_storage[user_id]["direction"] = direction
#     data_storage[user_id]["direction_text"] = direction_text

#     bag_buttons = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="Bagaj 1", callback_data="bag_1")],
#         [InlineKeyboardButton(text="Bagaj 2", callback_data="bag_2")]
#     ])
#     await callback.message.edit_text("Bagajni tanlang:", reply_markup=bag_buttons)

# @router.callback_query(lambda c: c.data.startswith("bag_"))
# async def handle_bag(callback: CallbackQuery):
#     user_id = callback.from_user.id
#     bag = callback.data.replace("bag_", "")

#     # Matnni saqlash
#     bag_text = "Bagaj 1" if bag == "1" else "Bagaj 2"
#     data_storage[user_id]["bag"] = bag
#     data_storage[user_id]["bag_text"] = bag_text

#     airport_buttons = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="Airport 1", callback_data="airport_1")],
#         [InlineKeyboardButton(text="Airport 2", callback_data="airport_2")]
#     ])
#     await callback.message.edit_text("Airportni tanlang:", reply_markup=airport_buttons)

# @router.callback_query(lambda c: c.data.startswith("airport_"))
# async def handle_airport(callback: CallbackQuery):
#     user_id = callback.from_user.id    
#     airport = callback.data.replace("airport_", "")
    
#     # Matnni saqlash
#     airport_text = "Airport 1" if airport == "1" else "Airport 2"
#     data_storage[user_id]["airport"] = airport
#     data_storage[user_id]["airport_text"] = airport_text

#     await callback.message.edit_text("Vaqtni kiriting (YYYY-MM-DD HH:MM):")

# @router.message()
# async def handle_text(message: Message):
#     user_id = message.from_user.id
#     if user_id not in data_storage or "airport" not in data_storage[user_id]:
#         await message.answer("")
#         return

#     if "time" not in data_storage[user_id]:
#         data_storage[user_id]["time"] = message.text
#         await message.answer("Izohni kiriting:")
#     elif "description" not in data_storage[user_id]:
#         data_storage[user_id]["description"] = message.text
#         await message.answer("Kontaktni kiriting:")
#     elif "contact" not in data_storage[user_id]:
#         data_storage[user_id]["contact"] = message.text
#         await message.answer("Narxni kiriting:")
#     elif "price" not in data_storage[user_id]:
#         data_storage[user_id]["price"] = message.text

#         ad = data_storage[user_id]
#         ad_message = (
#             f"📢 Yangi e'lon\n\n"
#             f"📌 E'lon turi: {ad['type_text']}\n"
#             f"🌍 Yo'nalish: {ad['direction_text']}\n"
#             f"🎒 Bagaj: {ad['bag_text']}\n"
#             f"✈️ Airport: {ad['airport_text']}\n"
#             f"🕒 Vaqt: {ad['time']}\n"
#             f"📝 Izoh: {ad['description']}\n"
#             f"📞 Kontakt: {ad['contact']}\n"
#             f"💵 Narx: {ad['price']}"
#         )
#         confirm_buttons = InlineKeyboardMarkup(inline_keyboard=[
#             [InlineKeyboardButton(text="Tasdiqlash", callback_data="confirm_ad")],
#             [InlineKeyboardButton(text="Bekor qilish", callback_data="cancel_ad")]
#         ])
#         await message.answer(ad_message, reply_markup=confirm_buttons)

# @router.callback_query(lambda c: c.data == "confirm_ad")
# async def handle_confirm_ad(callback: CallbackQuery):
#     user_id = callback.from_user.id
#     if user_id in data_storage:
#         ad = data_storage[user_id]
#         username = callback.from_user.username
#         username_text = f"@{username}" if username else "Username mavjud emas"
        
#         group_id = -1002119597681  # Replace with your group ID
#         ad_message = (
#             f"📢 Yangi e'lon\n\n"
#             f"📌 E'lon turi: {ad['type_text']}\n"
#             f"🌍 Yo'nalish: {ad['direction_text']}\n"
#             f"🎒 Bagaj: {ad['bag_text']}\n"
#             f"✈️ Airport: {ad['airport_text']}\n"
#             f"🕒 Vaqt: {ad['time']}\n"
#             f"📝 Izoh: {ad['description']}\n"
#             f"📞 Kontakt: {ad['contact']}\n"
#             f"💵 Narx: {ad['price']}\n"
#             f"👤 Foydalanuvchi: {username_text}\n\n\n\n"
#             "🔗 Guruhga qo'shilish 'guruhnomi'\n"
#             "📲 E'lon berish 'bot nomi'"
#         )
#         await bot.send_message(group_id, ad_message)
#         await callback.message.edit_text("E'lon tasdiqlandi va guruhga yuborildi!")
#         del data_storage[user_id]

# @router.callback_query(lambda c: c.data == "cancel_ad")
# async def handle_cancel_ad(callback: CallbackQuery):
#     user_id = callback.from_user.id
#     if user_id in data_storage:
#         del data_storage[user_id]
#     await callback.message.edit_text("E'lon bekor qilindi.")

async def main():
    try:
        dp.include_router(router)
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Xatolik yuz berdi: {e}")

if __name__ == '__main__':
    asyncio.run(main())
