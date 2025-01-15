import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from geopy.distance import geodesic

from database.models import Base, User, Order, OrderItem, MenuItem, CoffeeHouse, Variant

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def get_user(user_id):
    session = Session()
    user = session.query(User).filter_by(tg_user_id=user_id).first()
    session.close()
    return user


def get_user_byId(user_id):
    session = Session()
    user = session.query(User).filter_by(id=str(user_id)).first()
    session.close()
    return user


def get_user_state(user_id):
    session = Session()
    user = session.query(User).filter_by(tg_user_id=str(user_id)).first()
    session.close()
    return user.state


def get_users_by_role(role):
    session = Session()
    user = session.query(User).filter(User.role == str(role)).all()
    session.close()
    return user


def post_user(user_id):
    session = Session()
    user = User(tg_user_id=user_id)
    session.add(user)
    session.commit()
    session.close()


def post_item_in_order(user_id, coffee_id, quantity, size):
    user = get_user(user_id)
    order = get_unfinished_order(user_id)
    if not order:
        order = Order(user_id=user.id, status="in_progress")
        session = Session()
        session.add(order)
        session.commit()

    order_item = OrderItem(
        order_id=order.id,
        menu_item_id=coffee_id,
        quantity=int(quantity),
        size=size
    )
    session = Session()
    session.add(order_item)
    session.commit()
    session.close()


def get_menu_item(item_id):
    session = Session()
    order = session.query(MenuItem).filter_by(id=str(item_id)).first()
    session.close()
    return order


def get_coffee_variants(coffee_id):
    session = Session()
    variants = session.query(Variant).options(joinedload(Variant.menu_item)).\
        filter(Variant.menu_item_id == str(coffee_id)).all()
    session.close()
    return variants


def get_variant_for_item(menu_item_id, size):
    session = Session()
    variant = session.query(Variant).filter(Variant.menu_item_id == str(menu_item_id),
                                            Variant.weight == str(size)).first()
    session.close()
    return variant


def get_orders(user_id):
    user = get_user(user_id)
    session = Session()
    orders = session.query(Order).filter(Order.user_id == str(user.id),
                                         Order.status.notin_(['during_payment', 'in_progress'])).all()
    session.close()
    return orders


def get_order(user_id):
    user = get_user(user_id)
    session = Session()
    order = session.query(Order).filter_by(user_id=str(user.id)).order_by(Order.order_date.desc()).first()
    session.close()
    return order


def get_order_byId(order_id):
    session = Session()
    order = session.query(Order).filter_by(id=str(order_id)).order_by(Order.order_date.desc()).first()
    session.close()
    return order


def get_unfinished_order(user_id):
    user = get_user(user_id)
    session = Session()
    order = session.query(Order).filter(Order.user_id == str(user.id), Order.status == 'in_progress').first()
    session.close()
    return order


def get_payment_order(user_id):
    user = get_user(user_id)
    session = Session()
    order = session.query(Order).filter(Order.user_id == str(user.id), Order.status == 'during_payment').first()
    session.close()
    return order


def get_order_items(order_id):
    session = Session()
    order_items = session.query(OrderItem).filter(OrderItem.order_id == int(order_id)).all()
    session.close()
    return order_items


def get_locations(user_coordinates):
    session = Session()
    coffee_houses = session.query(CoffeeHouse).all()

    distances = [
        {
            "id": coffee_house.id,
            "address": coffee_house.address,
            "distance": geodesic(user_coordinates, (coffee_house.latitude, coffee_house.longitude)).meters
        }
        for coffee_house in coffee_houses
    ]

    session.close()

    return distances


def get_cafe_address_by_id(cafe_id):
    session = Session()
    cafe = session.query(CoffeeHouse).filter(CoffeeHouse.id == int(cafe_id)).first()
    session.close()
    if cafe:
        return cafe.address  # Возвращаем адрес кофейни
    return None


def update_user(user_id, dictionary):
    session = Session()
    session.query(User).filter_by(tg_user_id=user_id).update(dictionary)
    session.commit()
    session.close()


def update_order(order_id, dictionary):
    session = Session()
    session.query(Order).filter_by(id=order_id).update(dictionary)
    session.commit()
    session.close()


def delete_orders(user_id, statuses):
    try:
        user = get_user(user_id)
        session = Session()
        orders_to_delete = session.query(Order).filter(Order.user_id == int(user.id), Order.status.in_(statuses)).all()

        if orders_to_delete:
            for order in orders_to_delete:
                session.delete(order)
            session.commit()
        else:
            logging.info(f"Нет заказов для удаления у пользователя {user_id} с состояниями {statuses}")
    except Exception as e:
        logging.error(f"An error occurred while deleting orders: {str(e)}")









