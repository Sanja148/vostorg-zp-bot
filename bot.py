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
start_kb.add(KeyboardButton("/start"))


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
    await message.answer("Введите вашу ставку (например: 20000):")

@dp.message_handler(lambda message: message.text.isdigit())
async def handle_input(message: Message):
    user_id = message.from_user.id
    data = user_data.get(user_id, {})

    if "rate" not in data:
        data["rate"] = int(message.text)
        user_data[user_id] = data
        await message.answer("Введите количество отработанных часов (например: 140):")
    else:
        worked_hours = int(message.text)
        year = data["year"]
        month_name = data["month"]
        rate = data["rate"]

        month_number = months.index(month_name) + 1
        weekdays = count_weekdays(year, month_number)
        hourly_rate = (rate / weekdays) / 8
        total_salary = hourly_rate * worked_hours

        result = f"Ставка в час = {hourly_rate:.2f}\nЗП за отработанное время = {total_salary:.2f} грн"

        await message.answer(result, reply_markup=start_kb)

def count_weekdays(year, month):
    days_in_month = calendar.monthrange(year, month)[1]
    weekdays = 0
    for day in range(1, days_in_month + 1):
        current_day = date(year, month, day)
        if current_day.weekday() < 5:
            weekdays += 1
    return weekdays

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
