import logging

import aiogram
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Dispatcher
from database.database import update_order, get_user, get_user_byId, get_order_byId
from tg_bot.create_bot import bot
from tg_bot.logger.logger import print_error_double_click


async def process_exec_order(callback_query: types.CallbackQuery):
    order_id = callback_query.data.split("_")[-1]
    admin_id = str(callback_query.from_user.id)
    user_id = str(callback_query.from_user.id)

    try:
        admin = get_user(admin_id)
        if admin.role != 'admin':
            try:
                await bot.delete_message(user_id, callback_query.message.message_id)
            except aiogram.exceptions.MessageToDeleteNotFound:
                print_error_double_click(callback_query.from_user.id)
            await bot.answer_callback_query(callback_query.id, "У вас нет прав для выполнения этой операции.")
            return

        update_order(order_id, {'status': "Cook"})
        await bot.edit_message_text(
            chat_id=admin_id,
            message_id=callback_query.message.message_id,
            text="Юхуууу, ну как, заказ готов?",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("Уведомить о готовности заказа", callback_data=f"complete_order_{order_id}")
            )
        )
        order = get_order_byId(order_id)
        user = get_user_byId(order.user_id)
        await bot.send_message(
            user.tg_user_id,
            f"Ваш заказ №{order_id} готовится! \n\n"
            f"Адрес самовывоза: {order.pickup_location}\n\n"
        )

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


async def process_complete_order(callback_query: types.CallbackQuery):
    order_id = int(callback_query.data.split('_')[2])
    try:
        update_order(order_id, {'status': 'Completed'})

        await callback_query.message.edit_text(
            f"Заказ №{order_id} завершен"
        )

        order = get_order_byId(order_id)
        user = get_user_byId(order.user_id)
        await bot.send_message(
            user.tg_user_id,
            f"Ваш заказ №{order_id} готов! \n\n"
            f"Адрес самовывоза: {order.pickup_location}\n\n"
            f"Спасибо, что выбрали наше кафе!"
        )

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


def register_admin_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(process_exec_order, lambda c: c.data.startswith("exec_button_"))
    dp.register_callback_query_handler(process_complete_order, lambda c: c.data.startswith("complete_order_"))
