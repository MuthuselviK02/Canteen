import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { useAuth } from '@/contexts/AuthContext';
import {

  IndianRupee, 
  CreditCard, 
  Smartphone, 
  Wallet, 
  CheckCircle,
  Clock,
  Receipt,
  ArrowRight
} from 'lucide-react';
import { API_URL, buildApiUrl, buildImageUrl } from '@/utils/api';
import { toast } from 'sonner';

interface OrderBillingProps {
  order: any;
  cartItems: any[];
  totalAmount: number;
  onPaymentComplete: (paymentMethod: string) => void;
  onClose: () => void;
}

export default function OrderBilling({ 
  order, 
  cartItems, 
  totalAmount, 
  onPaymentComplete, 
  onClose 
}: OrderBillingProps) {
  const { user } = useAuth();
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [paymentStep, setPaymentStep] = useState<'select' | 'processing' | 'complete'>('select');

  const taxRate = 18; // 18% tax
  const taxAmount = totalAmount * (taxRate / 100);
  const finalAmount = totalAmount + taxAmount;

  const paymentMethods = [
    {
      id: 'cash',
      name: 'Cash',
      icon: <IndianRupee className="w-5 h-5" />,
      description: 'Pay with cash at counter',
      color: 'bg-green-50 border-green-200 text-green-700'
    },
    {
      id: 'card',
      name: 'Credit/Debit Card',
      icon: <CreditCard className="w-5 h-5" />,
      description: 'Pay with card at counter',
      color: 'bg-blue-50 border-blue-200 text-blue-700'
    },
    {
      id: 'upi',
      name: 'UPI',
      icon: <Smartphone className="w-5 h-5" />,
      description: 'Pay with UPI apps',
      color: 'bg-purple-50 border-purple-200 text-purple-700'
    },
    {
      id: 'wallet',
      name: 'Digital Wallet',
      icon: <Wallet className="w-5 h-5" />,
      description: 'Pay with digital wallet',
      color: 'bg-orange-50 border-orange-200 text-orange-700'
    }
  ];

  const handlePayment = async (method: string) => {
    if (!cartItems.length) {
      toast.error('Cannot create an invoice for an empty order');
      return;
    }

    setSelectedPaymentMethod(method);
    setIsProcessing(true);
    setPaymentStep('processing');

    try {
      const token = localStorage.getItem('canteen_token');
      if (!token) {
        toast.error('Authentication required');
        setIsProcessing(false);
        setPaymentStep('select');
        return;
      }

      const customerId = order?.customer_id ?? order?.userId ?? user?.id;
      if (!customerId) {
        toast.error('Customer not found. Please login again.');
        setIsProcessing(false);
        setPaymentStep('select');
        return;
      }

      const parsedOrderId = order?.id ? parseInt(String(order.id), 10) : undefined;
      const orderId = Number.isFinite(parsedOrderId) ? parsedOrderId : undefined;

      const invoiceData = {
        customer_id: customerId,
        order_id: orderId,
        customer_name: order?.customer_name || user?.fullname || 'Customer',
        customer_email: order?.customer_email || user?.email || '',
        customer_phone: order?.customer_phone || '',
        items: cartItems.map(item => ({
          name: item.menuItem.name,
          price: item.menuItem.price,
          quantity: item.quantity,
          description: item.menuItem.description
        })),
        notes: order.id ? `Order ORD-${String(order.id).padStart(6, '0')} - ${cartItems.length} items` : `New order - ${cartItems.length} items`,
        payment_method: method,
        subtotal: totalAmount,
        tax_amount: taxAmount,
        total_amount: finalAmount
      };

      const response = await fetch(buildApiUrl('/api/billing/invoices'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(invoiceData)
      });

      if (!response.ok) {
        const errorPayload = await response.json().catch(() => null);
        const message = (errorPayload && (errorPayload.detail || errorPayload.message)) || 'Failed to create invoice';
        throw new Error(message);
      }

      const invoice = await response.json();

      // Keep the user flow lightweight here: create the invoice and let admin
      // confirm payment from the billing dashboard.
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setPaymentStep('complete');
      onPaymentComplete(method);
      
      toast.success(`Invoice created successfully: ${invoice.invoice_number}`);
      
      // Auto close after success
      setTimeout(() => {
        onClose();
      }, 3000);
    } catch (error) {
      console.error('Payment error:', error);
      toast.error(error instanceof Error ? error.message : 'Payment failed. Please try again.');
      setIsProcessing(false);
      setPaymentStep('select');
    }
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Receipt className="w-5 h-5" />
            Order Billing & Payment
          </DialogTitle>
          <DialogDescription>
            Review your order summary and choose how you plan to pay so we can generate the invoice for admin review.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Order Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Order Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Order ID:</span>
                  <Badge variant="outline">
                    {order.id ? `ORD-${String(order.id).padStart(6, '0')}` : "Generating..."}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Items:</span>
                  <span className="font-medium">{cartItems.length} items</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Estimated Time:</span>
                  <span className="font-medium flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {order.predicted_wait_time || 15} mins
                  </span>
                </div>
              </div>

              {/* Items List */}
              <div className="mt-4 space-y-2">
                {cartItems.map((item, index) => (
                  <div key={index} className="flex justify-between items-center py-2 border-b">
                    <div>
                      <span className="font-medium">{item.menuItem.name}</span>
                      <span className="text-sm text-gray-500 ml-2">x{item.quantity}</span>
                    </div>
                    <span className="font-medium">
                      ₹{(item.menuItem.price * item.quantity).toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>

              {/* Bill Calculation */}
              <div className="mt-4 space-y-2 pt-4 border-t">
                <div className="flex justify-between">
                  <span className="text-gray-600">Subtotal:</span>
                  <span>₹{totalAmount.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Tax (18%):</span>
                  <span>₹{taxAmount.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-lg font-bold">
                  <span>Total Amount:</span>
                  <span className="text-primary">₹{finalAmount.toFixed(2)}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Payment Method Selection */}
          {paymentStep === 'select' && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Select Payment Method</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {paymentMethods.map((method) => (
                    <button
                      key={method.id}
                      onClick={() => handlePayment(method.id)}
                      disabled={isProcessing}
                      className={`p-4 rounded-lg border-2 transition-all hover:shadow-md ${method.color} ${
                        selectedPaymentMethod === method.id ? 'ring-2 ring-offset-2 ring-primary' : ''
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        {method.icon}
                        <div className="text-left">
                          <div className="font-medium">{method.name}</div>
                          <div className="text-xs opacity-75">{method.description}</div>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Creating Invoice */}
          {paymentStep === 'processing' && (
            <Card>
              <CardContent className="py-8">
                <div className="text-center space-y-4">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                  <h3 className="text-lg font-medium">Creating Invoice...</h3>
                  <p className="text-gray-600">Please wait while we prepare your invoice for admin confirmation</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Invoice Created */}
          {paymentStep === 'complete' && (
            <Card>
              <CardContent className="py-8">
                <div className="text-center space-y-4">
                  <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
                  <h3 className="text-xl font-medium text-green-700">Invoice Created!</h3>
                  <p className="text-gray-600">Your order has been placed. Admin can mark the invoice as paid from billing.</p>
                  <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
                    <ArrowRight className="w-4 h-4" />
                    <span>Redirecting to orders...</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
