import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { AuthLayout } from '@/components/auth/AuthLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Loader2, User, Mail, Lock } from 'lucide-react';

const validateUsername = (value: string): string => {
  const usernameRegex = /^[A-Za-z]+$/;
  if (!usernameRegex.test(value)) {
    return 'Username must contain only letters';
  }
  return '';
};

const validateEmail = (value: string): string => {
  const emailRegex = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
  if (!emailRegex.test(value)) {
    return 'Please enter a valid email address';
  }
  return '';
};

const validatePassword = (value: string): string => {
  if (value.length < 6) {
    return 'Password must be at least 6 characters';
  }
  if (value.length > 16) {
    return 'Password cannot exceed 16 characters';
  }
  return '';
};

export default function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isHumanVerified, setIsHumanVerified] = useState(false);
  const [errors, setErrors] = useState({ name: '', email: '', password: '' });
  const [touched, setTouched] = useState({ name: false, email: false, password: false });
  const [isLoading, setIsLoading] = useState(false);
  const { register, login, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Clear form on mount to prevent browser autofill
    setName('');
    setEmail('');
    setPassword('');
    
    if (user) {
      if (user.role === 'ADMIN' || user.role === 'SUPER_ADMIN') navigate('/admin');
      else if (user.role === 'KITCHEN' || user.role === 'STAFF') navigate('/kitchen');
      else navigate('/menu');
    }
  }, [user, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const nameError = validateUsername(name);
    const emailError = validateEmail(email);
    const passwordError = validatePassword(password);

    setErrors({ name: nameError, email: emailError, password: passwordError });
    setTouched({ name: true, email: true, password: true });

    if (nameError || emailError || passwordError) {
      return;
    }

    if (!isHumanVerified) {
      toast.error('Please confirm you are not a robot');
      return;
    }

    setIsLoading(true);
    try {
      await register(name, email, password);
      toast.success('Account created successfully!');
      
      // Auto-login after successful registration
      try {
        await login(email, password);
        toast.success('Welcome to Smart Canteen!');
        // Navigation will be handled by the useEffect based on user role
      } catch (loginError: any) {
        // If auto-login fails, redirect to login page
        toast.error('Please login with your new account');
        navigate('/login');
      }
    } catch (error: any) {
      toast.error(error.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  const isFormValid =
    !validateUsername(name) && !validateEmail(email) && !validatePassword(password);

  return (
    <AuthLayout
      title="Create Account"
      subtitle="Join Smart Canteen today"
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="space-y-2">
          <Label htmlFor="name">Full Name</Label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              id="name"
              type="text"
              placeholder="Enter your full name"
              value={name}
              onChange={(e) => {
                const value = e.target.value;
                setName(value);
                setErrors((prev) => ({ ...prev, name: validateUsername(value) }));
              }}
              onBlur={() => {
                setTouched((prev) => ({ ...prev, name: true }));
                setErrors((prev) => ({ ...prev, name: validateUsername(name) }));
              }}
              className={`pl-10 h-12 ${
                touched.name && errors.name ? 'border-red-500 focus-visible:ring-red-500' : ''
              }`}
              disabled={isLoading}
            />
          </div>
          {touched.name && errors.name && (
            <p className="text-sm text-red-500">{errors.name}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => {
                const value = e.target.value;
                setEmail(value);
                setErrors((prev) => ({ ...prev, email: validateEmail(value) }));
              }}
              onBlur={() => {
                setTouched((prev) => ({ ...prev, email: true }));
                setErrors((prev) => ({ ...prev, email: validateEmail(email) }));
              }}
              className={`pl-10 h-12 ${
                touched.email && errors.email ? 'border-red-500 focus-visible:ring-red-500' : ''
              }`}
              disabled={isLoading}
              autoComplete="off"
            />
          </div>
          {touched.email && errors.email && (
            <p className="text-sm text-red-500">{errors.email}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              id="password"
              type="password"
              placeholder="Create a password"
              value={password}
              onChange={(e) => {
                const value = e.target.value;
                setPassword(value);
                setErrors((prev) => ({ ...prev, password: validatePassword(value) }));
              }}
              onBlur={() => {
                setTouched((prev) => ({ ...prev, password: true }));
                setErrors((prev) => ({ ...prev, password: validatePassword(password) }));
              }}
              className={`pl-10 h-12 ${
                touched.password && errors.password ? 'border-red-500 focus-visible:ring-red-500' : ''
              }`}
              disabled={isLoading}
              autoComplete="new-password"
            />
          </div>
          {touched.password && errors.password && (
            <p className="text-sm text-red-500">{errors.password}</p>
          )}
        </div>

        <div className="rounded-lg border bg-card p-4">
          <div className="flex items-center space-x-3">
            <input
              id="register-robot-check"
              type="checkbox"
              checked={isHumanVerified}
              onChange={(e) => setIsHumanVerified(e.target.checked)}
              disabled={isLoading}
              className="h-4 w-4 cursor-pointer accent-primary"
            />
            <Label htmlFor="register-robot-check" className="cursor-pointer text-sm font-medium">
              I'm not a robot
            </Label>
          </div>
        </div>

        <Button
          type="submit"
          className="w-full h-12 gradient-primary text-primary-foreground font-semibold shadow-soft hover:shadow-card transition-all duration-300"
          disabled={isLoading || !isFormValid || !isHumanVerified}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Creating account...
            </>
          ) : (
            'Create Account'
          )}
        </Button>

        <div className="text-center text-sm text-muted-foreground">
          Already have an account?{' '}
          <Link to="/login" className="text-primary font-semibold hover:underline">
            Sign in
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
}
