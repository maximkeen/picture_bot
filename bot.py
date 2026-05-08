import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from aiogram.filters import Command

# ---------- НАСТРОЙКИ ----------
BOT_TOKEN = "8251156548:AAGmv0IZ-JdihBS9E0I0ERKsoXG-UFHY-b4"
TARGET_CHAT_ID = 1859354654            
                # ID человека, получающего все фото

# ---------- ИНИЦИАЛИЗАЦИЯ ----------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------- КЛАВИАТУРА «Отправить ещё фото» ----------
def get_another_photo_keyboard():
    button = InlineKeyboardButton(
        text="📤 Отправить ещё фото",
        callback_data="send_another"
    )
    return InlineKeyboardMarkup(inline_keyboard=[[button]])

# ---------- ОБРАБОТЧИК ФОТО (главное изменение здесь) ----------
@dp.message(F.photo)
async def handle_photo(message: Message):
    # Берём самое большое фото (последний элемент в списке)
    photo = message.photo[-1]

    # Получаем текст, который написал отправитель (может быть пустым)
    sender_caption = message.caption

    # Формируем подпись для получателя
    sender_info = f"📎 От @{message.from_user.username} ({message.from_user.full_name})"
    if sender_caption:
        # Если пользователь добавил описание – отправляем его вместе с информацией об отправителе
        final_caption = f"{sender_info}:\n{sender_caption}"
    else:
        # Если описание не добавлено – просто стандартная подпись
        final_caption = sender_info

    # Пересылаем фото получателю
    try:
        await bot.send_photo(
            TARGET_CHAT_ID,
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

# ---------- НАЖАТИЕ КНОПКИ «Отправить ещё» ----------
@dp.callback_query(F.data == "send_another")
async def ask_for_another_photo(callback: CallbackQuery):
    await callback.message.edit_text(
        "📷 Жду вашу следующую фотографию! Просто отправьте её сюда.\n"
        "Хотите добавить описание? Напишите текст прямо при отправке фото.",
        reply_markup=None
    )
    await callback.answer()

# ---------- КОМАНДА /start ----------
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Отправь мне фотографию – и я перешлю её владельцу.\n\n"
        "📝 Чтобы добавить описание или пожелание, просто напиши текст прямо при отправке фото.\n"
        "После каждой отправки появится кнопка для следующего снимка.",
        reply_markup=get_another_photo_keyboard()
    )

# ---------- ЗАПУСК ----------
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())