import sys
import os

# Путь до твоей папки с ботом
path = '/home/FenixAG/VostorgZP_bot'
if path not in sys.path:
    sys.path.insert(0, path)

# Загружаем переменные из .env
from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

# Запускаем бота
from bot import start_bot
application = start_bot()