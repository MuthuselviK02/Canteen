from app.database.session import get_db
from app.models.order import Order
from app.models.billing import Invoice
from sqlalchemy import and_

db = next(get_db())

# Find orders with invoices but check if invoices have items
orders_with_invoices = db.query(Order).filter(
    and_(Order.status == 'completed', Order.invoice_id.isnot(None))
).all()

print(f'Orders with invoices: {len(orders_with_invoices)}')

for order in orders_with_invoices[:3]:  # Check first 3
    invoice = db.query(Invoice).filter(Invoice.id == order.invoice_id).first()
    if invoice:
        items_count = len(invoice.items) if hasattr(invoice, 'items') else 'N/A'
        print(f'Order {order.id}: Invoice {invoice.id}, Items: {items_count}')