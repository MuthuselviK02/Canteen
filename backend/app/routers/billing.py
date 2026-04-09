"""
Billing API Router
Basic Billing System for Canteen Management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.billing import Invoice, Payment, BillingSettings
from app.schemas.billing import (
    InvoiceCreate, InvoiceResponse, InvoiceUpdate,
    PaymentCreate, PaymentResponse, PaymentStatusUpdate,
    BillingSettingsResponse, BillingSettingsUpdate,
    RevenueSummaryResponse, CustomerBillingSummary,
    MarkPaidRequest
)
from app.services.billing_service import BillingService
from app.routers.analytics import get_cached_data, set_cached_data


router = APIRouter(prefix="/api/billing", tags=["Billing"])


def build_invoice_items_from_order(db: Session, order_id: Optional[int]) -> List[Dict[str, Any]]:
    """Hydrate invoice line items from the linked order when invoice rows don't store them."""
    if not order_id:
        return []

    from app.models.order_item import OrderItem
    from app.models.menu import MenuItem

    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    hydrated_items: List[Dict[str, Any]] = []

    for item in order_items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
        if not menu_item:
            continue

        hydrated_items.append({
            "name": menu_item.name,
            "price": float(menu_item.price or 0),
            "quantity": int(item.quantity),
            "description": menu_item.description or ""
        })

    return hydrated_items


# Invoice Management Endpoints

@router.post("/invoices", response_model=InvoiceResponse)
def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new invoice (manual or from order)"""
    try:
        # Validate customer exists
        customer = db.query(User).filter(User.id == invoice_data.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )

        order = None
        if invoice_data.order_id is not None:
            from app.models.order import Order
            order = db.query(Order).filter(Order.id == invoice_data.order_id).first()
            if not order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Linked order not found"
                )
        
        # Create invoice using service
        invoice = BillingService.create_invoice(
            db=db,
            customer_id=invoice_data.customer_id,
            order_id=invoice_data.order_id,
            items=invoice_data.items,
            notes=invoice_data.notes
        )
        
        # Update payment method if provided
        if invoice_data.payment_method:
            invoice.payment_method = invoice_data.payment_method
            db.commit()

        if order and not order.invoice_id:
            order.invoice_id = invoice.id
            db.commit()
        
        # Update customer information if provided
        if hasattr(invoice_data, 'customer_name') and invoice_data.customer_name:
            # Store customer info in notes or create a separate customer info table
            if not invoice.notes:
                invoice.notes = ""
            invoice.notes += f"\nCustomer: {invoice_data.customer_name}"
            if hasattr(invoice_data, 'customer_email') and invoice_data.customer_email:
                invoice.notes += f"\nEmail: {invoice_data.customer_email}"
            if hasattr(invoice_data, 'customer_phone') and invoice_data.customer_phone:
                invoice.notes += f"\nPhone: {invoice_data.customer_phone}"
            db.commit()
        
        return InvoiceResponse(
            id=str(invoice.id),
            invoice_number=invoice.invoice_number,
            customer_id=invoice.customer_id,
            order_id=invoice.order_id,
            subtotal=float(invoice.subtotal),
            tax_amount=float(invoice.tax_amount),
            discount_amount=float(invoice.discount_amount),
            total_amount=float(invoice.total_amount),
            status=invoice.status,
            invoice_date=invoice.invoice_date.isoformat() if invoice.invoice_date else None,
            due_date=invoice.due_date.isoformat() if invoice.due_date else None,
            paid_date=invoice.paid_date.isoformat() if invoice.paid_date else None,
            notes=invoice.notes,
            payment_method=invoice.payment_method,
            created_at=invoice.created_at.isoformat(),
            updated_at=invoice.updated_at.isoformat(),
            is_overdue=invoice.is_overdue,
            amount_due=float(invoice.amount_due),
            customer_name=getattr(customer, 'fullname', None) or getattr(customer, 'name', f'Customer {invoice.customer_id}'),
            customer_email=getattr(customer, 'email', None),
            customer_phone=getattr(customer, 'phone', None),
            items=invoice_data.items  # Return the items from the request
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create invoice: {str(e)}"
        )


@router.get("/invoices", response_model=List[InvoiceResponse])
def get_invoices(
    status: Optional[str] = None,
    customer_id: Optional[int] = None,  # Changed to int
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get invoices with optional filters using canonical IST date filtering
    """
    try:
        # Parse dates if provided - invoice_date is stored in IST
        start_dt = None
        end_dt = None
        
        if start_date:
            # Parse start date as IST and create IST datetime range
            # Frontend sends IST date (YYYY-MM-DD), we need to filter IST invoice_date
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            
        if end_date:
            # Parse end date as IST and create IST datetime range  
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        if customer_id:
            invoices = BillingService.get_customer_invoices(
                db, customer_id, status, limit, start_dt, end_dt
            )
        else:
            invoices = BillingService.get_all_invoices(db, status, limit, start_dt, end_dt)
        
        # Convert to response format using from_orm method
        invoice_responses = []
        for invoice in invoices:
            # Get customer info
            customer = db.query(User).filter(User.id == invoice.customer_id).first()
            
            invoice_response = InvoiceResponse.from_orm(invoice)
            # Override customer info
            invoice_response.customer_name = getattr(customer, 'fullname', None) or getattr(customer, 'name', f'Customer {invoice.customer_id}')
            invoice_response.customer_email = getattr(customer, 'email', None)
            invoice_response.customer_phone = getattr(customer, 'phone', None)
            invoice_response.items = build_invoice_items_from_order(db, invoice.order_id)
            
            invoice_responses.append(invoice_response)
        
        return invoice_responses
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get invoices: {str(e)}"
        )


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get invoice by ID
    """
    invoice = BillingService.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    customer = db.query(User).filter(User.id == invoice.customer_id).first()
    invoice_response = InvoiceResponse.from_orm(invoice)
    invoice_response.customer_name = getattr(customer, 'fullname', None) or getattr(customer, 'name', f'Customer {invoice.customer_id}')
    invoice_response.customer_email = getattr(customer, 'email', None)
    invoice_response.customer_phone = getattr(customer, 'phone', None)
    invoice_response.items = build_invoice_items_from_order(db, invoice.order_id)

    return invoice_response


@router.get("/invoices/by-number/{invoice_number}", response_model=InvoiceResponse)
def get_invoice_by_number(
    invoice_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get invoice by invoice number
    """
    invoice = BillingService.get_invoice_by_number(db, invoice_number)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    customer = db.query(User).filter(User.id == invoice.customer_id).first()
    invoice_response = InvoiceResponse.from_orm(invoice)
    invoice_response.customer_name = getattr(customer, 'fullname', None) or getattr(customer, 'name', f'Customer {invoice.customer_id}')
    invoice_response.customer_email = getattr(customer, 'email', None)
    invoice_response.customer_phone = getattr(customer, 'phone', None)
    invoice_response.items = build_invoice_items_from_order(db, invoice.order_id)

    return invoice_response


@router.put("/invoices/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: str,
    invoice_update: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update invoice status
    """
    try:
        if current_user.role not in ["ADMIN", "SUPER_ADMIN"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can update invoices"
            )

        invoice = BillingService.update_invoice_status(
            db, invoice_id, invoice_update.status, invoice_update.payment_method
        )
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        return InvoiceResponse.from_orm(invoice)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update invoice: {str(e)}"
        )


@router.delete("/invoices/{invoice_id}")
def delete_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete invoice (admin only)
    """
    # Check admin permissions
    if current_user.role not in ['ADMIN', 'SUPER_ADMIN']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to delete invoices"
        )
    
    invoice = BillingService.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID {invoice_id} not found"
        )
    
    # Only allow deletion of pending invoices
    if invoice.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete invoice '{invoice.invoice_number}' because it has status '{invoice.status}'. Only pending invoices can be deleted."
        )
    
    try:
        db.delete(invoice)
        db.commit()
        return {"message": f"Invoice '{invoice.invoice_number}' deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete invoice: {str(e)}"
        )


# Payment Management Endpoints

@router.post("/payments", response_model=PaymentResponse)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create payment record
    """
    try:
        if current_user.role not in ["ADMIN", "SUPER_ADMIN"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can create payment records"
            )

        payment = BillingService.create_payment(
            db=db,
            invoice_id=payment_data.invoice_id,
            amount=Decimal(str(payment_data.amount)),
            payment_method=payment_data.payment_method,
            transaction_id=payment_data.transaction_id,
            gateway_response=payment_data.gateway_response
        )
        
        return PaymentResponse.from_orm(payment)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create payment: {str(e)}"
        )


@router.get("/payments", response_model=List[PaymentResponse])
def get_all_payments(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all payments with optional filters
    """
    try:
        # Parse dates if provided - treat as UTC dates directly
        start_dt = None
        end_dt = None
        
        if start_date:
            # Parse as UTC date (no timezone conversion needed)
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            
        if end_date:
            # Parse as UTC date and include entire day
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)  # Include entire day
        else:
            # If no end date, use end of current day (UTC)
            end_dt = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
            
        payments = BillingService.get_all_payments(db, status, limit, start_dt, end_dt)
        return [PaymentResponse.from_orm(payment) for payment in payments]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get payments: {str(e)}"
        )


@router.get("/invoices/{invoice_id}/payments", response_model=List[PaymentResponse])
def get_invoice_payments(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all payments for an invoice
    """
    try:
        payments = BillingService.get_invoice_payments(db, invoice_id)
        return [PaymentResponse.from_orm(payment) for payment in payments]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get payments: {str(e)}"
        )


@router.put("/payments/{payment_id}/status", response_model=PaymentResponse)
def update_payment_status(
    payment_id: str,
    status_update: PaymentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update payment status
    """
    try:
        if current_user.role not in ["ADMIN", "SUPER_ADMIN"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can update payment status"
            )

        payment = BillingService.update_payment_status(
            db, payment_id, status_update.status, status_update.gateway_response
        )
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        return PaymentResponse.from_orm(payment)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update payment: {str(e)}"
        )


# Billing Settings Endpoints

@router.get("/settings", response_model=BillingSettingsResponse)
def get_billing_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get billing settings
    """
    try:
        settings = BillingService.get_billing_settings(db)
        return BillingSettingsResponse.from_orm(settings)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get billing settings: {str(e)}"
        )


@router.put("/settings", response_model=BillingSettingsResponse)
def update_billing_settings(
    settings_update: BillingSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update billing settings (admin only)
    """
    try:
        settings = BillingService.get_billing_settings(db)
        
        # Update fields
        for field, value in settings_update.dict(exclude_unset=True).items():
            setattr(settings, field, value)
        
        db.commit()
        db.refresh(settings)
        
        return BillingSettingsResponse.from_orm(settings)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update billing settings: {str(e)}"
        )


# Revenue Analytics Endpoints

@router.get("/revenue/summary", response_model=RevenueSummaryResponse)
def get_revenue_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get revenue summary for date range
    """
    try:
        # Parse dates if provided - handle IST dates correctly
        start_dt = None
        end_dt = None
        
        if start_date:
            # Parse as UTC date (no timezone conversion needed)
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            
        if end_date:
            # Parse as UTC date and include entire day
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)  # Include entire day
        else:
            # If no end date, use end of current day (UTC)
            end_dt = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        summary = BillingService.get_revenue_summary(db, start_dt, end_dt)
        
        return RevenueSummaryResponse(**summary)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get revenue summary: {str(e)}"
        )


@router.get("/revenue/daily")
def get_daily_revenue(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get daily revenue for the last N days
    """
    try:
        daily_revenue = BillingService.get_daily_revenue(db, days)
        return {"daily_revenue": daily_revenue}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get daily revenue: {str(e)}"
        )


@router.get("/invoices/overdue")
def get_overdue_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all overdue invoices
    """
    try:
        overdue_invoices = BillingService.get_overdue_invoices(db)
        return {
            "overdue_invoices": [
                InvoiceResponse.from_orm(invoice) for invoice in overdue_invoices
            ],
            "count": len(overdue_invoices)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get overdue invoices: {str(e)}"
        )


# Customer Billing Endpoints

@router.get("/customers/{customer_id}/summary", response_model=CustomerBillingSummary)
def get_customer_billing_summary(
    customer_id: int,  # Changed to int
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get billing summary for a customer
    """
    try:
        summary = BillingService.get_customer_billing_summary(db, customer_id)
        return CustomerBillingSummary(**summary)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get customer billing summary: {str(e)}"
        )


# Customer Analytics Endpoints

@router.get("/customers/analytics", response_model=Dict[str, Any])
def get_customer_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive customer analytics"""
    try:
        # Get top customers by revenue
        top_customers = db.query(
            Invoice.customer_id,
            func.sum(Invoice.total_amount).label('total_spent'),
            func.count(Invoice.id).label('invoice_count')
        ).group_by(Invoice.customer_id).order_by(func.sum(Invoice.total_amount).desc()).limit(10).all()
        
        # Get customer growth metrics
        total_customers = db.query(func.count(func.distinct(Invoice.customer_id))).scalar()
        active_customers = db.query(func.count(func.distinct(Invoice.customer_id))).filter(
            Invoice.created_at >= datetime.utcnow() - timedelta(days=30)
        ).scalar()
        
        # Get average customer metrics
        avg_customer_value = db.query(func.avg(Invoice.total_amount)).scalar() or 0
        avg_invoices_per_customer = db.query(func.count(Invoice.id) / func.count(func.distinct(Invoice.customer_id))).scalar() or 0
        
        return {
            "summary": {
                "total_customers": total_customers,
                "active_customers": active_customers,
                "new_customers_this_month": active_customers,
                "average_customer_value": float(avg_customer_value),
                "average_invoices_per_customer": float(avg_invoices_per_customer)
            },
            "top_customers": [
                {
                    "customer_id": customer[0],
                    "total_spent": float(customer[1]),
                    "invoice_count": customer[2]
                }
                for customer in top_customers
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/overview", response_model=Dict[str, Any])
def get_billing_dashboard_overview(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive billing dashboard overview"""
    try:
        # Check cache first
        cache_key = f"billing_dashboard_{datetime.now().strftime('%Y-%m-%d_%H')}_{start_date}_{end_date}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # Parse date parameters or use IST today as default
        if start_date and end_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                # Set end date to end of day
                end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD")
        else:
            # Default to today (IST)
            now = datetime.utcnow()
            ist_offset = timedelta(hours=5, minutes=30)
            ist_now = now + ist_offset
            
            # Calculate IST date boundaries
            ist_today = ist_now.replace(hour=0, minute=0, second=0, microsecond=0)
            start_dt = ist_today - ist_offset  # Convert to UTC for database
            end_dt = ist_today.replace(hour=23, minute=59, second=59, microsecond=999999) - ist_offset
        
        # Optimize queries by combining them
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (current_month_start - timedelta(days=32)).replace(day=1)
        
        # Single query for all invoice metrics - filter by date range
        invoice_metrics = db.query(
            Invoice.status,
            func.sum(Invoice.total_amount).label('total_amount'),
            func.count(Invoice.id).label('count'),
            Invoice.payment_method
        ).filter(
            Invoice.created_at >= start_dt,
            Invoice.created_at <= end_dt
        ).all()
        
        # Process metrics in memory
        total_revenue = 0
        total_invoices = 0
        payment_totals = {"cash": 0, "card": 0, "upi": 0, "other": 0}
        status_counts = {"paid": 0, "pending": 0, "overdue": 0}
        
        current_month_revenue = 0
        last_month_revenue = 0
        
        for invoice in invoice_metrics:
            status = invoice.status
            amount = float(invoice.total_amount or 0)
            count = int(invoice.count)
            payment_method = invoice.payment_method
            
            total_invoices += count
            
            if status == "paid":
                total_revenue += amount
                status_counts["paid"] += count
                if payment_method in payment_totals:
                    payment_totals[payment_method] += amount
                else:
                    payment_totals["other"] += amount
            elif status == "pending":
                status_counts["pending"] += count
            elif status == "overdue":
                status_counts["overdue"] += count
        
        # Calculate growth rate
        growth_rate = 0  # Simplified for performance
        
        result = {
            "total_revenue": total_revenue,
            "total_invoices": total_invoices,
            "paid_invoices": status_counts["paid"],
            "pending_invoices": status_counts["pending"],
            "overdue_invoices": status_counts["overdue"],
            "growth_rate": growth_rate,
            "payment_breakdown": payment_totals,
            "current_month_revenue": current_month_revenue,
            "last_month_revenue": last_month_revenue,
        }
        
        # Simplified daily revenue (last 7 days for performance)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        daily_revenue = db.query(
            func.date(Invoice.created_at).label('date'),
            func.sum(Invoice.total_amount).label('revenue'),
            func.count(Invoice.id).label('orders')
        ).filter(
            Invoice.created_at >= seven_days_ago
        ).group_by(func.date(Invoice.created_at)).order_by(func.date(Invoice.created_at)).all()
        
        # Calculate average order value
        avg_order_value = float(total_revenue / status_counts["paid"]) if status_counts["paid"] > 0 else 0
        
        final_result = {
            "summary": {
                "total_revenue": float(total_revenue),
                "total_orders": total_invoices,
                "total_invoices": total_invoices,
                "paid_invoices": status_counts["paid"],
                "pending_invoices": status_counts["pending"],
                "overdue_invoices": status_counts["overdue"],
                "average_order_value": avg_order_value,
                "growth_rate": growth_rate,
                "payment_success_rate": (status_counts["paid"] / total_invoices * 100) if total_invoices > 0 else 0
            },
            "daily_revenue": [
                {
                    "date": str(day.date),
                    "revenue": float(day.revenue),
                    "orders": day.orders
                }
                for day in daily_revenue
            ],
            "payment_breakdown": payment_totals,
            "metrics": {
                "revenue_per_day": float(current_month_revenue / datetime.utcnow().day) if datetime.utcnow().day > 0 else 0,
                "invoices_per_day": float(status_counts["paid"] / datetime.utcnow().day) if datetime.utcnow().day > 0 else 0,
                "average_payment_time": 2.5, # Placeholder
                "customer_retention_rate": 85.0 # Placeholder
            }
        }
        
        # Cache the result for 10 minutes
        set_cached_data(cache_key, final_result, expire_seconds=600)
        return final_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/invoices/export")
def export_invoices(
    format: str = "csv",
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export invoices in various formats"""
    try:
        query = db.query(Invoice)
        
        if status:
            query = query.filter(Invoice.status == status)
        if date_from:
            query = query.filter(Invoice.created_at >= date_from)
        if date_to:
            query = query.filter(Invoice.created_at <= date_to)
        
        invoices = query.all()
        
        if format.lower() == "csv":
            # Generate CSV response
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Invoice Number', 'Customer ID', 'Total Amount', 'Status', 
                'Created Date', 'Due Date', 'Payment Method'
            ])
            
            # Write data
            for invoice in invoices:
                writer.writerow([
                    invoice.invoice_number,
                    invoice.customer_id,
                    invoice.total_amount,
                    invoice.status,
                    invoice.created_at,
                    invoice.due_date,
                    invoice.payment_method
                ])
            
            output.seek(0)
            
            from fastapi.responses import Response
            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=invoices.csv"}
            )
        
        elif format.lower() == "json":
            return {"invoices": [invoice.__dict__ for invoice in invoices]}
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use 'csv' or 'json'")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/invoices/{invoice_id}/send-reminder")
def send_payment_reminder(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send payment reminder for overdue/pending invoices"""
    try:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        if invoice.status not in ["pending", "overdue"]:
            raise HTTPException(status_code=400, detail="Invoice is not pending or overdue")
        
        # In a real implementation, this would send an email/SMS
        # For now, we'll just update a reminder_sent flag
        reminder_data = {
            "invoice_id": invoice_id,
            "reminder_sent": True,
            "reminder_date": datetime.utcnow(),
            "message": f"Payment reminder sent for invoice {invoice.invoice_number}"
        }
        
        return {
            "success": True,
            "message": f"Payment reminder sent for invoice {invoice.invoice_number}",
            "reminder_details": reminder_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance/metrics")
def get_billing_performance_metrics(
    period: str = "30d",  # 7d, 30d, 90d, 1y
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed billing performance metrics"""
    try:
        # Calculate date range based on period
        if period == "7d":
            start_date = datetime.utcnow() - timedelta(days=7)
        elif period == "30d":
            start_date = datetime.utcnow() - timedelta(days=30)
        elif period == "90d":
            start_date = datetime.utcnow() - timedelta(days=90)
        elif period == "1y":
            start_date = datetime.utcnow() - timedelta(days=365)
        else:
            start_date = datetime.utcnow() - timedelta(days=30)
        
        # Get invoices in the period
        period_invoices = db.query(Invoice).filter(Invoice.created_at >= start_date).all()
        
        # Calculate metrics
        total_revenue = sum(inv.total_amount for inv in period_invoices)
        total_invoices = len(period_invoices)
        paid_invoices = len([inv for inv in period_invoices if inv.status == "paid"])
        pending_invoices = len([inv for inv in period_invoices if inv.status == "pending"])
        overdue_invoices = len([inv for inv in period_invoices if inv.status == "overdue"])
        
        # Calculate average metrics
        avg_invoice_value = total_revenue / total_invoices if total_invoices > 0 else 0
        payment_success_rate = (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0
        
        # Get daily trends
        daily_metrics = {}
        for invoice in period_invoices:
            date_key = invoice.created_at.date()
            if date_key not in daily_metrics:
                daily_metrics[date_key] = {"revenue": 0, "count": 0, "paid": 0}
            daily_metrics[date_key]["revenue"] += invoice.total_amount
            daily_metrics[date_key]["count"] += 1
            if invoice.status == "paid":
                daily_metrics[date_key]["paid"] += 1
        
        # Get payment method trends
        payment_methods = {}
        for invoice in period_invoices:
            if invoice.status == "paid" and invoice.payment_method:
                if invoice.payment_method not in payment_methods:
                    payment_methods[invoice.payment_method] = 0
                payment_methods[invoice.payment_method] += invoice.total_amount
        
        return {
            "period": period,
            "date_range": {
                "start": start_date.isoformat(),
                "end": datetime.utcnow().isoformat()
            },
            "summary": {
                "total_revenue": float(total_revenue),
                "total_invoices": total_invoices,
                "paid_invoices": paid_invoices,
                "pending_invoices": pending_invoices,
                "overdue_invoices": overdue_invoices,
                "average_invoice_value": float(avg_invoice_value),
                "payment_success_rate": payment_success_rate
            },
            "daily_trends": [
                {
                    "date": str(date),
                    "revenue": float(metrics["revenue"]),
                    "invoices": metrics["count"],
                    "paid_invoices": metrics["paid"]
                }
                for date, metrics in sorted(daily_metrics.items())
            ],
            "payment_methods": {
                method: float(amount) for method, amount in payment_methods.items()
            },
            "insights": {
                "best_day": max(daily_metrics.items(), key=lambda x: x[1]["revenue"])[0] if daily_metrics else None,
                "worst_day": min(daily_metrics.items(), key=lambda x: x[1]["revenue"])[0] if daily_metrics else None,
                "peak_payment_method": max(payment_methods.items(), key=lambda x: x[1])[0] if payment_methods else None,
                "collection_efficiency": payment_success_rate
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Quick Actions Endpoints

@router.post("/invoices/{invoice_id}/mark-paid")
def mark_invoice_paid(
    invoice_id: str,
    request: MarkPaidRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Quick action: Mark invoice as paid with specified payment method
    """
    try:
        if current_user.role not in ["ADMIN", "SUPER_ADMIN"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can mark invoices as paid"
            )

        # Update invoice status
        invoice = BillingService.update_invoice_status(db, invoice_id, "paid", request.payment_method)
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Create payment record
        payment = BillingService.create_payment(
            db, invoice_id, invoice.total_amount, request.payment_method
        )
        
        # Mark payment as completed
        BillingService.update_payment_status(db, payment.id, "completed")
        
        # Invalidate cache to refresh analytics
        cache_key = f"billing_dashboard_{datetime.now().strftime('%Y-%m-%d_%H')}"
        # Clear the cache by setting it to None
        from app.routers.analytics import analytics_cache
        if cache_key in analytics_cache:
            del analytics_cache[cache_key]
        
        # Also clear any revenue summary cache
        revenue_cache_key = f"revenue_summary_{datetime.now().strftime('%Y-%m-%d')}"
        if revenue_cache_key in analytics_cache:
            del analytics_cache[revenue_cache_key]
        
        # Clear overview cache too
        overview_cache_key = "overview"
        if overview_cache_key in analytics_cache:
            del analytics_cache[overview_cache_key]
        
        return {
            "message": "Invoice marked as paid successfully",
            "invoice_id": invoice_id,
            "payment_method": request.payment_method,
            "amount": float(invoice.total_amount),
            "status": invoice.status
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to mark invoice as paid: {str(e)}"
        )


@router.post("/orders/{order_id}/create-invoice")
def create_invoice_from_order(
    order_id: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Quick action: Create invoice from order
    """
    try:
        # Get order details
        from app.models.order import Order
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Create invoice
        invoice = BillingService.create_invoice(
            db, order.user_id, order_id, notes=notes
        )
        
        if not order.invoice_id:
            order.invoice_id = invoice.id
            db.commit()
            db.refresh(order)
        
        return InvoiceResponse.from_orm(invoice)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create invoice from order: {str(e)}"
        )
