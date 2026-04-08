import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {

  FileText, 
  Plus, 
  Search, 
  Eye, 
  Edit, 
  Trash2,
  CreditCard,
  IndianRupee,
  Calendar,
  User,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  DollarSign,
  RefreshCw,
  Mail,
  Phone,
  MapPin,
  Building,
  Settings,
  Printer,
  Share2,
  ChevronDown,
  ChevronUp,
  ArrowUpRight,
  ArrowDownRight,
  Zap,
  Target,
  Award,
  Star,
  TrendingDown,
  AlertTriangle,
  Info,
  MoreHorizontal,
  Smartphone,
  Wallet
} from 'lucide-react';
import { API_URL, buildApiUrl, buildImageUrl } from '@/utils/api';
import { formatDateOnly } from '@/utils/istTime';

interface Invoice {
  id: string;
  invoice_number: string;
  customer_id: string;
  order_id?: string;
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  status: string;
  due_date?: string;
  paid_date?: string;
  notes?: string;
  payment_method?: string;
  created_at: string;
  updated_at: string;
  is_overdue: boolean;
  amount_due: number;
  customer_name?: string;
  customer_email?: string;
  customer_phone?: string;
  items?: Array<{
    name: string;
    price: number;
    quantity: number;
    description?: string;
  }>;
}

interface Payment {
  id: string;
  invoice_id: string;
  payment_reference: string;
  amount: number;
  payment_method: string;
  transaction_id?: string;
  status: string;
  gateway_response?: string;
  gateway_name?: string;
  created_at: string;
  updated_at: string;
}

interface BillingSettings {
  id: string;
  tax_rate: number;
  tax_name: string;
  currency: string;
  currency_symbol: string;
  invoice_prefix: string;
  invoice_number_length: number;
  business_name?: string;
  business_address?: string;
  business_phone?: string;
  business_email?: string;
  payment_methods: string[];
}

interface RevenueSummary {
  summary: {
    total_revenue: number;
    total_orders: number;
    total_invoices: number;
    paid_invoices: number;
    pending_invoices: number;
    average_order_value: number;
    growth_rate: number;
  };
  daily_revenue: Array<{
    date: string;
    revenue: number;
    orders: number;
  }>;
  payment_breakdown: {
    cash: number;
    card: number;
    upi: number;
    other: number;
  };
}

interface CustomerBillingSummary {
  customer_id: string;
  total_invoices: number;
  total_spent: number;
  paid_invoices: number;
  pending_invoices: number;
  overdue_invoices: number;
  average_order_value: number;
  last_invoice_date?: string;
}

interface Payment {
  invoice_id: string;
  payment_reference: string;
  amount: number;
  payment_method: string;
  transaction_id?: string;
  status: string;
  created_at: string;
  completed_at?: string;
}

interface BillingDashboard {
  total_revenue: number;
  total_invoices: number;
  paid_invoices: number;
  pending_invoices: number;
  overdue_invoices: number;
  today_revenue: number;
  today_orders: number;
  today_invoices: number;
  payment_methods: Record<string, number>;
}

export default function BillingDashboard() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [dashboard, setDashboard] = useState<BillingDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  // Fetch billing data
  const fetchBillingData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('canteen_token');
      
      const [invoicesResponse, dashboardResponse] = await Promise.all([
        fetch(buildApiUrl('/api/billing/invoices'), {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }),
        fetch(buildApiUrl('/api/billing/revenue/summary'), {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
      ]);

      if (invoicesResponse.ok && dashboardResponse.ok) {
        const invoicesData = await invoicesResponse.json();
        const dashboardData = await dashboardResponse.json();
        
        setInvoices(invoicesData);
        setDashboard({
          total_revenue: dashboardData.summary.total_revenue,
          total_invoices: dashboardData.summary.total_invoices,
          paid_invoices: dashboardData.summary.paid_invoices,
          pending_invoices: dashboardData.summary.pending_invoices,
          overdue_invoices: 0, // Will be updated separately
          today_revenue: dashboardData.summary.total_revenue, // Simplified
          today_orders: dashboardData.summary.total_orders,
          today_invoices: dashboardData.summary.total_invoices,
          payment_methods: dashboardData.payment_breakdown
        });
        
        setError(null);
      } else {
        throw new Error('Failed to fetch billing data');
      }
    } catch (err) {
      setError('Failed to load billing data');
      console.error('Error fetching billing data:', err);
    } finally {
      setLoading(false);
    }
  };

  const deleteInvoice = async (invoiceId: string) => {
    if (!window.confirm('Are you sure you want to delete this invoice?')) {
      return;
    }
    
    try {
      const token = localStorage.getItem('canteen_token');
      const response = await fetch(`buildApiUrl('/api/')billing/invoices/${invoiceId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        alert(result.message || 'Invoice deleted successfully');
        fetchBillingData(); // Refresh the data
      } else {
        const errorData = await response.json();
        alert(`Failed to delete invoice: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error deleting invoice:', error);
      alert('Error deleting invoice');
    }
  };

  useEffect(() => {
    fetchBillingData();
  }, []);

  // Filter invoices
  const filteredInvoices = invoices.filter(invoice => {
    const matchesSearch = invoice.invoice_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (invoice.notes && invoice.notes.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesStatus = statusFilter === 'all' || invoice.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  // Get status badge color
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'paid':
        return <Badge variant="default" className="bg-green-100 text-green-800">Paid</Badge>;
      case 'pending':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">Pending</Badge>;
      case 'overdue':
        return <Badge variant="destructive">Overdue</Badge>;
      case 'cancelled':
        return <Badge variant="outline" className="bg-gray-100 text-gray-800">Cancelled</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  // Get payment method icon
  const getPaymentMethodIcon = (method: string) => {
    switch (method?.toLowerCase()) {
      case 'card':
        return <CreditCard className="h-4 w-4" />;
      case 'cash':
        return <IndianRupee className="h-4 w-4" />;
      case 'upi':
        return <CreditCard className="h-4 w-4" />;
      default:
        return <CreditCard className="h-4 w-4" />;
    }
  };

  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  // Format date
  const formatDate = (dateString: string) => {
    return formatDateOnly(dateString);
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Unable to load billing data</h3>
          <p className="text-red-600 text-center">{error}</p>
          <Button onClick={fetchBillingData} className="mt-4">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Billing & Invoices</h2>
          <p className="text-gray-600 mt-1">Manage invoices, payments, and revenue tracking</p>
        </div>
        <div className="flex gap-2">
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Invoice
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>Create New Invoice</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="customer">Customer ID</Label>
                  <Input id="customer" type="number" placeholder="Enter customer ID (e.g., 1)" />
                </div>
                <div>
                  <Label htmlFor="amount">Amount</Label>
                  <Input id="amount" type="number" placeholder="0.00" />
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea id="description" placeholder="Invoice description" />
                </div>
                <div>
                  <Label htmlFor="payment-method">Payment Method</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select payment method" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="cash">Cash</SelectItem>
                      <SelectItem value="card">Card</SelectItem>
                      <SelectItem value="upi">UPI</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex gap-2 pt-4">
                  <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                    Cancel
                  </Button>
                  <Button className="flex-1">
                    Create Invoice
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Dashboard Overview */}
      {dashboard && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(dashboard.total_revenue)}</div>
              <p className="text-xs text-muted-foreground">
                {dashboard.paid_invoices} paid invoices
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Invoices</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboard.total_invoices}</div>
              <p className="text-xs text-muted-foreground">
                {dashboard.pending_invoices} pending
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Today's Revenue</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(dashboard.today_revenue)}</div>
              <p className="text-xs text-muted-foreground">
                {dashboard.today_invoices} invoices today
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending Payments</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboard.pending_invoices}</div>
              <p className="text-xs text-muted-foreground">
                Awaiting payment
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Invoices Table */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Invoices</CardTitle>
            <div className="flex gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search invoices..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="paid">Paid</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="overdue">Overdue</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Invoice #</th>
                  <th className="text-left p-2">Customer</th>
                  <th className="text-left p-2">Amount</th>
                  <th className="text-left p-2">Status</th>
                  <th className="text-left p-2">Payment Method</th>
                  <th className="text-left p-2">Due Date</th>
                  <th className="text-left p-2">Created</th>
                  <th className="text-left p-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredInvoices.map((invoice) => (
                  <tr key={invoice.id} className="border-b hover:bg-gray-50">
                    <td className="p-2 font-medium">{invoice.invoice_number}</td>
                    <td className="p-2">
                      <div className="flex items-center gap-2">
                        <User className="h-4 w-4 text-gray-400" />
                        <span>{invoice.customer_id.slice(0, 8)}...</span>
                      </div>
                    </td>
                    <td className="p-2 font-medium">{formatCurrency(invoice.total_amount)}</td>
                    <td className="p-2">{getStatusBadge(invoice.status)}</td>
                    <td className="p-2">
                      {invoice.payment_method && (
                        <div className="flex items-center gap-1">
                          {getPaymentMethodIcon(invoice.payment_method)}
                          <span className="text-sm">{invoice.payment_method}</span>
                        </div>
                      )}
                    </td>
                    <td className="p-2">
                      {invoice.due_date ? formatDate(invoice.due_date) : '-'}
                    </td>
                    <td className="p-2">{formatDate(invoice.created_at)}</td>
                    <td className="p-2">
                      <div className="flex gap-1">
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        {invoice.status === 'pending' && (
                          <Button variant="outline" size="sm" className="text-green-600">
                            <CheckCircle className="h-4 w-4" />
                          </Button>
                        )}
                        {(invoice.status === 'pending' || invoice.status === 'paid') && (
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="text-red-600" 
                            title="Delete Invoice"
                            onClick={() => deleteInvoice(invoice.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {filteredInvoices.length === 0 && (
              <div className="text-center py-8">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No invoices found</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
