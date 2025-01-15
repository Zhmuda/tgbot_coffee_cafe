from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Float
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String)
    cafe_address = Column(String)
    tg_user_id = Column(String)
    name = Column(String)
    contact_info = Column(String)
    loyalty_points = Column(Integer)
    account_status = Column(String)
    state = Column(String)

    orders = relationship("Order", back_populates="user")


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String)
    total_price = Column(Integer)
    order_date = Column(DateTime, server_default=func.now())
    pickup_location = Column(String)
    payment_method = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = 'order_items'

    order_item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    menu_item_id = Column(String, ForeignKey('menu_items.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    size = Column(String)

    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")


class MenuItem(Base):
    __tablename__ = 'menu_items'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    image = Column(String)

    variants = relationship("Variant", back_populates="menu_item", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="menu_item", cascade="all, delete-orphan")


class Variant(Base):
    __tablename__ = 'variants'

    id = Column(String, primary_key=True)
    menu_item_id = Column(String, ForeignKey('menu_items.id'), nullable=False)
    name = Column(String, nullable=False)
    cost = Column(Integer, nullable=False)
    weight = Column(String, nullable=False)

    menu_item = relationship("MenuItem", back_populates="variants")


class CoffeeHouse(Base):
    __tablename__ = 'coffee_houses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=False)
