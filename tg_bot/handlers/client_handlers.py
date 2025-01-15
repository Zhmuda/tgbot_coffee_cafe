import logging
import os

import aiogram
from aiogram import Dispatcher, types
from aiogram.types import ContentType
from database.database import get_user, post_user, update_user, get_user_state, post_item_in_order, \
    get_unfinished_order, get_order_items, get_menu_item, update_order, get_payment_order, get_orders, get_locations, \
    get_cafe_address_by_id, get_order_byId, delete_orders, get_users_by_role, get_coffee_variants, get_variant_for_item
from tg_bot import elements
from tg_bot.create_bot import bot
from tg_bot.logger.logger import print_error_double_click


async def process_start(message: types.Message):
    user_id = str(message.from_user.id)

    try:
        user = get_user(user_id)
        if not user:
            post_user(user_id)

        delete_orders(user_id, ['in_progress', 'during_payment'])

        await bot.send_photo(chat_id=user_id,
                             photo=open(
                                 r'C:\Users\danii\PycharmProjects\TelegramBotCoffeeHouse\меню.jpeg', 'rb')
                             )

        await bot.send_message(
            chat_id=user_id,
            text="Выберите кофе для заказа:",
            reply_markup=elements.get_coffee_position_button()
        )
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


async def process_position(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    coffee_id = callback_query.data.split('_')[1]

    try:
        variants = get_coffee_variants(coffee_id)

        if not variants:
            await bot.send_message(
                chat_id=user_id,
                text="Извините, для выбранного кофе нет доступных вариантов."
            )
            return

        await bot.edit_message_text(
            text=f"Выберите объем для {variants[0].menu_item.name}:",
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            reply_markup=elements.get_create_size_button(variants)
        )
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


async def process_size(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    coffee_id, size = callback_query.data.split('_')[1:3]

    try:
        await bot.edit_message_text(
            text=f"Выберите количество для {elements.coffee_positions[int(coffee_id) - 1]['name']} ({size}):",
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            reply_markup=elements.get_create_quantity_buttons(coffee_id, size)
        )
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


async def process_quantity(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    coffee_id, size, quantity = callback_query.data.split('_')[1:]

    try:
        quantity_numeric = int(''.join(filter(str.isdigit, quantity)))

        post_item_in_order(user_id, coffee_id, quantity_numeric, size)

        await bot.edit_message_text(
            text="Выберите кофе для заказа:",
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            reply_markup=elements.get_coffee_position_button()
        )

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


async def process_giving_location(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    try:
        try:
            await bot.delete_message(user_id, callback_query.message.message_id)
        except aiogram.exceptions.MessageToDeleteNotFound:
            print_error_double_click(callback_query.from_user.id)

        await bot.send_message(chat_id=user_id,
                               text="Поделитесь своим местоположением, "
                                    "чтобы мы могли найти ближайшую кофейню ☕.",
                               reply_markup=elements.get_location_button())
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


async def process_location(message: types.Message):
    if message.location:
        user_coordinates = (message.location.latitude, message.location.longitude)

        try:
            distances = get_locations(user_coordinates)

            nearest = min(distances, key=lambda x: x['distance'])

            await message.answer(
                f"Ближайшая кофейня находится здесь:\n\n"
                f"📍 Адрес: {nearest['address']}\n"
                f"🚶‍♂️ Расстояние: {nearest['distance']:.2f} м\n\n",
                reply_markup=elements.get_confirm_location_button(nearest['id'])
            )

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            await message.answer("Произошла ошибка при поиске ближайшей кофейни. Попробуйте позже.")


async def process_finish_order(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    cafe_id = callback_query.data.split("_")[-1]
    try:
        try:
            await bot.delete_message(user_id, callback_query.message.message_id)
        except aiogram.exceptions.MessageToDeleteNotFound:
            print_error_double_click(callback_query.from_user.id)

        order = get_unfinished_order(user_id)

        if order:
            order_items = get_order_items(order.id)

            cafe_address = get_cafe_address_by_id(cafe_id)
            update_order(order.id, {'pickup_location': cafe_address})

            order_details = f"Ваш заказ:\n\n"
            total_price = 0

            for item in order_items:
                menu_item = get_menu_item(item.menu_item_id)
                variant_item = get_variant_for_item(item.menu_item_id, item.size)
                item_total = variant_item.cost * item.quantity
                total_price += item_total
                order_details += f"{menu_item.name} - {item.quantity} шт. " \
                                 f"по {variant_item.cost} руб. = {item_total} руб.\n"

            update_order(order.id, {'total_price': total_price})

            order_details += f"\nОбщая сумма: {total_price} руб.\n"
            order_details += f"Адрес: {cafe_address}"

            await callback_query.message.answer(order_details, reply_markup=elements.get_order_confirm_button())

        else:
            await callback_query.message.answer("У вас нет незавершённых заказов.")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


async def process_send_way_payment(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    try:
        try:
            await bot.delete_message(user_id, callback_query.message.message_id)
        except aiogram.exceptions.MessageToDeleteNotFound:
            print_error_double_click(callback_query.from_user.id)

        await callback_query.message.answer(
            "Как вы хотите оплатить заказ?",
            reply_markup=elements.get_payment_method_buttons()
        )
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


async def process_order_confirm(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    payment_method = callback_query.data.split("_")[-1]

    try:
        try:
            await bot.delete_message(user_id, callback_query.message.message_id)
        except aiogram.exceptions.MessageToDeleteNotFound:
            print_error_double_click(callback_query.from_user.id)

        order = get_unfinished_order(user_id)

        if order:
            order_items = get_order_items(order.id)

            order_details = f"Ваш заказ:\n\n"
            total_price = 0

            for item in order_items:
                menu_item = get_menu_item(item.menu_item_id)
                variant_item = get_variant_for_item(item.menu_item_id, item.size)
                item_total = variant_item.cost * item.quantity
                total_price += item_total
                order_details += f"{menu_item.name} - {item.quantity} шт. " \
                                 f"по {variant_item.cost} руб. = {item_total} руб.\n"

            order_details += f"\nОбщая сумма: {total_price} руб."

            update_order(order.id, {'status': 'during_payment'})

            amount = total_price * 100

            if payment_method == "card":
                await bot.send_invoice(
                    chat_id=user_id,
                    title=f"Оплата заказа №{order.id}",
                    description=order_details,
                    payload="pay_order",
                    provider_token=os.getenv('YOOTOKEN'),
                    currency="RUB",
                    start_parameter="pay_order",
                    prices=[{"label": "Руб", "amount": amount}]
                )

            elif payment_method == "wallet":
                user = get_user(user_id)
                if user.loyalty_points:
                    await callback_query.message.answer(f"Вы выбрали оплату кошельком. "
                                                        f"Доступный баланс: {user.loyalty_points}",
                                                        reply_markup=elements.get_wallet_payment_buttons(total_price,
                                                                                                         order.id))
                else:
                    await callback_query.message.answer(
                        f"Вы не можете оплатить из-за отсутствия кошелька.\n\n"
                        "Пожалуйста, воспользуйтесь командой /wallet для создания и пополнения кошелька")

                    await callback_query.message.answer(
                        "Вы можете попробовать оплатить снова.\n\n"
                        f"К оплате: {int(total_price * 0.95)} рублей",
                        reply_markup=elements.get_repeat_pay_button(order.id)
                    )

        else:
            await callback_query.message.answer("У вас нет незавершённых заказов.")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


async def process_payment_using_wallet(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    order_id = int(callback_query.data.split("_")[-1])

    try:
        try:
            await bot.delete_message(user_id, callback_query.message.message_id)
        except aiogram.exceptions.MessageToDeleteNotFound:
            print_error_double_click(callback_query.from_user.id)

        order = get_order_byId(order_id)
        if order:
            user = get_user(user_id)

            discount_amount = int(order.total_price * 0.95)
            remaining_amount = user.loyalty_points - discount_amount

            if remaining_amount >= 0:

                update_user(user_id, {'loyalty_points': remaining_amount})

                update_order(order.id, {'status': "In processing"})
                await bot.send_message(user_id, f"Вы успешно оплатили заказ №{order.id} "
                                                f"на сумму с учетом персональной скидки "
                                                f"{int(order.total_price * 0.95)} рублей!\n\n"
                                                f"Текущий статус заказа: В обработке")

                await callback_query.message.answer(
                    f"Доступный баланс после оплаты: {remaining_amount} баллов.\n"
                    "Спасибо за ваш заказ!"
                )

                admins = get_users_by_role('admin')

                order_items = get_order_items(order.id)

                order_details = f"Состав заказа:\n\n"
                total_price = 0

                for item in order_items:
                    menu_item = get_menu_item(item.menu_item_id)
                    variant_item = get_variant_for_item(item.menu_item_id, item.size)
                    item_total = variant_item.cost * item.quantity
                    total_price += item_total
                    order_details += f"{menu_item.name} - {item.quantity} шт. " \
                                     f"по {variant_item.cost} руб. = {item_total} руб.\n"

                order_details += f"\nОбщая сумма: {total_price} руб."

                for admin in admins:
                    await bot.send_message(admin.tg_user_id, f"НОВЫЙ ЗАКАЗ №{order.id}\n\n"
                                                             f"{order_details}",
                                           reply_markup=elements.get_exec_order_button(order.id))

            else:
                await callback_query.message.answer(
                    f"У вас недостаточно средств на кошельке.\n\n"
                    f"Доступный баланс: {user.loyalty_points} баллов.\n"
                    "Пожалуйста, пополните кошелек с помощью команды /wallet или выберите другой способ оплаты."
                )

                await callback_query.message.answer(
                    "Вы можете попробовать оплатить снова.",
                    reply_markup=elements.get_repeat_pay_button(order.id)
                )

        else:
            await callback_query.message.answer("Заказ не найден или уже завершен.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        await callback_query.message.answer("Произошла ошибка при обработке вашего платежа. Попробуйте снова.")


async def process_getting_orders(message: types.Message):
    user_id = str(message.from_user.id)

    try:
        orders = get_orders(user_id)

        if not orders:
            await message.answer("У вас нет оплаченных заказов.")
        else:
            order_details = "Ваши оплаченные заказы:\n\n"
            for order in orders:
                if order.status == 'In processing':
                    order_details += f"Заказ #{order.id} - Статус: В обработке\n"
                elif order.status == 'Cook':
                    order_details += f"Заказ #{order.id} - Статус: Готовится\n"
                elif order.status == 'Completed':
                    order_details += f"Заказ #{order.id} - Статус: Выполнен\n"

            await message.answer(order_details)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


async def process_wallet(message: types.Message):
    user_id = str(message.from_user.id)
    try:
        user = get_user(user_id)
        if user.loyalty_points is None:
            await bot.send_message(
                chat_id=user_id,
                text="У вас не создан кошелек!\n\n"
                     "Если хотите вступить в ряды кофеманов нажмите 'Создать' ☕",
                reply_markup=elements.get_loyalty_confirm_button()
            )
        else:
            await bot.send_message(
                chat_id=user_id,
                text="Добро пожаловать в кошелек Coffee House! ☕\n\n"
                     "С помощью кошелька вы можете пополнить баланс и использовать его для оплаты заказов "
                     "в нашем кафе. "
                     "При оплате с использованием кошелька вы получите скидку 5% на общую сумму заказа. 🎉\n\n"
                     "Пополните баланс прямо сейчас и наслаждайтесь выгодными покупками!",
                reply_markup=elements.get_pay_balance_button()
            )
            await bot.send_message(
                chat_id=user_id,
                text=f"Ваш текущий баланс: {user.loyalty_points} рублей 😄",
            )

    except Exception as e:

        logging.error(f"An error occurred: {str(e)}")


async def process_create_wallet(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)

    try:
        try:
            await bot.delete_message(user_id, callback_query.message.message_id)
        except aiogram.exceptions.MessageToDeleteNotFound:
            print_error_double_click(callback_query.from_user.id)

        update_user(user_id, {'loyalty_points': 0})

        await bot.send_message(
            chat_id=user_id,
            text="Добро пожаловать в кошелек Coffee House! ☕\n\n"
                 "С помощью кошелька вы можете пополнить баланс и использовать его для оплаты заказов в нашем кафе. "
                 "При оплате с использованием кошелька вы получите скидку 5% на общую сумму заказа. 🎉\n\n"
                 "Пополните баланс прямо сейчас и наслаждайтесь выгодными покупками!",
            reply_markup=elements.get_pay_balance_button()
        )
    except Exception as e:

        logging.error(f"An error occurred: {str(e)}")


async def process_choose_money(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)

    try:
        try:
            await bot.delete_message(user_id, callback_query.message.message_id)
        except aiogram.exceptions.MessageToDeleteNotFound:
            print_error_double_click(callback_query.from_user.id)

        update_user(user_id, {'state': 'choose_money'})

        await bot.send_message(
            chat_id=user_id,
            text="Введите сумму пополнения кошелька.",
        )
    except Exception as e:

        logging.error(f"An error occurred: {str(e)}")


async def process_check_money_for_pay_balance(message: types.Message):
    user_id = str(message.from_user.id)

    try:

        if message.text.isdigit():
            amount = int(message.text) * 100
            await bot.send_invoice(
                chat_id=user_id,
                title="Пополнение баланса",
                description=f"Пополнение баланса на сумму {message.text}",
                payload="pay_balance",
                provider_token=os.getenv('YOOTOKEN'),
                currency="RUB",
                start_parameter="pay_balance",
                prices=[{"label": "Руб", "amount": amount}]
            )

            update_user(user_id, {'state': 'pay_money'})

        else:
            await bot.send_message(
                chat_id=user_id,
                text="Пожалуйста, введите корректное число для пополнения баланса.",
            )
    except Exception as e:

        logging.error(f"An error occurred: {str(e)}")


async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    try:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


# Где вам нужно отправить сообщение админу о поступлении нового заказа
async def process_successful_pay(message: types.Message):
    user_id = str(message.from_user.id)

    try:

        if message.successful_payment.invoice_payload == 'pay_balance':
            sum_balance = message.successful_payment.total_amount // 100
            user = get_user(user_id)
            final_balance = user.loyalty_points + sum_balance
            update_user(user_id, {'state': 'Default', 'loyalty_points': final_balance})
            await bot.send_message(user_id, f"Вы успешно пополнили баланс на сумму "
                                            f"{sum_balance} рублей!\n\n"
                                            f"Воспользуйтесь командой /wallet, чтобы посмотреть Ваш текущий баланс!")

        elif message.successful_payment.invoice_payload == 'pay_order':
            sum_balance = message.successful_payment.total_amount // 100
            order = get_payment_order(user_id)
            update_order(order.id, {'status': "In processing"})
            await bot.send_message(user_id, f"Вы успешно оплатили заказ №{order.id} на сумму "
                                            f"{sum_balance} рублей!\n\n"
                                            f"Текущий статус заказа: В обработке")

            admins = get_users_by_role('admin')

            order_items = get_order_items(order.id)

            order_details = f"Состав заказа:\n\n"
            total_price = 0

            for item in order_items:
                menu_item = get_menu_item(item.menu_item_id)
                variant_item = get_variant_for_item(item.menu_item_id, item.size)
                item_total = variant_item.cost * item.quantity
                total_price += item_total
                order_details += f"{menu_item.name} - {item.quantity} шт. " \
                                 f"по {variant_item.cost} руб. = {item_total} руб.\n"

            order_details += f"\nОбщая сумма: {total_price} руб."

            for admin in admins:
                await bot.send_message(admin.tg_user_id, f"НОВЫЙ ЗАКАЗ №{order.id}\n\n"
                                                         f"{order_details}",
                                       reply_markup=elements.get_exec_order_button(order.id))

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(process_start, commands=['start'])
    dp.register_message_handler(process_wallet, commands=['wallet'])
    dp.register_message_handler(process_getting_orders, commands=['order_status'])
    dp.register_callback_query_handler(process_position, lambda c: c.data.startswith("position_"))
    dp.register_callback_query_handler(process_size, lambda c: c.data.startswith("size_"))
    dp.register_callback_query_handler(process_quantity, lambda c: c.data.startswith("quantity_"))
    dp.register_callback_query_handler(process_giving_location, lambda c: c.data.startswith("order_confirmation_"))
    dp.register_message_handler(process_location, content_types=["location"])
    dp.register_callback_query_handler(process_finish_order, lambda c: c.data.startswith("confirm_location_"))
    dp.register_callback_query_handler(process_send_way_payment, lambda c: c.data.startswith("order_confirm_"))
    dp.register_callback_query_handler(process_order_confirm, lambda c: c.data.startswith("payment_method_"))
    dp.register_callback_query_handler(process_payment_using_wallet, lambda c: c.data.startswith("pay_button_"))
    dp.register_callback_query_handler(process_create_wallet, lambda c: c.data.startswith('loyalty_confirm_'))
    dp.register_callback_query_handler(process_choose_money, lambda c: c.data.startswith('pay_balance_'))
    dp.register_message_handler(process_check_money_for_pay_balance,
                                lambda message: get_user_state(message.from_user.id) == 'choose_money')
    dp.register_pre_checkout_query_handler(process_pre_checkout_query)
    dp.register_message_handler(process_successful_pay, content_types=ContentType.SUCCESSFUL_PAYMENT)
