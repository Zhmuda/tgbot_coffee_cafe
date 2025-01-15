from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

coffee_positions = [
    {"name": "Эспрессо", "id": 1},
    {"name": "Капучино", "id": 2},
    {"name": "Латте", "id": 3},
    {"name": "Американо", "id": 4},
    {"name": "Мокка", "id": 5}
]


def get_start_order_button():
    web_app_button = InlineKeyboardButton(
        text="Перейти к заказу",
        callback_data='start_order_button'
    )
    keyboard = InlineKeyboardMarkup().add(web_app_button)
    return keyboard


def get_coffee_position_button():
    keyboard = InlineKeyboardMarkup(row_width=1)

    for coffee in coffee_positions:
        keyboard.add(InlineKeyboardButton(f'{coffee["name"]}☕', callback_data=f"position_{coffee['id']}"))

    keyboard.insert(InlineKeyboardButton(
        text="Далее",
        callback_data='order_confirmation_button'
    ))
    return keyboard


def get_location_button():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_geo = KeyboardButton(text="📍 Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    return keyboard


def get_confirm_location_button(cafe_id):
    button = InlineKeyboardButton(
        text="Заберу отсюда",
        callback_data=f'confirm_location_button_{cafe_id}'
    )
    keyboard = InlineKeyboardMarkup().add(button)
    return keyboard


def get_payment_method_buttons():
    button_card = InlineKeyboardButton(text="Оплатить картой", callback_data="payment_method_card")
    button_wallet = InlineKeyboardButton(text="Оплатить кошельком", callback_data="payment_method_wallet")

    keyboard = InlineKeyboardMarkup(row_width=1).add(button_card, button_wallet)
    return keyboard


def get_repeat_pay_button(order_id):
    button_retry_payment = InlineKeyboardButton(text="Оплатить снова",
                                                callback_data=f"pay_button_{order_id}")
    keyboard = InlineKeyboardMarkup(row_width=1).add(button_retry_payment)
    return keyboard


def get_exec_order_button(order_id):
    button = InlineKeyboardButton("Начать выполнение заказа", callback_data=f"exec_button_{order_id}")
    keyboard = InlineKeyboardMarkup(row_width=1).add(button)
    return keyboard


def get_wallet_payment_buttons(total_price, order_id):
    button_wallet = InlineKeyboardButton(text=f"Оплатить со скидкой {int(total_price * 0.95)}",
                                         callback_data=f"pay_button_{order_id}")

    keyboard = InlineKeyboardMarkup(row_width=1).add(button_wallet)
    return keyboard


# def get_create_size_buttons(coffee_id):
#     sizes = [200, 400, 500]
#     buttons = [
#         InlineKeyboardButton(text=f"{size} мл", callback_data=f"size_{coffee_id}_{size}")
#         for size in sizes
#     ]
#     keyboard = InlineKeyboardMarkup(row_width=3).add(*buttons)
#     return keyboard

def get_create_size_button(variants):
    buttons = [
        InlineKeyboardButton(
            text=f"{variant.weight} - {variant.cost}₽",
            callback_data=f"size_{variant.menu_item_id}_{variant.weight}"
        )
        for variant in variants
    ]
    keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
    return keyboard


def get_create_quantity_buttons(coffee_id, size):
    buttons = [
        InlineKeyboardButton(text=f"1", callback_data=f"quantity_{coffee_id}_{size}_1"),
        InlineKeyboardButton(text=f"2", callback_data=f"quantity_{coffee_id}_{size}_2"),
        InlineKeyboardButton(text=f"3", callback_data=f"quantity_{coffee_id}_{size}_3"),
        InlineKeyboardButton(text=f"4", callback_data=f"quantity_{coffee_id}_{size}_4"),
        InlineKeyboardButton(text=f"5", callback_data=f"quantity_{coffee_id}_{size}_5")
    ]
    keyboard = InlineKeyboardMarkup(row_width=3).add(*buttons)
    return keyboard


def get_order_confirm_button():
    button = InlineKeyboardButton(
        text="Подтвердить",
        callback_data='order_confirm_button'
    )
    keyboard = InlineKeyboardMarkup().add(button)
    return keyboard


def get_loyalty_confirm_button():
    button = InlineKeyboardButton(
        text="Подтвердить",
        callback_data='loyalty_confirm_button'
    )
    keyboard = InlineKeyboardMarkup().add(button)
    return keyboard


def get_pay_balance_button():
    button = InlineKeyboardButton(
        text="Пополнить баланс",
        callback_data='pay_balance_button'
    )
    keyboard = InlineKeyboardMarkup().add(button)
    return keyboard
