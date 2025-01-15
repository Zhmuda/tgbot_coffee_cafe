import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

load_dotenv()

bot = Bot(os.getenv('BOT_TOKEN'))
Bot.set_current(bot)
dp = Dispatcher(bot)
