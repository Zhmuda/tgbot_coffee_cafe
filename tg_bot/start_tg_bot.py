from aiogram import executor
from tg_bot.create_bot import dp
from tg_bot.handlers import client_handlers, admin_handlers

client_handlers.register_handlers(dp)
admin_handlers.register_admin_handlers(dp)


async def on_startup(dp):
    print("Бот запущен")


def start_bot():
    executor.start_polling(dp, on_startup=on_startup)


if __name__ == "__main__":
    start_bot()

