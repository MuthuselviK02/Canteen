"""
Billing Database Models
Basic Billing System for Canteen Management
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database.base import Base


class Invoice(Base):
    """
    Invoice Model - Basic Billing System
    """
    __tablename__ = "invoices"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Changed to Integer
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)  # Changed to Integer
    
    # Financial Details
    subtotal = Column(Float, nullable=False, default=0.0)
    tax_amount = Column(Float, nullable=False, default=0.0)
    discount_amount = Column(Float, nullable=False, default=0.0)
    total_amount = Column(Float, nullable=False, default=0.0)
    
    # Status and Dates
    status = Column(String(20), nullable=False, default="pending")  # pending, paid, overdue, cancelled
    invoice_date = Column(DateTime, nullable=False, default=datetime.utcnow)  # Business date in IST
    due_date = Column(DateTime, nullable=True)
    paid_date = Column(DateTime, nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    payment_method = Column(String(50), nullable=True)  # cash, card, upi, other
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Using string references to avoid circular imports
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Invoice {self.invoice_number} - {self.status}>"
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        if self.status != "pending" or not self.due_date:
            return False
        return datetime.utcnow() > self.due_date
    
    @property
    def amount_due(self):
        """Calculate remaining amount due"""
        if self.status == "paid":
            return 0.00
        
        paid_amount = sum(payment.amount for payment in self.payments 
                          if payment.status == "completed")
        return float(self.total_amount - paid_amount)


class Payment(Base):
    """
    Payment Model - Payment Processing
    """
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id = Column(String(36), ForeignKey("invoices.id"), nullable=False)
    payment_reference = Column(String(100), unique=True, nullable=True, index=True)
    
    # Payment Details
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)  # cash, card, upi, net_banking, wallet
    transaction_id = Column(String(100), nullable=True)  # Gateway transaction ID
    
    # Status
    status = Column(String(20), nullable=False, default="pending")  # pending, completed, failed, refunded
    
    # Payment Gateway Details
    gateway_response = Column(Text, nullable=True)  # JSON response from payment gateway
    gateway_name = Column(String(50), nullable=True)  # razorpay, stripe, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships - Using string references to avoid circular imports
    invoice = relationship("Invoice", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment {self.payment_reference} - {self.status}>"


class BillingSettings(Base):
    """
    Billing Settings Model - System Configuration
    """
    __tablename__ = "billing_settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Tax Settings
    tax_rate = Column(Float, nullable=False, default=18.0)  # GST rate
    tax_name = Column(String(50), nullable=False, default="GST")
    
    # Currency Settings
    currency = Column(String(10), nullable=False, default="INR")
    currency_symbol = Column(String(5), nullable=False, default="₹")
    
    # Invoice Settings
    invoice_prefix = Column(String(20), nullable=False, default="INV")
    invoice_number_length = Column(Integer, nullable=False, default=6)
    
    # Payment Settings
    accepted_payment_methods = Column(Text, nullable=True)  # JSON array of payment methods
    auto_mark_paid = Column(Boolean, default=False)  # Auto-mark cash payments as paid
    
    # Reminder Settings
    payment_due_days = Column(Integer, nullable=False, default=7)  # Days until payment due
    reminder_enabled = Column(Boolean, default=True)
    
    # Business Information
    business_name = Column(String(200), nullable=True)
    business_address = Column(Text, nullable=True)
    business_phone = Column(String(20), nullable=True)
    business_email = Column(String(100), nullable=True)
    gst_number = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<BillingSettings {self.currency} - {self.tax_rate}%>"


class RevenueSummary(Base):
    """
    Revenue Summary Model - Daily Revenue Tracking
    """
    __tablename__ = "revenue_summary"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(DateTime, nullable=False, index=True)  # Date of revenue
    
    # Revenue Metrics
    total_revenue = Column(Float, nullable=False, default=0.0)
    total_orders = Column(Integer, nullable=False, default=0)
    total_invoices = Column(Integer, nullable=False, default=0)
    paid_invoices = Column(Integer, nullable=False, default=0)
    pending_invoices = Column(Integer, nullable=False, default=0)
    
    # Payment Method Breakdown
    cash_revenue = Column(Float, nullable=False, default=0.0)
    card_revenue = Column(Float, nullable=False, default=0.0)
    upi_revenue = Column(Float, nullable=False, default=0.0)
    other_revenue = Column(Float, nullable=False, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<RevenueSummary {self.date.date()} - ₹{self.total_revenue}>"
