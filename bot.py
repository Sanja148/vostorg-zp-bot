import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv
import os
from datetime import date, timedelta
import calendar

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Клавиатура для выбора года
year_kb = ReplyKeyboardMarkup(resize_keyboard=True)
year_kb.add(KeyboardButton("2025"), KeyboardButton("2026"), KeyboardButton("2027"))

# Клавиатура для выбора месяца
month_kb = ReplyKeyboardMarkup(resize_keyboard=True)
months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
          "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
for month in months:
    month_kb.add(KeyboardButton(month))

# Клавиатура для старта заново
start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(KeyboardButton("Заново"))

user_data = {}

@dp.message_handler(commands=["start"])
async def start_handler(message: Message):
    await message.answer("Выберите год:", reply_markup=year_kb)

@dp.message_handler(lambda message: message.text in ["2025", "2026", "2027"])
async def year_handler(message: Message):
    user_data[message.from_user.id] = {"year": int(message.text)}
    await message.answer("Выберите месяц:", reply_markup=month_kb)

@dp.message_handler(lambda message: message.text in months)
async def month_handler(message: Message):
    user_data[message.from_user.id]["month"] = message.text
    # Убираем клавиатуру после выбора месяца
    await message.answer("Введите вашу ставку (например: 11000):", reply_markup_
