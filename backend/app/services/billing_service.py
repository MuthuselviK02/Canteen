"""
Billing Service - Core Billing Logic
Basic Billing System for Canteen Management
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import uuid

from app.models.billing import Invoice, Payment, BillingSettings, RevenueSummary
from app.models.user import User
from app.models.order import Order
from app.database.session import get_db


class BillingService:
    """
    Core Billing Service - Handles all billing operations
    """
    
    @staticmethod
    def get_billing_settings(db: Session) -> BillingSettings:
        """Get or create billing settings"""
        settings = db.query(BillingSettings).first()
        if not settings:
            settings = BillingSettings()
            db.add(settings)
            db.commit()
            db.refresh(settings)
        return settings
    
    @staticmethod
    def generate_invoice_number(db: Session) -> str:
        """Generate unique invoice number"""
        settings = BillingService.get_billing_settings(db)
        
        # Get last invoice number ordered by invoice number (not created_at)
        last_invoice = db.query(Invoice).filter(
            Invoice.invoice_number.like(f"{settings.invoice_prefix}%")
        ).order_by(desc(Invoice.invoice_number)).first()
        
        if last_invoice:
            # Extract numeric part and increment
            try:
                last_num = int(last_invoice.invoice_number[len(settings.invoice_prefix):])
                new_num = last_num + 1
            except ValueError:
                new_num = 1
        else:
            new_num = 1
        
        # Format with leading zeros
        invoice_number = f"{settings.invoice_prefix}{str(new_num).zfill(settings.invoice_number_length)}"
        return invoice_number
    
    @staticmethod
    def create_invoice(
        db: Session,
        customer_id: int,  
        order_id: Optional[int] = None,  
        items: Optional[List[Dict[str, Any]]] = None,
        notes: Optional[str] = None
    ) -> Invoice:
        """Create a new invoice"""
        try:
            # Get billing settings
            settings = BillingService.get_billing_settings(db)
            
            # Calculate totals
            subtotal = 0.0
            if items:
                for item in items:
                    subtotal += float(item.get('price', 0)) * int(item.get('quantity', 1))
            
            tax_amount = subtotal * (settings.tax_rate / 100)
            total_amount = subtotal + tax_amount
            
            # Generate invoice number
            invoice_number = BillingService.generate_invoice_number(db)
            
            # Set due date (30 days from now)
            due_date = datetime.now() + timedelta(days=30)
            
            # Calculate IST business date (UTC + 5:30)
            ist_offset = timedelta(hours=5, minutes=30)
            ist_now = datetime.now() + ist_offset
            
            # Create invoice
            invoice = Invoice(
                invoice_number=invoice_number,
                customer_id=customer_id,
                order_id=order_id,
                subtotal=subtotal,
                tax_amount=tax_amount,
                discount_amount=0.0,
                total_amount=total_amount,
                status="pending",
                invoice_date=ist_now,  # Business date in IST
                due_date=due_date,
                notes=notes
            )
            
            db.add(invoice)
            db.commit()
            db.refresh(invoice)
            
            return invoice
            
        except Exception as e:
            db.rollback()
            raise e
    
    @staticmethod
    def get_invoice(db: Session, invoice_id: str) -> Optional[Invoice]:
        """Get invoice by ID"""
        return db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    @staticmethod
    def get_invoice_by_number(db: Session, invoice_number: str) -> Optional[Invoice]:
        """Get invoice by invoice number"""
        return db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()
    
    @staticmethod
    def get_customer_invoices(
        db: Session,
        customer_id: int,  # Changed to int
        status: Optional[str] = None,
        limit: int = 50,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Invoice]:
        """Get all invoices for a customer using canonical invoice_date filtering"""
        query = db.query(Invoice).filter(Invoice.customer_id == customer_id)
        
        if status:
            query = query.filter(Invoice.status == status)
        
        if start_date:
            query = query.filter(Invoice.invoice_date >= start_date)
        
        if end_date:
            query = query.filter(Invoice.invoice_date < end_date)
        
        return query.order_by(desc(Invoice.invoice_date)).limit(limit).all()
    
    @staticmethod
    def get_all_invoices(
        db: Session,
        status: Optional[str] = None,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Invoice]:
        """Get all invoices with optional status filter using canonical invoice_date filtering"""
        query = db.query(Invoice)
        
        if status:
            query = query.filter(Invoice.status == status)
        
        if start_date:
            query = query.filter(Invoice.invoice_date >= start_date)
        
        if end_date:
            query = query.filter(Invoice.invoice_date < end_date)
        
        return query.order_by(desc(Invoice.invoice_date)).limit(limit).all()
    
    @staticmethod
    def update_invoice_status(
        db: Session,
        invoice_id: str,
        status: str,
        payment_method: Optional[str] = None
    ) -> Optional[Invoice]:
        """Update invoice status"""
        invoice = BillingService.get_invoice(db, invoice_id)
        if not invoice:
            return None
        
        invoice.status = status
        if payment_method:
            invoice.payment_method = payment_method
        
        if status == "paid":
            invoice.paid_date = datetime.now()
        
        db.commit()
        db.refresh(invoice)
        return invoice
    
    @staticmethod
    def create_payment(
        db: Session,
        invoice_id: str,
        amount: float,
        payment_method: str,
        transaction_id: Optional[str] = None,
        gateway_response: Optional[str] = None
    ) -> Payment:
        """
        Create payment record
        """
        # Generate payment reference
        payment_reference = f"PAY{uuid.uuid4().hex[:12].upper()}"
        
        payment = Payment(
            invoice_id=invoice_id,
            payment_reference=payment_reference,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
            gateway_response=gateway_response,
            status="pending"
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        return payment
    
    @staticmethod
    def update_payment_status(
        db: Session,
        payment_id: str,
        status: str,
        gateway_response: Optional[str] = None
    ) -> Optional[Payment]:
        """Update payment status"""
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            return None
        
        payment.status = status
        if gateway_response:
            payment.gateway_response = gateway_response
        
        if status == "completed":
            payment.completed_at = datetime.now()
            
            # Update invoice status if fully paid
            invoice = payment.invoice
            if invoice.amount_due <= 0:
                BillingService.update_invoice_status(db, invoice.id, "paid", payment.payment_method)
        
        db.commit()
        db.refresh(payment)
        return payment
    
    @staticmethod
    def get_all_payments(
        db: Session,
        status: Optional[str] = None,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Payment]:
        """Get all payments with optional filters"""
        query = db.query(Payment)
        
        if status:
            query = query.filter(Payment.status == status)
        
        if start_date:
            query = query.filter(Payment.created_at >= start_date)
        
        if end_date:
            query = query.filter(Payment.created_at < end_date)
        
        return query.order_by(desc(Payment.created_at)).limit(limit).all()
    
    @staticmethod
    def get_invoice_payments(db: Session, invoice_id: str) -> List[Payment]:
        """Get all payments for an invoice"""
        return db.query(Payment).filter(Payment.invoice_id == invoice_id).all()
    
    @staticmethod
    def get_revenue_summary(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get revenue summary for date range
        """
        if not start_date:
            # Get current IST time by adding 5.5 hours to UTC
            now = datetime.utcnow()
            ist_offset = timedelta(hours=5, minutes=30)
            ist_now = now + ist_offset
            start_date = ist_now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if not end_date:
            end_date = start_date + timedelta(days=1)
        
        # Get invoices in date range
        invoices = db.query(Invoice).filter(
            and_(
                Invoice.created_at >= start_date,
                Invoice.created_at < end_date
            )
        ).all()
        
        # Calculate metrics
        total_revenue = 0.0
        total_orders = 0
        paid_invoices = 0
        pending_invoices = 0
        
        payment_breakdown = {
            "cash": 0.0,
            "card": 0.0,
            "upi": 0.0,
            "other": 0.0
        }
        
        for invoice in invoices:
            # Only count revenue from PAID invoices
            if invoice.status == "paid":
                total_revenue += invoice.total_amount
                # Payment method breakdown only for paid invoices
                if invoice.payment_method:
                    method = invoice.payment_method.lower()
                    if method in payment_breakdown:
                        payment_breakdown[method] += invoice.total_amount
                    else:
                        payment_breakdown["other"] += invoice.total_amount
            
            if invoice.order_id:
                total_orders += 1
            
            if invoice.status == "paid":
                paid_invoices += 1
            else:
                pending_invoices += 1
        
        # Calculate growth rate (compare with previous period)
        growth_rate = 0.0
        
        if start_date and end_date:
            # Calculate previous period (same duration)
            duration = end_date - start_date
            prev_start = start_date - duration
            prev_end = start_date
            
            # Get previous period revenue
            prev_invoices = db.query(Invoice).filter(
                and_(
                    Invoice.created_at >= prev_start,
                    Invoice.created_at < prev_end,
                    Invoice.status == "paid"
                )
            ).all()
            
            prev_revenue = sum(inv.total_amount for inv in prev_invoices)
            
            if prev_revenue > 0:
                growth_rate = ((total_revenue - prev_revenue) / prev_revenue) * 100
        
        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "summary": {
                "total_revenue": float(total_revenue),
                "total_orders": total_orders,
                "total_invoices": len(invoices),
                "paid_invoices": paid_invoices,
                "pending_invoices": pending_invoices,
                "growth_rate": growth_rate
            },
            "payment_breakdown": {
                method: float(amount) for method, amount in payment_breakdown.items()
            }
        }
    
    @staticmethod
    def get_daily_revenue(db: Session, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily revenue for the last N days"""
        daily_revenue = []
        
        # Get current IST time by adding 5.5 hours to UTC
        now = datetime.utcnow()
        ist_offset = timedelta(hours=5, minutes=30)
        ist_now = now + ist_offset
        
        for i in range(days):
            # Calculate IST date
            ist_date = ist_now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
            
            # Convert IST date to UTC for database query
            utc_start_date = ist_date - ist_offset
            utc_end_date = ist_date + timedelta(days=1) - ist_offset
            
            summary = BillingService.get_revenue_summary(db, utc_start_date, utc_end_date)
            
            daily_revenue.append({
                "date": ist_date.strftime("%Y-%m-%d"),
                "revenue": summary["summary"]["total_revenue"],
                "orders": summary["summary"]["total_orders"],
                "invoices": summary["summary"]["total_invoices"]
            })
        
        return list(reversed(daily_revenue))  # Most recent first
    
    @staticmethod
    def get_overdue_invoices(db: Session) -> List[Invoice]:
        """Get all overdue invoices"""
        return db.query(Invoice).filter(
            and_(
                Invoice.status == "pending",
                Invoice.due_date < datetime.now()
            )
        ).all()
    
    @staticmethod
    def get_customer_billing_summary(db: Session, customer_id: int) -> Dict[str, Any]:  # Changed to int
        """Get billing summary for a customer"""
        invoices = BillingService.get_customer_invoices(db, customer_id)
        
        total_invoiced = sum(invoice.total_amount for invoice in invoices)
        total_paid = sum(invoice.total_amount for invoice in invoices if invoice.status == "paid")
        total_pending = sum(invoice.total_amount for invoice in invoices if invoice.status == "pending")
        
        return {
            "customer_id": customer_id,
            "total_invoices": len(invoices),
            "total_invoiced": float(total_invoiced),
            "total_paid": float(total_paid),
            "total_pending": float(total_pending),
            "last_invoice": invoices[0].created_at.isoformat() if invoices else None
        }
