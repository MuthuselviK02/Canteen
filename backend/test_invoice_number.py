"""
Test invoice number generation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.session import SessionLocal
from app.services.billing_service import BillingService

def test_invoice_number_generation():
    try:
        db = SessionLocal()
        
        print("🔢 Testing invoice number generation...")
        
        # Test the generate_invoice_number function
        invoice_number = BillingService.generate_invoice_number(db)
        print(f"Generated invoice number: {invoice_number}")
        
        # Check what the last invoice actually is
        from app.models.billing import Invoice
        from app.core.config import settings
        
        last_invoice = db.query(Invoice).filter(
            Invoice.invoice_number.like(f"{settings.invoice_prefix}%")
        ).order_by(desc(Invoice.created_at)).first()
        
        if last_invoice:
            print(f"Last invoice in database: {last_invoice.invoice_number}")
        else:
            print("No invoices found in database")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Invoice Number Generation")
    print("=" * 40)
    test_invoice_number_generation()
