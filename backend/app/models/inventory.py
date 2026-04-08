from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from datetime import datetime
from app.database.base import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), unique=True)
    stock_quantity = Column(Integer, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)


class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity_used = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class InventoryStockUpdate(Base):
    __tablename__ = "inventory_stock_updates"

    id = Column(Integer, primary_key=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    previous_stock = Column(Integer, nullable=False)
    quantity_delta = Column(Integer, nullable=False)
    new_stock = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)  # restock / correction / wastage / order_completion
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)  # Link to order if applicable
    created_at = Column(DateTime, default=datetime.utcnow)
