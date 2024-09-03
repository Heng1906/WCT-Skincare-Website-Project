from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Float, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# User table
class AccountDB(Base):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    phone_number = Column(String, nullable=False, unique=True)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    photo = Column(String, default=None)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum('active', 'suspended', 'removed', name='account_status'), default='active')
    verification_code = Column(String, nullable=True)
    reset_token = Column(String, nullable=True, default=None)
    reset_token_expires = Column(DateTime, nullable=True, default=None)

    role = relationship('RoleDB', back_populates='users')
    addresses = relationship('UserAddressDB', back_populates='user')
    shopping_carts = relationship('ShoppingCartDB', back_populates='user')
    orders = relationship('OrderDB', back_populates='user')  # Relationship to OrderDB


# Role table
class RoleDB(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    users = relationship('AccountDB', back_populates='role')


# User Address table
class UserAddressDB(Base):
    __tablename__ = "user_address"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    country = Column(String, nullable=False)

    user = relationship('AccountDB', back_populates='addresses')

# Shopping Cart table
class ShoppingCartDB(Base):
    __tablename__ = "shopping_cart"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('AccountDB', back_populates='shopping_carts')
    cart_items = relationship('ShoppingCartItemDB', back_populates='shopping_cart')

# Shopping Cart Item table
class ShoppingCartItemDB(Base):
    __tablename__ = "shopping_cart_item"
    id = Column(Integer, primary_key=True)
    shopping_cart_id = Column(Integer, ForeignKey('shopping_cart.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False)

    shopping_cart = relationship('ShoppingCartDB', back_populates='cart_items')
    product = relationship('ProductDB')

# Product table
class ProductDB(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey('product_category.id'))
    brand_id = Column(Integer, ForeignKey('brand.id'))  # Link to the BrandDB table
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship('ProductCategoryDB', back_populates='products')
    brand = relationship('BrandDB', back_populates='products')  # Relationship to the BrandDB
    cart_items = relationship('ShoppingCartItemDB', back_populates='product')
    promotions = relationship('PromotionDB', secondary='promotion_product_link', back_populates='products')

# Product Category table
class ProductCategoryDB(Base):
    __tablename__ = "product_category"  
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    products = relationship('ProductDB', back_populates='category')

# Brand table
class BrandDB(Base):
    __tablename__ = "brand"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    products = relationship('ProductDB', back_populates='brand')

# Order table
class OrderDB(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum('paid', 'delivering', 'refund', 'cancel', name='order_status'), default='paid')

    user = relationship('AccountDB', back_populates='orders')
    order_items = relationship('OrderItemDB', back_populates='order')

# Order Item table
class OrderItemDB(Base):
    __tablename__ = "order_item"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False)

    order = relationship('OrderDB', back_populates='order_items')
    product = relationship('ProductDB')

# Promotion table
class PromotionDB(Base):
    __tablename__ = "promotion"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    discount_percentage = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    products = relationship('ProductDB', secondary='promotion_product_link', back_populates='promotions')

# Association table for Promotion and Product many-to-many relationship
class PromotionProductLinkDB(Base):
    __tablename__ = "promotion_product_link"
    promotion_id = Column(Integer, ForeignKey('promotion.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), primary_key=True)
