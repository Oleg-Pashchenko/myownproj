import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
import os
import dotenv

import penzgtu_connector

dotenv.load_dotenv()
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=os.getenv('API_TOKEN'))
# Диспетчер
dp = Dispatcher()


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Посмотреть статистику"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True)
    await message.answer(
        "Чтобы посмотреть статистику по количеству нажмите на кнопку `Посмотреть статистику` и "
        "подождите примерно 2 минуты. Это время необходимо для сбора информации.",
        reply_markup=keyboard)


@dp.message(F.text.lower() == "посмотреть статистику")
async def with_puree(message: types.Message):
    await message.reply("Собираю информацию...")
    await message.reply(penzgtu_connector.get_stats())


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
