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
    await message.answer("Введите вашу ставку (например: 11000):", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(lambda message: message.text.isdigit())
async def handle_rate_input(message: Message):
    user_id = message.from_user.id
    data = user_data.get(user_id, {})

    if "rate" not in data:
        try:
            rate = int(message.text)
            data["rate"] = rate
            user_data[user_id] = data
            await message.answer("Введите количество отработанных часов (например: 140):")
        except ValueError:
            await message.answer("Пожалуйста, введите корректную числовую ставку.")
    else:
        await handle_worked_hours_input(message)

@dp.message_handler(lambda message: message.text.isdigit())
async def handle_worked_hours_input(message: Message):
    user_id = message.from_user.id
    data = user_data.get(user_id, {})

    if "worked_hours" not in data:
        try:
            worked_hours = int(message.text)
            if worked_hours < 0:
                raise ValueError("Количество часов не может быть отрицательным.")
            data["worked_hours"] = worked_hours
            user_data[user_id] = data

            # Выполнение расчета
            year = data["year"]
            month_name = data["month"]
            rate = data["rate"]
            worked_hours = data["worked_hours"]

            month_number = months.index(month_name) + 1
            weekdays = count_weekdays(year, month_number)
            hourly_rate = (rate / weekdays) / 8
            total_salary = hourly_rate * worked_hours

            result = f"Ставка в час = {hourly_rate:.2f}\nЗП за отработанное время = {total_salary:.2f} грн"

            await message.answer(result, reply_markup=start_kb)

            # Очистка данных пользователя после расчета
            del user_data[user_id]

        except ValueError:
            await message.answer("Пожалуйста, введите корректное число для количества отработанных часов.")
        
@dp.message_handler(lambda message: message.text == "Заново")
async def restart_handler(message: Message):
    # Очистка данных пользователя для начала нового расчета
    if message.from_user.id in user_data:
        del user_data[message.from_user.id]
    # Отправляем сообщение с запросом выбрать год снова
    await message.answer("Выберите год:", reply_markup=year_kb)

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
