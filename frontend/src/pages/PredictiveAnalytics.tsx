import React from 'react';
import PredictiveAnalyticsDashboardRefactored from '@/components/analytics/PredictiveAnalyticsDashboardRefactored';
import { useAuth } from '@/contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function PredictiveAnalyticsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  // Check if user is authenticated and has admin privileges
  React.useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    
    // Check if user has admin or staff role
    if (!['ADMIN', 'SUPER_ADMIN', 'STAFF'].includes(user.role)) {
      navigate('/menu');
      return;
    }
  }, [user, navigate]);

  if (!user || !['ADMIN', 'SUPER_ADMIN', 'STAFF'].includes(user.role)) {
    return null;
  }

  return (
    <div className="container mx-auto px-4 py-6">
      <PredictiveAnalyticsDashboardRefactored />
    </div>
  );
}
