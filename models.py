from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
import enum
from base import Base

class ProductType(str, enum.Enum):
    STARS = "stars"
    GIFT = "gift"
    REACTION = "reaction"
    PREMIUM = "premium"

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    AWAITING_RECEIPT = "awaiting_receipt"
    AWAITING_CONFIRM = "awaiting_confirm"
    PAID = "paid"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PriceConfig(Base):
    __tablename__ = "price_config"
    __table_args__ = {'extend_existing': True}
    
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[int] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(String(128))
    unit: Mapped[str] = mapped_column(String(32), default="تومان")

class UnitLimit(Base):
    __tablename__ = "unit_limits"
    __table_args__ = {'extend_existing': True}
    
    product_type: Mapped[ProductType] = mapped_column(Enum(ProductType), primary_key=True)
    min_qty: Mapped[int] = mapped_column(Integer, default=1)
    max_qty: Mapped[int] = mapped_column(Integer, default=2000)

class GiftItem(Base):
    __tablename__ = "gift_items"
    __table_args__ = {'extend_existing': True}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(64))
    emoji: Mapped[str] = mapped_column(String(8), default="🎁")
    star_cost: Mapped[int] = mapped_column(Integer)
    min_qty: Mapped[int] = mapped_column(Integer, default=1)
    max_qty: Mapped[int] = mapped_column(Integer, default=2000)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

class Order(Base):
    __tablename__ = "orders"
    __table_args__ = {'extend_existing': True}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    product_type: Mapped[ProductType] = mapped_column(Enum(ProductType))
    gift_item_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("gift_items.id"), nullable=True)
    product_detail: Mapped[str] = mapped_column(String(128))
    quantity: Mapped[int] = mapped_column(Integer)
    recipient: Mapped[str] = mapped_column(String(64))
    price_toman: Mapped[int] = mapped_column(Integer)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING)
    receipt_file_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    receipt_message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

class Wallet(Base):
    __tablename__ = "wallets"
    __table_args__ = {'extend_existing': True}
    
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), primary_key=True)
    balance: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)