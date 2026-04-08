"""
Billing Schemas - Pydantic Models for API
Basic Billing System for Canteen Management
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


# Invoice Schemas

class InvoiceItem(BaseModel):
    """Invoice item for creating invoices"""
    name: str
    price: float
    quantity: int = 1
    description: Optional[str] = None


class InvoiceCreate(BaseModel):
    """Schema for creating new invoice"""
    customer_id: int  # Changed to int
    order_id: Optional[int] = None  # Changed to int
    items: List[Dict[str, Any]]  # List of items with name, price, quantity, description
    notes: Optional[str] = None
    payment_method: Optional[str] = None
    # Additional customer info for manual invoices
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    # Calculated fields (optional, will be calculated if not provided)
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    total_amount: Optional[float] = None


class InvoiceUpdate(BaseModel):
    """Schema for updating invoice"""
    status: str  # pending, paid, overdue, cancelled
    payment_method: Optional[str] = None


class MarkPaidRequest(BaseModel):
    """Schema for marking invoice as paid"""
    payment_method: str = "cash"


class PaymentInfo(BaseModel):
    """Payment information for invoice"""
    amount: float
    method: str
    status: str
    date: Optional[datetime] = None


class InvoiceResponse(BaseModel):
    """Schema for invoice response"""
    id: str
    invoice_number: str
    customer_id: int
    order_id: Optional[int] = None
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    status: str
    invoice_date: str  # Canonical business date in IST
    due_date: Optional[str] = None
    paid_date: Optional[str] = None
    notes: Optional[str] = None
    payment_method: Optional[str] = None
    created_at: str
    updated_at: str
    is_overdue: bool
    amount_due: float
    # Enhanced fields
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    items: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """Create response from ORM object"""
        data = {
            "id": str(obj.id),
            "invoice_number": obj.invoice_number,
            "customer_id": obj.customer_id,
            "order_id": obj.order_id,
            "subtotal": float(obj.subtotal),
            "tax_amount": float(obj.tax_amount),
            "discount_amount": float(obj.discount_amount),
            "total_amount": float(obj.total_amount),
            "status": obj.status,
            "invoice_date": obj.invoice_date.isoformat() if hasattr(obj, 'invoice_date') and obj.invoice_date else None,
            "due_date": obj.due_date.isoformat() if obj.due_date else None,
            "paid_date": obj.paid_date.isoformat() if obj.paid_date else None,
            "notes": obj.notes,
            "payment_method": obj.payment_method,
            "created_at": obj.created_at.isoformat(),
            "updated_at": obj.updated_at.isoformat(),
            "is_overdue": obj.is_overdue,
            "amount_due": float(obj.amount_due),
            "customer_name": getattr(obj, 'name', None),
            "customer_email": getattr(obj, 'email', None),
            "customer_phone": getattr(obj, 'phone', None),
            "items": None  # Items not stored in database, would need separate table
        }
        return cls(**data)


class PaymentInfo(BaseModel):
    """Payment information for invoice"""
    amount: float
    method: str
    status: str
    date: Optional[datetime] = None


# Payment Schemas

class PaymentCreate(BaseModel):
    """Schema for creating payment"""
    invoice_id: str
    amount: float
    payment_method: str  # cash, card, upi, net_banking, wallet
    transaction_id: Optional[str] = None
    gateway_response: Optional[str] = None


class PaymentStatusUpdate(BaseModel):
    """Schema for updating payment status"""
    status: str  # pending, completed, failed, refunded
    gateway_response: Optional[str] = None


class PaymentResponse(BaseModel):
    """Payment response schema"""
    id: str
    invoice_id: str
    payment_reference: str
    amount: float
    payment_method: str
    transaction_id: Optional[str] = None
    status: str
    gateway_response: Optional[str] = None
    gateway_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """Create response from ORM object"""
        data = {
            "id": str(obj.id),
            "invoice_id": str(obj.invoice_id),
            "payment_reference": obj.payment_reference,
            "amount": float(obj.amount),
            "payment_method": obj.payment_method,
            "transaction_id": obj.transaction_id,
            "status": obj.status,
            "gateway_response": obj.gateway_response,
            "gateway_name": obj.gateway_name,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
            "completed_at": obj.completed_at
        }
        return cls(**data)


# Billing Settings Schemas

class BillingSettingsResponse(BaseModel):
    """Billing settings response schema"""
    id: str
    tax_rate: float
    tax_name: str
    currency: str
    currency_symbol: str
    invoice_prefix: str
    invoice_number_length: int
    accepted_payment_methods: Optional[str] = None
    auto_mark_paid: bool
    payment_due_days: int
    reminder_enabled: bool
    business_name: Optional[str] = None
    business_address: Optional[str] = None
    business_phone: Optional[str] = None
    business_email: Optional[str] = None
    gst_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """Create response from ORM object"""
        data = {
            "id": str(obj.id),
            "tax_rate": float(obj.tax_rate),
            "tax_name": obj.tax_name,
            "currency": obj.currency,
            "currency_symbol": obj.currency_symbol,
            "invoice_prefix": obj.invoice_prefix,
            "invoice_number_length": obj.invoice_number_length,
            "accepted_payment_methods": obj.accepted_payment_methods,
            "auto_mark_paid": obj.auto_mark_paid,
            "payment_due_days": obj.payment_due_days,
            "reminder_enabled": obj.reminder_enabled,
            "business_name": obj.business_name,
            "business_address": obj.business_address,
            "business_phone": obj.business_phone,
            "business_email": obj.business_email,
            "gst_number": obj.gst_number,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at
        }
        return cls(**data)


class BillingSettingsUpdate(BaseModel):
    """Schema for updating billing settings"""
    tax_rate: Optional[float] = None
    tax_name: Optional[str] = None
    currency: Optional[str] = None
    currency_symbol: Optional[str] = None
    invoice_prefix: Optional[str] = None
    invoice_number_length: Optional[int] = None
    accepted_payment_methods: Optional[str] = None
    auto_mark_paid: Optional[bool] = None
    payment_due_days: Optional[int] = None
    reminder_enabled: Optional[bool] = None
    business_name: Optional[str] = None
    business_address: Optional[str] = None
    business_phone: Optional[str] = None
    business_email: Optional[str] = None
    gst_number: Optional[str] = None


# Revenue Analytics Schemas

class PeriodInfo(BaseModel):
    """Period information for revenue summary"""
    start_date: datetime
    end_date: datetime


class RevenueSummary(BaseModel):
    """Revenue summary information"""
    total_revenue: float
    total_orders: int
    total_invoices: int
    paid_invoices: int
    pending_invoices: int
    growth_rate: float = 0.0


class PaymentBreakdown(BaseModel):
    """Payment method breakdown"""
    cash: float
    card: float
    upi: float
    other: float


class RevenueSummaryResponse(BaseModel):
    """Revenue summary response schema"""
    period: PeriodInfo
    summary: RevenueSummary
    payment_breakdown: PaymentBreakdown


class DailyRevenue(BaseModel):
    """Daily revenue data"""
    date: str
    revenue: float
    orders: int
    invoices: int


class CustomerBillingSummary(BaseModel):
    """Customer billing summary"""
    customer_id: int  # Changed to int
    total_invoices: int
    total_invoiced: float
    total_paid: float
    total_pending: float
    last_invoice: Optional[datetime] = None


# Dashboard Schemas

class BillingDashboard(BaseModel):
    """Billing dashboard overview"""
    # Key metrics
    total_revenue: float
    total_invoices: int
    paid_invoices: int
    pending_invoices: int
    overdue_invoices: int
    
    # Today's metrics
    today_revenue: float
    today_orders: int
    today_invoices: int
    
    # Recent activity
    recent_invoices: List[InvoiceResponse]
    recent_payments: List[PaymentResponse]
    
    # Payment breakdown
    payment_methods: Dict[str, float]
    
    # Revenue trend (last 7 days)
    revenue_trend: List[DailyRevenue]


class QuickInvoiceCreate(BaseModel):
    """Quick invoice creation schema"""
    customer_id: str
    amount: float
    description: str
    payment_method: Optional[str] = None
    notes: Optional[str] = None


# Invoice Export Schemas

class InvoiceExportRequest(BaseModel):
    """Invoice export request"""
    invoice_ids: List[str]
    format: str = "pdf"  # pdf, excel, csv
    include_payments: bool = True


class InvoiceExportResponse(BaseModel):
    """Invoice export response"""
    download_url: str
    expires_at: datetime
    file_size: Optional[int] = None


# Bulk Operations Schemas

class BulkInvoiceUpdate(BaseModel):
    """Bulk invoice update schema"""
    invoice_ids: List[str]
    status: str
    payment_method: Optional[str] = None


class BulkPaymentCreate(BaseModel):
    """Bulk payment creation schema"""
    payments: List[PaymentCreate]


# Search and Filter Schemas

class InvoiceSearch(BaseModel):
    """Invoice search parameters"""
    customer_id: Optional[str] = None
    status: Optional[str] = None
    payment_method: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    search_term: Optional[str] = None  # Search in invoice number, notes
    page: int = 1
    limit: int = 50


class InvoiceSearchResponse(BaseModel):
    """Invoice search response"""
    invoices: List[InvoiceResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int


# Validation Schemas

class PaymentMethodValidation(BaseModel):
    """Payment method validation"""
    payment_method: str
    amount: float
    customer_id: int  # Changed to int
    
    class Config:
        schema_extra = {
            "example": {
                "payment_method": "upi",
                "amount": 250.00,
                "customer_id": 1
            }
        }


class TaxCalculation(BaseModel):
    """Tax calculation schema"""
    subtotal: float
    tax_rate: float
    discount_amount: float = 0.0
    
    class Config:
        schema_extra = {
            "example": {
                "subtotal": 1000.00,
                "tax_rate": 18.0,
                "discount_amount": 50.00
            }
        }


class TaxCalculationResponse(BaseModel):
    """Tax calculation response"""
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    tax_rate: float
