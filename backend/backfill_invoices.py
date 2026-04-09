#!/usr/bin/env python3
"""
Backfill invoices for existing completed orders that don't have invoices
"""

import sys
sys.path.append('.')

from app.database.session import SessionLocal
from app.services.billing_service import BillingService
from app.services.order_time_service import OrderTimeService
from app.models.order import Order
from datetime import datetime

def backfill_invoices():
    """Create invoices for completed orders that don't have them"""
    db = SessionLocal()

    try:
        # Find completed orders without invoices
        orders_without_invoices = db.query(Order).filter(
            Order.status == "completed",
            Order.invoice_id.is_(None)
        ).all()

        print(f"Found {len(orders_without_invoices)} completed orders without invoices")

        for order in orders_without_invoices:
            try:
                print(f"Processing order {order.id}...")

                # Get order items to create invoice
                from app.models.order_item import OrderItem
                from app.models.menu import MenuItem
                
                order_items_query = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
                order_items = []
                for item in order_items_query:
                    menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
                    if menu_item:
                        order_items.append({
                            "name": menu_item.name,
                            "price": float(menu_item.price),
                            "quantity": int(item.quantity),
                            "description": menu_item.description or ""
                        })

                # Create invoice
                invoice = BillingService.create_invoice(
                    db=db,
                    customer_id=order.user_id,
                    order_id=order.id,
                    items=order_items,
                    notes=f"Backfilled invoice for completed order #{order.id}"
                )

                # Update order with invoice ID
                order.invoice_id = str(invoice.id)
                print(f"Created invoice {invoice.id} for order {order.id}")

            except Exception as e:
                print(f"Error creating invoice for order {order.id}: {e}")
                continue

        db.commit()
        print("Backfill completed successfully")

    except Exception as e:
        print(f"Error in backfill: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    backfill_invoices()