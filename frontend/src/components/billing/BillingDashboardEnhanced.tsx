import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {

  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar
} from 'recharts';
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
  Users,
  ShoppingCart,
  Activity,
  BarChart3,
  PieChart,
  Filter,
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
  Wallet,
  Save
} from 'lucide-react';
import { API_URL, buildApiUrl, buildImageUrl } from '@/utils/api';
import { formatDateOnly, getCurrentISTDateForAPI, getBusinessDayForAPI, getISTDateRange } from '@/utils/istTime';
import { useAuth } from '@/contexts/AuthContext';

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
  invoice_date: string;  // Canonical business date in IST
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

const BillingDashboardEnhanced: React.FC = () => {
  const { isAdmin } = useAuth();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [allPayments, setAllPayments] = useState<Payment[]>([]);
  const [settings, setSettings] = useState<BillingSettings | null>(null);
  const [revenueSummary, setRevenueSummary] = useState<RevenueSummary | null>(null);
  const [dailyRevenue, setDailyRevenue] = useState<any[]>([]);
  const [performanceMetrics, setPerformanceMetrics] = useState<any>(null);
  
  // KPI state variables (canonical data flow)
  const [totalRevenue, setTotalRevenue] = useState<number>(0);
  const [totalInvoices, setTotalInvoices] = useState<number>(0);
  const [pendingInvoices, setPendingInvoices] = useState<number>(0);
  const [avgOrderValue, setAvgOrderValue] = useState<number>(0);
  
  // Payment method dialog state
  const [showPaymentMethodDialog, setShowPaymentMethodDialog] = useState(false);
  const [selectedInvoiceId, setSelectedInvoiceId] = useState<string | null>(null);
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState('cash');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [savingSettings, setSavingSettings] = useState(false);
  
  // Date range state
  const [dateRange, setDateRange] = useState<'today' | 'week' | 'month' | 'custom'>('today');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');

  // Debug dateRange changes
  useEffect(() => {
    console.log('DateRange changed to:', dateRange);
  }, [dateRange]);
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('all');
  const [expandedInvoice, setExpandedInvoice] = useState<string | null>(null);
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const [showViewDialog, setShowViewDialog] = useState(false);
  const [showMoreMenu, setShowMoreMenu] = useState<string | null>(null);
  
  // Manual invoice creation state
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [createInvoiceData, setCreateInvoiceData] = useState({
    customer_id: '',
    customer_name: '',
    customer_email: '',
    customer_phone: '',
    items: [{ name: '', price: 0, quantity: 1, description: '' }],
    notes: '',
    payment_method: 'cash'
  });
  const [isCreating, setIsCreating] = useState(false);
  const [createSuccess, setCreateSuccess] = useState(false);

  // Simple date formatter for invoice dates (already in IST)
  const formatInvoiceDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      const day = date.getDate();
      const month = months[date.getMonth()];
      const year = date.getFullYear();
      return `${day} ${month} ${year}`;
    } catch (error) {
      console.error('Error formatting invoice date:', error);
      return dateString;
    }
  };

  // Helper function to get date range using IST time
  const getDateRange = () => {
    // Get business day for "today" filter (more appropriate for billing)
    const businessDayStr = getBusinessDayForAPI();
    const todayStr = getCurrentISTDateForAPI(); // Keep for reference
    
    let dateRangeResult;
    switch (dateRange) {
      case 'today':
        // Use business day for today filter to show current business day invoices
        dateRangeResult = { start: businessDayStr, end: businessDayStr };
        break;
      case 'week':
        // Use IST date range for last 7 days (6 days back to include today)
        dateRangeResult = getISTDateRange(6);
        break;
      case 'month':
        // Use IST date range for last 30 days (29 days back to include today)
        dateRangeResult = getISTDateRange(29);
        break;
      case 'custom':
        dateRangeResult = { start: startDate || businessDayStr, end: endDate || businessDayStr };
        break;
      default:
        dateRangeResult = { start: businessDayStr, end: businessDayStr };
    }
    
    console.log('📅 Date Range Calculation:', {
      dateRange,
      businessDayStr,
      todayStr,
      result: dateRangeResult,
      explanation: `Filtering from ${dateRangeResult.start} to ${dateRangeResult.end}`
    });
    
    return dateRangeResult;
  };

  // Fetch data from API - combine initial load and date range changes
  useEffect(() => {
    console.log('🔄 useEffect triggered - dateRange:', dateRange, 'startDate:', startDate, 'endDate:', endDate);
    fetchBillingData();
  }, [dateRange, startDate, endDate]);

  const fetchBillingData = async () => {
    try {
      setLoading(true); // Set loading to true at the start
      const token = localStorage.getItem('canteen_token');
      if (!token) {
        setError('Authentication token not found');
        setLoading(false);
        return;
      }

      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      // Get date range
      const { start, end } = getDateRange();
      
      console.log('📅 Billing Dashboard: Fetching filtered invoices for:', {
        dateRange,
        start,
        end,
        today: new Date().toISOString().split('T')[0]
      });
      
      // PRIMARY DATA SOURCE: Fetch filtered invoices (canonical dataset)
      const invoicesRes = await fetch(buildApiUrl(`/api/billing/invoices?start_date=${start}&end_date=${end}`), { headers });
      
      if (!invoicesRes.ok) {
        throw new Error('Failed to fetch invoices');
      }
      
      const rawInvoices = await invoicesRes.json();
      const filteredInvoices = rawInvoices.filter(inv => !inv.order_id || (Array.isArray(inv.items) && inv.items.length > 0));
      
      console.log('📋 API Response Details:', {
        dateRange,
        apiParams: { start, end },
        totalInvoicesReturned: filteredInvoices.length,
        invoiceDetails: filteredInvoices.map(inv => ({
          invoice_number: inv.invoice_number,
          invoice_date: inv.invoice_date,
          status: inv.status,
          amount: inv.total_amount
        }))
      });
      
      // SECONDARY DATA: Fetch settings, payments, and analytics data (all date-filtered for consistency)
      const [settingsRes, paymentsRes, revenueRes, dailyRevenueRes, performanceRes] = await Promise.all([
        fetch(buildApiUrl('/api/billing/settings'), { headers }),
        fetch(buildApiUrl(`/api/billing/payments?start_date=${start}&end_date=${end}`), { headers }),
        fetch(buildApiUrl(`/api/billing/revenue/summary?start_date=${start}&end_date=${end}`), { headers }),
        fetch(buildApiUrl(`/api/billing/revenue/daily?days=${dateRange === 'today' ? 1 : dateRange === 'week' ? 7 : 30}`), { headers }),
        fetch(buildApiUrl(`/api/billing/performance/metrics?start_date=${start}&end_date=${end}`), { headers })
      ]);

      const settings = settingsRes.ok ? await settingsRes.json() : null;
      const payments = paymentsRes.ok ? await paymentsRes.json() : [];
      const revenueSummaryData = revenueRes.ok ? await revenueRes.json() : null;
      const dailyRevenueData = dailyRevenueRes.ok ? await dailyRevenueRes.json() : null;
      const performanceData = performanceRes.ok ? await performanceRes.json() : null;
      
      // CANONICAL KPI CALCULATIONS (from same filtered dataset)
      const paidInvoices = filteredInvoices.filter(inv => inv.status === 'paid');
      const pendingInvoices = filteredInvoices.filter(inv => inv.status === 'pending' && inv.total_amount > 0);
      
      const totalRevenue = paidInvoices.reduce((sum, inv) => sum + inv.total_amount, 0);
      const totalInvoices = filteredInvoices.length;
      const pendingCount = pendingInvoices.length;
      const avgOrderValue = paidInvoices.length > 0 ? totalRevenue / paidInvoices.length : 0;
      
      console.log('📊 KPIs from filtered dataset:', {
        totalInvoices: filteredInvoices.length,
        paidInvoices: paidInvoices.length,
        pendingCount: pendingInvoices.length,
        totalRevenue,
        avgOrderValue
      });
      
      const daysParam = dateRange === 'today' ? 1 : dateRange === 'week' ? 7 : 30;
      
      console.log('📊 Analytics Data Fetched:', {
        dateRange,
        dateParams: { start, end },
        daysParam,
        revenueSummary: revenueSummaryData ? '✅ fetched' : '❌ failed',
        dailyRevenue: dailyRevenueData ? `✅ ${dailyRevenueData.daily_revenue?.length || 0} days` : '❌ failed',
        performanceMetrics: performanceData ? '✅ fetched' : '❌ failed'
      });
      
      // Set state with canonical data
      console.log('📊 Setting state with:', {
        invoicesCount: filteredInvoices.length,
        totalRevenue,
        totalInvoices,
        pendingCount,
        avgOrderValue
      });
      setInvoices(filteredInvoices);
      setSettings(settings);
      setAllPayments(payments);
      setRevenueSummary(revenueSummaryData);
      setDailyRevenue(dailyRevenueData?.daily_revenue || dailyRevenueData || []);
      setPerformanceMetrics(performanceData);
      setTotalRevenue(totalRevenue);
      setTotalInvoices(totalInvoices);
      setPendingInvoices(pendingCount);
      setAvgOrderValue(avgOrderValue);
      setError(null);
      setLoading(false); // Set loading to false on success
      
    } catch (error) {
      console.error('Error fetching billing data:', error);
      setError('Failed to load billing data');
      setLoading(false); // Set loading to false on error
    }
  };

  // Save billing settings
  const saveSettings = async () => {
    if (!settings) return;
    
    try {
      setSavingSettings(true);
      const token = localStorage.getItem('canteen_token');
      if (!token) {
        setError('Authentication token not found');
        return;
      }

      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      const response = await fetch(buildApiUrl('/api/billing/settings'), {
        method: 'PUT',
        headers,
        body: JSON.stringify(settings)
      });

      if (response.ok) {
        const updatedSettings = await response.json();
        setSettings(updatedSettings);
        // Show success message (you could use a toast here)
        alert('Settings saved successfully!');
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (err) {
      console.error('Error saving settings:', err);
      alert('Failed to save settings');
    } finally {
      setSavingSettings(false);
    }
  };

  // Create manual invoice
  const createManualInvoice = async () => {
    console.log('Creating invoice with data:', createInvoiceData);
    
    // Validate form data
    const customerId = parseInt(createInvoiceData.customer_id);
    const hasCustomerId = !isNaN(customerId) && customerId > 0;
    const hasCustomerName = createInvoiceData.customer_name && createInvoiceData.customer_name.trim() !== '';
    const hasValidItems = createInvoiceData.items.some(item => item.name && item.name.trim() !== '' && item.price > 0);
    
    console.log('Validation:', {
      customerId,
      hasCustomerId,
      hasCustomerName,
      hasValidItems,
      items: createInvoiceData.items
    });
    
    if (!hasCustomerId || !hasCustomerName || !hasValidItems) {
      setError('Please fill in all required fields: valid Customer ID (number > 0), Customer Name, and at least one item with name and price > 0');
      return;
    }
    
    setIsCreating(true);
    try {
      const token = localStorage.getItem('canteen_token');
      if (!token) {
        setError('Authentication token not found');
        return;
      }

      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      // Calculate totals
      const subtotal = createInvoiceData.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
      const taxRate = settings?.tax_rate || 18;
      const taxAmount = subtotal * (taxRate / 100);
      const totalAmount = subtotal + taxAmount;

      const invoicePayload = {
        customer_id: parseInt(createInvoiceData.customer_id) || 0,
        customer_name: createInvoiceData.customer_name || '',
        customer_email: createInvoiceData.customer_email || '',
        customer_phone: createInvoiceData.customer_phone || '',
        items: createInvoiceData.items.filter(item => item.name && item.price > 0),
        subtotal,
        tax_amount: taxAmount,
        total_amount: totalAmount,
        notes: createInvoiceData.notes || '',
        payment_method: createInvoiceData.payment_method || 'cash'
      };

      const response = await fetch(buildApiUrl('/api/billing/invoices'), {
        method: 'POST',
        headers,
        body: JSON.stringify(invoicePayload)
      });

      if (response.ok) {
        const newInvoice = await response.json();
        console.log('Invoice created successfully:', newInvoice);
        setInvoices([newInvoice, ...invoices]);
        setCreateSuccess(true);
        setIsCreateDialogOpen(false);
        
        // Reset form
        setCreateInvoiceData({
          customer_id: '',
          customer_name: '',
          customer_email: '',
          customer_phone: '',
          items: [{ name: '', price: 0, quantity: 1, description: '' }],
          notes: '',
          payment_method: 'cash'
        });
        
        // Refresh data
        fetchBillingData();
        
        // Hide success message after 3 seconds
        setTimeout(() => setCreateSuccess(false), 3000);
      } else {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || 'Failed to create invoice';
        console.error('Invoice creation error:', errorData);
        setError(errorMessage);
        // Don't close dialog on error so user can fix issues
      }
    } catch (err) {
      setError('Failed to create invoice');
      console.error('Error creating invoice:', err);
    } finally {
      setIsCreating(false);
    }
  };

  // Add item to invoice
  const addInvoiceItem = () => {
    setCreateInvoiceData({
      ...createInvoiceData,
      items: [...createInvoiceData.items, { name: '', price: 0, quantity: 1, description: '' }]
    });
  };

  // Update invoice item
  const updateInvoiceItem = (index: number, field: string, value: any) => {
    const updatedItems = [...createInvoiceData.items];
    updatedItems[index] = { ...updatedItems[index], [field]: value };
    setCreateInvoiceData({ ...createInvoiceData, items: updatedItems });
  };

  // Remove invoice item
  const removeInvoiceItem = (index: number) => {
    if (createInvoiceData.items.length > 1) {
      setCreateInvoiceData({
        ...createInvoiceData,
        items: createInvoiceData.items.filter((_, i) => i !== index)
      });
    }
  };

  // Calculate invoice totals
  const calculateInvoiceTotals = () => {
    const subtotal = createInvoiceData.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const taxRate = settings?.tax_rate || 18;
    const taxAmount = subtotal * (taxRate / 100);
    const totalAmount = subtotal + taxAmount;
    return { subtotal, taxAmount, totalAmount };
  };

  // Quick actions for invoices
  const openPaymentMethodDialog = (invoiceId: string) => {
    console.log('Opening payment method dialog for invoice:', invoiceId);
    setSelectedInvoiceId(invoiceId);
    setSelectedPaymentMethod('cash'); // Default to cash
    setShowPaymentMethodDialog(true);
  };

  const markInvoiceAsPaid = async (invoiceId: string, paymentMethod: string) => {
    console.log('Marking invoice as paid:', { invoiceId, paymentMethod });
    try {
      const token = localStorage.getItem('canteen_token');
      if (!token) {
        console.error('No token found');
        return;
      }

      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      const requestBody = { payment_method: paymentMethod };
      console.log('Request body:', requestBody);
      console.log('Request URL:', buildApiUrl(`/api/billing/invoices/${invoiceId}/mark-paid`));

      const response = await fetch(buildApiUrl(`/api/billing/invoices/${invoiceId}/mark-paid`), {
        method: 'POST',
        headers,
        body: JSON.stringify(requestBody)
      });

      console.log('Response status:', response.status);
      const responseData = await response.json();
      console.log('Response data:', responseData);

      if (response.ok) {
        // Update local state
        setInvoices(invoices.map(inv => 
          inv.id === invoiceId 
            ? { ...inv, status: 'paid', paid_date: new Date().toISOString(), payment_method: paymentMethod }
            : inv
        ));
        fetchBillingData(); // Refresh data
        setShowPaymentMethodDialog(false);
        console.log('Invoice marked as paid successfully');
      } else {
        console.error('Failed to mark invoice as paid:', responseData);
      }
    } catch (err) {
      console.error('Error marking invoice as paid:', err);
    }
  };

  const sendPaymentReminder = async (invoiceId: string) => {
    try {
      const token = localStorage.getItem('canteen_token');
      const response = await fetch(buildApiUrl(`/api/billing/invoices/${invoiceId}/send-reminder`), {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        alert(`Payment reminder sent: ${data.message}`);
        fetchBillingData();
      } else {
        alert('Failed to send payment reminder');
      }
    } catch (error) {
      alert('Error sending payment reminder');
    }
  };

  const viewInvoice = async (invoice: Invoice) => {
    try {
      const token = localStorage.getItem('canteen_token');
      const response = await fetch(buildApiUrl(`/api/billing/invoices/${invoice.id}`), {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const invoiceDetails = await response.json();
        setSelectedInvoice(invoiceDetails);
      } else {
        setSelectedInvoice(invoice);
      }
    } catch (error) {
      console.error('Error fetching invoice details:', error);
      setSelectedInvoice(invoice);
    }

    setShowViewDialog(true);
  };

  const deleteInvoice = async (invoiceId: string) => {
    try {
      const token = localStorage.getItem('canteen_token');
      const response = await fetch(buildApiUrl(`/api/billing/invoices/${invoiceId}`), {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        alert(result.message || 'Invoice deleted successfully');
        fetchBillingData();
      } else {
        const errorData = await response.json();
        alert(`Failed to delete invoice: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error deleting invoice:', error);
      alert('Error deleting invoice. Please try again.');
    }
  };

  const fetchUserData = async (userId: string) => {
    try {
      const token = localStorage.getItem('canteen_token');
      const response = await fetch(buildApiUrl(`/api/users/${userId}`), {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const userData = await response.json();
        return userData.fullname || userData.name || `User ${userId}`; 
      }
    } catch (error) {
      console.error('Error fetching user data:', error);
    }
    return `User ${userId}`;
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'paid': return 'bg-green-100 text-green-800 border-green-200';
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'overdue': return 'bg-red-100 text-red-800 border-red-200';
      case 'cancelled': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'paid': return <CheckCircle className="w-4 h-4" />;
      case 'pending': return <Clock className="w-4 h-4" />;
      case 'overdue': return <AlertCircle className="w-4 h-4" />;
      case 'cancelled': return <AlertCircle className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  // CANONICAL DISPLAY FILTERING (uses same dataset as KPIs)
  const filteredInvoicesForDisplay = useMemo(() => {
    const filtered = invoices.filter(invoice => {
      const matchesSearch = !searchTerm || 
        invoice.invoice_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (invoice.customer_name && invoice.customer_name.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesStatus = statusFilter === 'all' || invoice.status === statusFilter;
      
      return matchesSearch && matchesStatus;
    });

    console.log('🔍 Display filtering:', {
      totalInvoicesInState: invoices.length,
      searchTerm,
      statusFilter,
      displayInvoicesCount: filtered.length
    });

    return filtered;
  }, [invoices, searchTerm, statusFilter]);

  // KPIs from canonical state (already calculated in fetchBillingData)
  const displayTotalRevenue = totalRevenue;
  const displayTotalInvoices = totalInvoices;
  const displayPendingInvoices = pendingInvoices;
  const displayAvgOrderValue = avgOrderValue;
  const growthRate = 0; // Placeholder for growth rate calculation
  const paidInvoices = displayTotalInvoices - displayPendingInvoices; // Calculate paid invoices

  // Debug: Track invoice state changes
  console.log('📋 Current invoice state:', {
    invoicesLength: invoices.length,
    totalInvoices,
    displayTotalInvoices,
    filteredInvoicesForDisplayLength: filteredInvoicesForDisplay.length,
    invoiceNumbers: invoices.map(inv => inv.invoice_number),
    filteredInvoiceNumbers: filteredInvoicesForDisplay.map(inv => inv.invoice_number)
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-600">Loading billing data...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <AlertCircle className="w-8 h-8 text-red-500" />
        <span className="ml-2 text-red-600">{error}</span>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Success Message */}
      {createSuccess && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center">
          <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
          <span className="text-green-800">Invoice created successfully!</span>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Billing Dashboard</h1>
          <p className="text-gray-600 mt-1">Manage invoices, payments, and revenue analytics</p>
          {/* UI Consistency Label */}
          <div className="mt-2 p-2 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              Showing invoices for: <span className="font-semibold">{dateRange === 'today' ? 'Today' : dateRange === 'week' ? 'Last 7 Days' : dateRange === 'month' ? 'Last 30 Days' : 'Custom Range'}</span>
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline" onClick={fetchBillingData}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                New Invoice
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Create New Invoice</DialogTitle>
              </DialogHeader>
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mx-6">
                  <div className="flex items-center">
                    <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                    <span className="text-red-800">{error}</span>
                  </div>
                </div>
              )}
              <div className="space-y-6">
                {/* Customer Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="customer_id">Customer ID *</Label>
                    <Input
                      id="customer_id"
                      type="number"
                      placeholder="Enter customer ID"
                      value={createInvoiceData.customer_id}
                      onChange={(e) => {
                        setCreateInvoiceData({...createInvoiceData, customer_id: e.target.value});
                        setError(null); // Clear error when user types
                      }}
                    />
                  </div>
                  <div>
                    <Label htmlFor="customer_name">Customer Name *</Label>
                    <Input
                      id="customer_name"
                      placeholder="Enter customer name"
                      value={createInvoiceData.customer_name}
                      onChange={(e) => {
                        setCreateInvoiceData({...createInvoiceData, customer_name: e.target.value});
                        setError(null); // Clear error when user types
                      }}
                    />
                  </div>
                  <div>
                    <Label htmlFor="customer_email">Email</Label>
                    <Input
                      id="customer_email"
                      type="email"
                      placeholder="customer@example.com"
                      value={createInvoiceData.customer_email}
                      onChange={(e) => setCreateInvoiceData({...createInvoiceData, customer_email: e.target.value})}
                    />
                  </div>
                  <div>
                    <Label htmlFor="customer_phone">Phone</Label>
                    <Input
                      id="customer_phone"
                      placeholder="+91 9876543210"
                      value={createInvoiceData.customer_phone}
                      onChange={(e) => setCreateInvoiceData({...createInvoiceData, customer_phone: e.target.value})}
                    />
                  </div>
                </div>

                {/* Invoice Items */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <Label>Invoice Items</Label>
                    <Button type="button" variant="outline" size="sm" onClick={addInvoiceItem}>
                      <Plus className="w-4 h-4 mr-2" />
                      Add Item
                    </Button>
                  </div>
                  <div className="space-y-3">
                    {createInvoiceData.items.map((item, index) => (
                      <div key={index} className="grid grid-cols-1 md:grid-cols-5 gap-3 p-3 border rounded-lg">
                        <div>
                          <Label>Item Name *</Label>
                          <Input
                            placeholder="Item name"
                            value={item.name}
                            onChange={(e) => updateInvoiceItem(index, 'name', e.target.value)}
                          />
                        </div>
                        <div>
                          <Label>Price *</Label>
                          <Input
                            type="number"
                            step="0.01"
                            placeholder="0.00"
                            value={item.price || ''}
                            onChange={(e) => updateInvoiceItem(index, 'price', parseFloat(e.target.value) || 0)}
                          />
                        </div>
                        <div>
                          <Label>Quantity *</Label>
                          <Input
                            type="number"
                            min="1"
                            placeholder="1"
                            value={item.quantity}
                            onChange={(e) => updateInvoiceItem(index, 'quantity', parseInt(e.target.value) || 1)}
                          />
                        </div>
                        <div>
                          <Label>Description</Label>
                          <Input
                            placeholder="Optional description"
                            value={item.description}
                            onChange={(e) => updateInvoiceItem(index, 'description', e.target.value)}
                          />
                        </div>
                        <div className="flex items-end">
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => removeInvoiceItem(index)}
                            disabled={createInvoiceData.items.length === 1}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Invoice Summary */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium mb-3">Invoice Summary</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Subtotal:</span>
                      <span>₹{calculateInvoiceTotals().subtotal.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Tax ({settings?.tax_rate || 18}%):</span>
                      <span>₹{calculateInvoiceTotals().taxAmount.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between font-bold text-lg">
                      <span>Total:</span>
                      <span>₹{calculateInvoiceTotals().totalAmount.toFixed(2)}</span>
                    </div>
                  </div>
                </div>

                {/* Additional Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="payment_method">Payment Method</Label>
                    <Select value={createInvoiceData.payment_method} onValueChange={(value) => setCreateInvoiceData({...createInvoiceData, payment_method: value})}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="cash">Cash</SelectItem>
                        <SelectItem value="card">Card</SelectItem>
                        <SelectItem value="upi">UPI</SelectItem>
                        <SelectItem value="net_banking">Net Banking</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="notes">Notes</Label>
                    <Textarea
                      id="notes"
                      placeholder="Additional notes for this invoice"
                      value={createInvoiceData.notes}
                      onChange={(e) => setCreateInvoiceData({...createInvoiceData, notes: e.target.value})}
                    />
                  </div>
                </div>

                {/* Actions */}
                <div className="flex justify-end space-x-3">
                  <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button 
                    onClick={createManualInvoice} 
                    disabled={isCreating || !parseInt(createInvoiceData.customer_id) || parseInt(createInvoiceData.customer_id) <= 0 || !createInvoiceData.customer_name?.trim() || !createInvoiceData.items.some(item => item.name?.trim() && item.price > 0)}
                  >
                    {isCreating ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Creating...
                      </>
                    ) : (
                      <>
                        <FileText className="w-4 h-4 mr-2" />
                        Create Invoice
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Date Range Selector */}
      <Card className="mb-6">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center">
              <Calendar className="w-5 h-5 mr-2" />
              Date Range
            </div>
            <div className="text-sm text-gray-500">
              {dateRange === 'today' && 'Today'}
              {dateRange === 'week' && 'Last 7 days'}
              {dateRange === 'month' && 'Last 30 days'}
              {dateRange === 'custom' && `${startDate} to ${endDate}`}
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="flex flex-wrap gap-2">
            <Button
              variant={dateRange === 'today' ? 'default' : 'outline'}
              size="sm"
              onClick={() => {
                console.log('Today button clicked, setting dateRange to today');
                setDateRange('today');
              }}
            >
              Today
            </Button>
            <Button
              variant={dateRange === 'week' ? 'default' : 'outline'}
              size="sm"
              onClick={() => {
                console.log('Week button clicked, setting dateRange to week');
                setDateRange('week');
              }}
            >
              Last 7 Days
            </Button>
            <Button
              variant={dateRange === 'month' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setDateRange('month')}
            >
              Last 30 Days
            </Button>
            <Button
              variant={dateRange === 'custom' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setDateRange('custom')}
            >
              Custom
            </Button>
            
            {dateRange === 'custom' && (
              <div className="flex gap-2 ml-4">
                <Input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-auto"
                />
                <span className="self-center">to</span>
                <Input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-auto"
                />
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium flex items-center">
              <DollarSign className="w-5 h-5 mr-2" />
              Total Revenue
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">₹{displayTotalRevenue.toLocaleString()}</div>
            {displayTotalInvoices > 0 && (
              <div className="flex items-center mt-2 text-blue-100">
                {growthRate >= 0 ? (
                  <ArrowUpRight className="w-4 h-4 mr-1" />
                ) : (
                  <ArrowDownRight className="w-4 h-4 mr-1" />
                )}
                <span className="text-sm">
                  {growthRate >= 0 ? '+' : ''}{growthRate.toFixed(1)}% from last month
                </span>
              </div>
            )}
            {displayTotalInvoices === 0 && (
              <div className="flex items-center mt-2 text-gray-400">
                <span className="text-sm">No paid invoices yet</span>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium flex items-center">
              <FileText className="w-5 h-5 mr-2" />
              Total Invoices
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{displayTotalInvoices}</div>
            <div className="flex items-center mt-2 text-green-100">
              <CheckCircle className="w-4 h-4 mr-1" />
              <span className="text-sm">{displayTotalInvoices - displayPendingInvoices} paid</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-yellow-500 to-yellow-600 text-white">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium flex items-center">
              <Clock className="w-5 h-5 mr-2" />
              Pending
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{pendingInvoices}</div>
            <div className="flex items-center mt-2 text-yellow-100">
              <AlertTriangle className="w-4 h-4 mr-1" />
              <span className="text-sm">Awaiting payment</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-medium flex items-center">
              <ShoppingCart className="w-5 h-5 mr-2" />
              Avg Order Value
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">₹{displayAvgOrderValue.toFixed(0)}</div>
            {paidInvoices > 0 ? (
              <div className="flex items-center mt-2 text-purple-100">
                <TrendingUp className="w-4 h-4 mr-1" />
                <span className="text-sm">Per paid transaction</span>
              </div>
            ) : (
              <div className="flex items-center mt-2 text-gray-400">
                <span className="text-sm">No paid transactions</span>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="invoices" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="invoices">Invoices</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="payments">Payments</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Invoices Tab */}
        <TabsContent value="invoices" className="space-y-6">
          {/* Filters */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Filter className="w-5 h-5 mr-2" />
                Filters
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-4">
                <div className="flex-1 min-w-[200px]">
                  <Label htmlFor="search">Search</Label>
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      id="search"
                      placeholder="Search invoices..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <div className="min-w-[150px]">
                  <Label htmlFor="status">Status</Label>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Status" />
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
            </CardContent>
          </Card>

          {/* Invoices List */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center">
                  <FileText className="w-4 h-4 mr-2" />
                  Invoices ({filteredInvoicesForDisplay.length})
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredInvoicesForDisplay.map((invoice) => (
                  <div key={invoice.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(invoice.status)}
                          <span className="font-medium">{invoice.invoice_number}</span>
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <User className="w-4 h-4" />
                          <span>{invoice.customer_name || invoice.customer_email || `User ${invoice.customer_id}`}</span>
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <Calendar className="w-4 h-4" />
                          <span>{formatInvoiceDate(invoice.invoice_date)}</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <div className="font-semibold">₹{invoice.total_amount.toFixed(2)}</div>
                          <Badge className={getStatusColor(invoice.status)}>
                            {invoice.status}
                          </Badge>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => setExpandedInvoice(expandedInvoice === invoice.id ? null : invoice.id)}
                          >
                            {expandedInvoice === invoice.id ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                          </Button>
                          <div className="flex items-center gap-1">
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => viewInvoice(invoice)}
                            title="View Invoice"
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          {isAdmin && invoice.status === 'pending' && (
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              onClick={() => openPaymentMethodDialog(invoice.id)}
                              className="text-green-600 hover:text-green-700"
                              title="Mark as Paid"
                            >
                              <CheckCircle className="w-4 h-4" />
                            </Button>
                          )}
                          {(invoice.status === 'pending' || invoice.status === 'overdue') && (
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              onClick={() => sendPaymentReminder(invoice.id)}
                              className="text-blue-600 hover:text-blue-700"
                              title="Send Reminder"
                            >
                              <Mail className="w-4 h-4" />
                            </Button>
                          )}
                          <div className="relative">
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              onClick={() => setShowMoreMenu(showMoreMenu === invoice.id ? null : invoice.id)}
                              title="More Options"
                            >
                              <MoreHorizontal className="w-4 h-4" />
                            </Button>
                            {showMoreMenu === invoice.id && (
                              <div className="absolute right-0 top-8 bg-white border border-gray-200 rounded-md shadow-lg z-10 min-w-[120px]">
                                <button
                                  onClick={() => {
                                    deleteInvoice(invoice.id);
                                    setShowMoreMenu(null);
                                  }}
                                  className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                                >
                                  <Trash2 className="w-4 h-4" />
                                  Delete
                                </button>
                              </div>
                            )}
                          </div>
                        </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Expandable Details */}
                    {expandedInvoice === invoice.id && (
                      <div className="mt-4 pt-4 border-t">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-gray-600">Subtotal:</span>
                            <div className="font-medium">₹{invoice.subtotal.toFixed(2)}</div>
                          </div>
                          <div>
                            <span className="text-gray-600">Tax:</span>
                            <div className="font-medium">₹{invoice.tax_amount.toFixed(2)}</div>
                          </div>
                          <div>
                            <span className="text-gray-600">Discount:</span>
                            <div className="font-medium">₹{invoice.discount_amount.toFixed(2)}</div>
                          </div>
                          <div>
                            <span className="text-gray-600">Payment Method:</span>
                            <div className="font-medium">{invoice.payment_method || 'N/A'}</div>
                          </div>
                        </div>
                        {invoice.notes && (
                          <div className="mt-3">
                            <span className="text-gray-600">Notes:</span>
                            <div className="text-sm mt-1">{invoice.notes}</div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
                
                {filteredInvoicesForDisplay.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p>No invoices found</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Revenue Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center">
                    <BarChart3 className="w-5 h-5 mr-2" />
                    Revenue Trend
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {dailyRevenue.length > 0 ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={dailyRevenue}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="date" 
                        tickFormatter={(value) => {
                          const date = new Date(value);
                          return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                        }}
                      />
                      <YAxis 
                        domain={[0, 'dataMax + 1000']}
                        tickFormatter={(value) => `₹${value}`}
                      />
                      <Tooltip 
                        formatter={(value: any) => [`₹${value}`, 'Revenue']}
                        labelFormatter={(label) => {
                          const date = new Date(label);
                          return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
                        }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="revenue" 
                        stroke="#3b82f6" 
                        strokeWidth={2}
                        dot={{ fill: '#3b82f6', r: 6 }}
                        activeDot={{ r: 8 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-64 flex items-center justify-center text-gray-500">
                    <div className="text-center">
                      <BarChart3 className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                      <p>No revenue data available</p>
                      <p className="text-sm">Revenue trends will appear here once invoices are paid</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Payment Methods Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center">
                    <PieChart className="w-5 h-5 mr-2" />
                    Payment Methods Distribution
                  </div>
                  <div className="text-sm text-gray-500">
                    {paidInvoices} paid transactions
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {paidInvoices > 0 ? (
                  <div className="space-y-4">
                    {[
                      { name: 'Cash', amount: revenueSummary?.payment_breakdown?.cash || 0, color: 'bg-green-500', icon: <IndianRupee className="w-4 h-4" /> },
                      { name: 'Card', amount: revenueSummary?.payment_breakdown?.card || 0, color: 'bg-blue-500', icon: <CreditCard className="w-4 h-4" /> },
                      { name: 'UPI', amount: revenueSummary?.payment_breakdown?.upi || 0, color: 'bg-purple-500', icon: <Smartphone className="w-4 h-4" /> },
                      { name: 'Other', amount: revenueSummary?.payment_breakdown?.other || 0, color: 'bg-gray-500', icon: <Wallet className="w-4 h-4" /> }
                    ].map((method) => {
                      const total = revenueSummary?.payment_breakdown ? 
                        Object.values(revenueSummary.payment_breakdown).reduce((a, b) => a + b, 0) : 1;
                      const percentage = total > 0 ? (method.amount / total * 100).toFixed(1) : 0;
                    
                    return (
                      <div key={method.name} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className={`w-3 h-3 ${method.color} rounded-full mr-2`}></div>
                            <span className="flex items-center gap-1">
                              {method.icon}
                              {method.name}
                            </span>
                          </div>
                          <div className="text-right">
                            <div className="font-medium">₹{method.amount.toLocaleString()}</div>
                            <div className="text-sm text-gray-500">{percentage}%</div>
                          </div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`${method.color} h-2 rounded-full transition-all duration-300`}
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
                ) : (
                  <div className="text-center py-8">
                    <PieChart className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500">No payment data available</p>
                    <p className="text-sm text-gray-400">Payment methods will appear here once invoices are paid</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Performance Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center">
                  <Activity className="w-5 h-5 mr-2" />
                  Performance Metrics
                </div>
                <div className="flex items-center text-sm text-gray-500">
                  <Award className="w-4 h-4 mr-1" />
                  This month
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-full mx-auto mb-2">
                    <TrendingUp className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="text-2xl font-bold text-blue-600">
                    {growthRate >= 0 ? '+' : ''}{growthRate.toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">Revenue Growth</div>
                  <div className={`text-xs mt-1 ${growthRate >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {growthRate >= 0 ? '↑' : '↓'} vs last month
                  </div>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-full mx-auto mb-2">
                    <Users className="w-6 h-6 text-green-600" />
                  </div>
                  <div className="text-2xl font-bold text-green-600">
                    {totalInvoices > 0 ? ((paidInvoices / totalInvoices) * 100).toFixed(1) : 0}%
                  </div>
                  <div className="text-sm text-gray-600">Payment Rate</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {paidInvoices} of {totalInvoices} invoices paid
                  </div>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center w-12 h-12 bg-orange-100 rounded-full mx-auto mb-2">
                    <FileText className="w-6 h-6 text-orange-600" />
                  </div>
                  <div className="text-2xl font-bold text-orange-600">{pendingInvoices}</div>
                  <div className="text-sm text-gray-600">Pending Payments</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {pendingInvoices > 0 ? 'Need attention' : 'All caught up'}
                  </div>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-full mx-auto mb-2">
                    <Target className="w-6 h-6 text-purple-600" />
                  </div>
                  <div className="text-2xl font-bold text-purple-600">₹{displayAvgOrderValue.toFixed(0)}</div>
                  <div className="text-sm text-gray-600">Avg Order Value</div>
                  <div className="text-xs text-gray-500 mt-1">
                    Per paid transaction
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Payments Tab */}
        <TabsContent value="payments" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center">
                  <CreditCard className="w-5 h-5 mr-2" />
                  Recent Payments
                </div>
                <div className="text-sm text-gray-500">
                  {allPayments.length} transactions
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {allPayments.length > 0 ? (
                <div className="space-y-4">
                  {allPayments.map((payment) => (
                    <div key={payment.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center justify-center w-10 h-10 bg-blue-100 rounded-full">
                          <CreditCard className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <div className="font-medium">{payment.payment_reference}</div>
                          <div className="text-sm text-gray-500">
                            {payment.payment_method} • {formatDateOnly(payment.created_at)}
                          </div>
                          {payment.transaction_id && (
                            <div className="text-xs text-gray-400">Transaction: {payment.transaction_id}</div>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium">₹{payment.amount}</div>
                        <div className="text-sm">
                          <Badge 
                            variant={payment.status === 'completed' ? 'default' : 
                                   payment.status === 'pending' ? 'secondary' : 'destructive'}
                          >
                            {payment.status}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <CreditCard className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>No payments found</p>
                  <p className="text-sm">Payments will appear here once transactions are processed</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Settings className="w-5 h-5 mr-2" />
                Billing Settings
              </CardTitle>
            </CardHeader>
            <CardContent>
              {settings && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <Label htmlFor="tax_rate">Tax Rate (%)</Label>
                      <Input
                        id="tax_rate"
                        type="number"
                        value={settings.tax_rate}
                        onChange={(e) => setSettings({...settings, tax_rate: parseFloat(e.target.value)})}
                      />
                    </div>
                    <div>
                      <Label htmlFor="currency">Currency</Label>
                      <Select value={settings.currency} onValueChange={(value) => setSettings({...settings, currency: value})}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="INR">INR (₹)</SelectItem>
                          <SelectItem value="USD">USD ($)</SelectItem>
                          <SelectItem value="EUR">EUR (€)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="invoice_prefix">Invoice Prefix</Label>
                      <Input
                        id="invoice_prefix"
                        value={settings.invoice_prefix}
                        onChange={(e) => setSettings({...settings, invoice_prefix: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label htmlFor="business_name">Business Name</Label>
                      <Input
                        id="business_name"
                        value={settings.business_name || ''}
                        onChange={(e) => setSettings({...settings, business_name: e.target.value})}
                      />
                    </div>
                  </div>
                  <div className="flex justify-end">
                    <Button 
                      onClick={saveSettings} 
                      disabled={savingSettings}
                      className="min-w-[120px]"
                    >
                      {savingSettings ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                          Saving...
                        </>
                      ) : (
                        <>
                          <Save className="w-4 h-4 mr-2" />
                          Save Settings
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* View Invoice Dialog */}
      <Dialog open={showViewDialog} onOpenChange={setShowViewDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Invoice Details</DialogTitle>
          </DialogHeader>
          {selectedInvoice && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Invoice Number</Label>
                  <div className="font-medium">{selectedInvoice.invoice_number}</div>
                </div>
                <div>
                  <Label>Status</Label>
                  <Badge className={getStatusColor(selectedInvoice.status)}>
                    {selectedInvoice.status}
                  </Badge>
                </div>
                <div>
                  <Label>Customer</Label>
                  <div className="font-medium">{selectedInvoice.customer_name || selectedInvoice.customer_email || `User ${selectedInvoice.customer_id}`}</div>
                </div>
                <div>
                  <Label>Created Date</Label>
                  <div className="font-medium">{formatInvoiceDate(selectedInvoice.invoice_date)}</div>
                </div>
              </div>
              
              <div className="border-t pt-4">
                <h4 className="font-medium mb-2">Invoice Items</h4>
                {selectedInvoice.items && selectedInvoice.items.length > 0 ? (
                  <div className="space-y-2">
                    {selectedInvoice.items.map((item, index) => (
                      <div key={index} className="flex justify-between p-2 bg-gray-50 rounded">
                        <div>
                          <div className="font-medium">{item.name}</div>
                          <div className="text-sm text-gray-600">{item.description}</div>
                          <div className="text-sm">Qty: {item.quantity}</div>
                        </div>
                        <div className="font-medium">₹{(item.price * item.quantity).toFixed(2)}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-gray-500">No items found</div>
                )}
              </div>
              
              <div className="border-t pt-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Subtotal:</span>
                    <span>₹{selectedInvoice.subtotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Tax:</span>
                    <span>₹{selectedInvoice.tax_amount.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Discount:</span>
                    <span>₹{selectedInvoice.discount_amount.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between font-bold text-lg">
                    <span>Total:</span>
                    <span>₹{selectedInvoice.total_amount.toFixed(2)}</span>
                  </div>
                </div>
              </div>
              
              {selectedInvoice.notes && (
                <div>
                  <Label>Notes</Label>
                  <div className="text-sm bg-gray-50 p-2 rounded">{selectedInvoice.notes}</div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Payment Method Selection Dialog */}
      <Dialog open={showPaymentMethodDialog} onOpenChange={setShowPaymentMethodDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Select Payment Method</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="payment_method">Payment Method</Label>
              <Select value={selectedPaymentMethod} onValueChange={setSelectedPaymentMethod}>
                <SelectTrigger>
                  <SelectValue placeholder="Select payment method" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cash">
                    <div className="flex items-center gap-2">
                      <DollarSign className="w-4 h-4" />
                      Cash
                    </div>
                  </SelectItem>
                  <SelectItem value="card">
                    <div className="flex items-center gap-2">
                      <CreditCard className="w-4 h-4" />
                      Card
                    </div>
                  </SelectItem>
                  <SelectItem value="upi">
                    <div className="flex items-center gap-2">
                      <Smartphone className="w-4 h-4" />
                      UPI
                    </div>
                  </SelectItem>
                  <SelectItem value="other">
                    <div className="flex items-center gap-2">
                      <Wallet className="w-4 h-4" />
                      Other
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowPaymentMethodDialog(false)}>
                Cancel
              </Button>
              <Button 
                onClick={() => selectedInvoiceId && markInvoiceAsPaid(selectedInvoiceId, selectedPaymentMethod)}
                className="bg-green-600 hover:bg-green-700"
              >
                Mark as Paid
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default BillingDashboardEnhanced;
