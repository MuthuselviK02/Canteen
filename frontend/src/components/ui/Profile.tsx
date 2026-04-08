import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  User, 
  Mail, 
  Calendar, 
  Shield, 
  LogOut, 
  X,
  Clock,
  Package,
  UtensilsCrossed,
  Heart
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface ProfileDropdownProps {
  onClose: () => void;
}

export function ProfileDropdown({ onClose }: ProfileDropdownProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
    onClose();
  };

  const getRoleColor = (role: string) => {
    switch (role?.toUpperCase()) {
      case 'SUPER_ADMIN': return 'bg-red-100 text-red-800 border-red-200';
      case 'ADMIN': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'STAFF': return 'bg-green-100 text-green-800 border-green-200';
      case 'USER': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role?.toUpperCase()) {
      case 'SUPER_ADMIN': return 'Super Admin';
      case 'ADMIN': return 'Admin';
      case 'STAFF': return 'Staff';
      case 'USER': return 'User';
      default: return 'User';
    }
  };

  const getDashboardRoute = (role: string) => {
    switch (role?.toUpperCase()) {
      case 'SUPER_ADMIN':
      case 'ADMIN': return '/admin';
      case 'STAFF': return '/kitchen';
      case 'USER': return '/menu';
      default: return '/menu';
    }
  };

  const handleGoToDashboard = () => {
    const route = getDashboardRoute(user?.role || '');
    navigate(route);
    onClose();
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, y: -10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95, y: -10 }}
      transition={{ duration: 0.2 }}
      className="absolute right-0 top-full mt-2 w-80 bg-background border rounded-xl shadow-lg z-50"
    >
      <Card className="border-0 shadow-none">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Profile</CardTitle>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-6 w-6"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* User Info */}
          <div className="flex items-center space-x-3">
            <div className="h-12 w-12 rounded-full gradient-primary flex items-center justify-center">
              <User className="h-6 w-6 text-primary-foreground" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-foreground">{user?.fullname}</h3>
              <p className="text-sm text-muted-foreground">{user?.email}</p>
              <Badge className={`mt-1 text-xs ${getRoleColor(user?.role || '')}`}>
                {getRoleLabel(user?.role || '')}
              </Badge>
            </div>
          </div>

          {/* Account Details */}
          <div className="space-y-3 pt-3 border-t">
            <div className="flex items-center space-x-3 text-sm">
              <Mail className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">Email:</span>
              <span className="text-foreground font-medium">{user?.email}</span>
            </div>
            
            <div className="flex items-center space-x-3 text-sm">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">Member since:</span>
              <span className="text-foreground font-medium">Recent</span>
            </div>

            <div className="flex items-center space-x-3 text-sm">
              <Shield className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">Role:</span>
              <Badge className={`text-xs ${getRoleColor(user?.role || '')}`}>
                {getRoleLabel(user?.role || '')}
              </Badge>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="space-y-2 pt-3 border-t">
            <Button
              variant="outline"
              size="sm"
              onClick={handleGoToDashboard}
              className="w-full justify-start"
            >
              <UtensilsCrossed className="h-4 w-4 mr-2" />
              Go to Dashboard
            </Button>

            {user?.role === 'USER' && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    navigate('/orders');
                    onClose();
                  }}
                  className="w-full justify-start"
                >
                  <Package className="h-4 w-4 mr-2" />
                  My Orders
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    navigate('/favorites');
                    onClose();
                  }}
                  className="w-full justify-start"
                >
                  <Heart className="h-4 w-4 mr-2" />
                  Favorites
                </Button>
              </>
            )}
          </div>

          {/* Logout */}
          <div className="pt-3 border-t">
            <Button
              variant="destructive"
              size="sm"
              onClick={handleLogout}
              className="w-full justify-start"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

export function ProfileButton() {
  const [showProfile, setShowProfile] = useState(false);
  const { user } = useAuth();

  return (
    <div className="relative">
      <Button
        variant="outline"
        size="icon"
        onClick={() => setShowProfile(!showProfile)}
        className="relative"
      >
        <User className="h-5 w-5" />
        {showProfile && (
          <div className="absolute -bottom-1 -right-1 h-3 w-3 rounded-full bg-primary"></div>
        )}
      </Button>

      <AnimatePresence>
        {showProfile && (
          <ProfileDropdown onClose={() => setShowProfile(false)} />
        )}
      </AnimatePresence>
    </div>
  );
}
