import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

export const useAuthNavigation = () => {
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = useCallback(() => {
    logout();
    navigate('/login');
  }, [logout, navigate]);

  const handleLogin = useCallback(async (email: string, password: string) => {
    const { login } = useAuth();
    await login(email, password);
    
    // Navigate based on user role after successful login
    if (user) {
      if (user.role === 'ADMIN' || user.role === 'SUPER_ADMIN') {
        navigate('/admin');
      } else if (user.role === 'KITCHEN' || user.role === 'STAFF') {
        navigate('/kitchen');
      } else {
        navigate('/menu');
      }
    }
  }, [navigate, user]);

  return {
    logout: handleLogout,
    login: handleLogin,
    user
  };
};
