import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from aiogram.filters import Command
from config import BOT_TOKEN, CHAT_ID       

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_another_photo_keyboard():
    button = InlineKeyboardButton(
        text="📤 Отправить ещё фото",
        callback_data="send_another"
    )
    return InlineKeyboardMarkup(inline_keyboard=[[button]])

@dp.message(F.photo)
async def handle_photo(message: Message):
    photo = message.photo[-1]

    sender_caption = message.caption

    sender_info = f"📎 От @{message.from_user.username} ({message.from_user.full_name})"
    if sender_caption:
        final_caption = f"{sender_info}:\n{sender_caption}"
    else:
        final_caption = sender_info

    try:
        await bot.send_photo(
            CHAT_ID,
            photo.file_id,
            caption=final_caption
        )
    except Exception as e:
        logging.error(f"Ошибка пересылки: {e}")
        await message.answer("❌ Не удалось доставить фото. Получатель, возможно, ещё не запустил бота.")
        return

    # Отвечаем отправителю
    await message.answer(
        "📸 Фото отправлено, спасибо!",
        reply_markup=get_another_photo_keyboard()
    )

@dp.callback_query(F.data == "send_another")
async def ask_for_another_photo(callback: CallbackQuery):
    await callback.message.edit_text(
        "📷 Жду вашу следующую фотографию! Просто отправьте её сюда.\n"
        "Хотите добавить описание? Напишите текст прямо при отправке фото.",
        reply_markup=None
    )
    await callback.answer()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Отправь мне фотографию – и я перешлю её владельцу.\n\n"
        "📝 Чтобы добавить описание или пожелание, просто напиши текст прямо при отправке фото.\n"
        "После каждой отправки появится кнопка для следующего снимка.",
        reply_markup=get_another_photo_keyboard()
    )

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
