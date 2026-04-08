import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Shield, ShoppingBag, Clock, IndianRupee, TrendingUp, LogOut, BarChart3, Brain, FileText, ArrowUp, ArrowDown, Minus, RefreshCw } from 'lucide-react';
import { UserManagement } from '@/components/admin/UserManagement';
import { MenuManagement } from '@/components/admin/MenuManagement';
import HistoricalAnalyticsDashboard from '@/components/analytics/HistoricalAnalyticsDashboard';
import PredictiveAnalyticsDashboardRefactored from '@/components/analytics/PredictiveAnalyticsDashboardRefactored';
import PredictiveAIDashboard from '@/components/analytics/PredictiveAIDashboardNew';
import BillingDashboardEnhanced from '@/components/billing/BillingDashboardEnhanced';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ProfileButton } from '@/components/ui/Profile';
import { toast } from 'sonner';
import { API_URL, buildApiUrl, buildImageUrl } from '@/utils/api';

export default function Admin() {
  const { user, logout, isSuperAdmin } = useAuth();
  const navigate = useNavigate();
  const [kpiData, setKpiData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Fetch KPI data
  const fetchKpiData = async () => {
    try {
      const token = localStorage.getItem('canteen_token');
      if (!token) {
        toast.error('Authentication token not found');
        return;
      }

      const response = await fetch(`${API_URL}/api/admin/kpi/daily`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setKpiData(data);
      } else {
        toast.error('Failed to fetch KPI data');
      }
    } catch (error) {
      console.error('Error fetching KPI data:', error);
      toast.error('Error fetching KPI data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKpiData();
    // Refresh KPI data every 5 minutes
    const interval = setInterval(fetchKpiData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleRefresh = () => {
    // Refresh KPI data
    fetchKpiData();
    // Show toast notification
    toast.success('Dashboard refreshed!');
    // Optionally refresh the entire page after a short delay
    setTimeout(() => {
      window.location.reload();
    }, 500);
  };

  // Format KPI stats with change indicators
  const getKpiStats = () => {
    if (!kpiData) return [];

    const { today, changes } = kpiData;

    const formatChange = (change: any) => {
      const { value, percentage, trend } = change;
      const isPositive = trend === 'up';
      const isNeutral = trend === 'neutral';
      
      let icon = Minus;
      let colorClass = 'text-gray-500';
      
      if (!isNeutral) {
        icon = isPositive ? ArrowUp : ArrowDown;
        colorClass = isPositive ? 'text-green-500' : 'text-red-500';
      }

      return {
        icon,
        colorClass,
        text: `${isPositive ? '+' : ''}${percentage.toFixed(1)}%`,
        show: !isNeutral
      };
    };

    return [
      {
        label: 'Total Orders',
        value: today.total_orders,
        icon: ShoppingBag,
        color: 'text-primary',
        change: formatChange(changes.total_orders)
      },
      {
        label: 'Revenue',
        value: `₹${today.revenue.toFixed(2)}`,
        icon: IndianRupee,
        color: 'text-secondary',
        change: formatChange(changes.revenue)
      },
      {
        label: 'Avg. Wait Time',
        value: `${today.avg_wait_time} min`,
        icon: Clock,
        color: 'text-blue-500',
        change: formatChange(changes.avg_wait_time)
      },
      {
        label: 'Active Orders',
        value: today.active_orders,
        icon: TrendingUp,
        color: 'text-purple-500',
        change: formatChange(changes.active_orders)
      },
    ];
  };

  const stats = getKpiStats();

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-card/95 backdrop-blur-md border-b shadow-soft">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-foreground rounded-xl">
                <Shield className="h-6 w-6 text-background" />
              </div>
              <div>
                <h1 className="font-bold text-lg text-foreground">
                  {isSuperAdmin ? 'SuperAdmin Dashboard' : 'Admin Dashboard'}
                </h1>
                <p className="text-xs text-muted-foreground">
                  {isSuperAdmin ? 'Manage your canteen with advanced analytics' : 'Manage your canteen'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                onClick={handleRefresh}
                title="Refresh dashboard"
                className="hover:bg-muted transition-colors"
              >
                <RefreshCw className="h-5 w-5" />
              </Button>
              
              <div className="text-sm text-right hidden sm:block">
                <p className="font-medium">{user?.fullname}</p>
                <p className="text-xs text-muted-foreground">{user?.role}</p>
              </div>
              
              <ProfileButton />
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {loading ? (
            // Loading skeleton
            Array.from({ length: 4 }).map((_, index) => (
              <motion.div
                key={`skeleton-${index}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-card rounded-xl border p-4 shadow-soft"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-muted animate-pulse">
                    <div className="h-5 w-5 bg-gray-300 rounded"></div>
                  </div>
                  <div className="flex-1">
                    <div className="h-6 bg-gray-300 rounded mb-1 animate-pulse"></div>
                    <div className="h-3 bg-gray-200 rounded w-3/4 animate-pulse"></div>
                  </div>
                </div>
              </motion.div>
            ))
          ) : (
            stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-card rounded-xl border p-4 shadow-soft hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg bg-muted ${stat.color}`}>
                      <stat.icon className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-foreground">{stat.value}</p>
                      <p className="text-xs text-muted-foreground">{stat.label}</p>
                    </div>
                  </div>
                  {stat.change.show && (
                    <div className={`flex flex-col items-end ${stat.change.colorClass}`}>
                      <stat.change.icon className="h-3 w-3" />
                      <span className="text-xs font-medium">{stat.change.text}</span>
                      <span className="text-xs text-muted-foreground">vs yesterday</span>
                    </div>
                  )}
                </div>
              </motion.div>
            ))
          )}
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="management" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="management">Management</TabsTrigger>
            <TabsTrigger value="billing">
              <FileText className="h-4 w-4 mr-2" />
              Billing
            </TabsTrigger>
            <TabsTrigger value="predictive">
              <Brain className="h-4 w-4 mr-2" />
              Predictive AI
            </TabsTrigger>
            {isSuperAdmin && (
              <TabsTrigger value="analytics">
                <BarChart3 className="h-4 w-4 mr-2" />
                Analytics
              </TabsTrigger>
            )}
          </TabsList>

          <TabsContent value="management" className="space-y-6">
            {/* Menu Management - SUPER ADMIN ONLY */}
            {isSuperAdmin && <MenuManagement />}

            {/* User Management */}
            <UserManagement />

            {/* Info Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="p-4 bg-accent rounded-xl border border-primary/20"
            >
              <div className="flex items-start gap-3">
                <Shield className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="font-medium text-accent-foreground">Access Control</p>
                  <p className="text-sm text-muted-foreground">
                    {isSuperAdmin 
                      ? "As Super Admin, you have full access to all features including advanced analytics, menu management, and user management."
                      : "Only Super Admins can manage the Menu and create Admins. Regular Admins can only manage Kitchen Staff and view statistics."
                    }
                  </p>
                </div>
              </div>
            </motion.div>
          </TabsContent>

          <TabsContent value="billing" className="mt-6">
            <BillingDashboardEnhanced />
          </TabsContent>

          {/* Predictive Analytics Tab */}
          <TabsContent value="predictive" className="space-y-6">
            <PredictiveAIDashboard />
          </TabsContent>

          {isSuperAdmin && (
            <TabsContent value="analytics" className="space-y-6">
              <HistoricalAnalyticsDashboard />
            </TabsContent>
          )}
        </Tabs>
      </div>
    </div>
  );
}
