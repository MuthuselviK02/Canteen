import { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext, AuthContextType } from '@/contexts/AuthContext';

// Custom hook that safely uses navigate within AuthContext
export const useAuthNavigate = (): AuthContextType & { navigate: ReturnType<typeof useNavigate> } => {
  const navigate = useNavigate();
  const auth = useContext(AuthContext);
  
  if (!auth) {
    throw new Error('useAuthNavigate must be used within AuthProvider');
  }
  
  return {
    user: auth.user,
    isLoading: auth.isLoading,
    login: auth.login,
    register: auth.register,
    logout: auth.logout,
    isAdmin: auth.isAdmin,
    isSuperAdmin: auth.isSuperAdmin,
    navigate
  };
};
