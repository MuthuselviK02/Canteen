import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckCircle, ArrowRight, User, Mail, Lock, UtensilsCrossed } from 'lucide-react';
import { motion } from 'framer-motion';

export default function RegisterSuccess() {
  const navigate = useNavigate();
  const [countdown, setCountdown] = useState(10);

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          navigate('/login');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [navigate]);

  const handleGoToLogin = () => {
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="text-center pb-2">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="mx-auto w-16 h-16 bg-gradient-to-r from-green-400 to-green-600 rounded-full flex items-center justify-center mb-4"
            >
              <CheckCircle className="w-8 h-8 text-white" />
            </motion.div>
            <CardTitle className="text-2xl font-bold text-gray-900">
              Account Created Successfully! 🎉
            </CardTitle>
            <p className="text-gray-600 mt-2">
              Welcome to Smart Canteen! Your account has been created.
            </p>
          </CardHeader>

          <CardContent className="space-y-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="bg-blue-50 border border-blue-200 rounded-lg p-4"
            >
              <div className="flex items-center space-x-2 mb-2">
                <User className="w-4 h-4 text-blue-600" />
                <span className="font-medium text-blue-900">What's Next?</span>
              </div>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Sign in with your email and password</li>
                <li>• Explore our smart menu recommendations</li>
                <li>• Place your first order</li>
                <li>• Enjoy personalized AI suggestions</li>
              </ul>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="text-center"
            >
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">
                  Redirecting to login page in...
                </p>
                <div className="text-3xl font-bold text-primary">
                  {countdown}
                </div>
                <div className="text-xs text-gray-500">seconds</div>
              </div>

              <Button
                onClick={handleGoToLogin}
                className="w-full h-12 gradient-primary text-primary-foreground font-semibold shadow-soft hover:shadow-card transition-all duration-300"
              >
                Go to Login Now
                <ArrowRight className="ml-2 w-4 h-4" />
              </Button>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="text-center text-xs text-gray-500"
            >
              <div className="flex items-center justify-center space-x-1 mb-2">
                <UtensilsCrossed className="w-3 h-3" />
                <span>Smart Canteen - AI-Powered Food Ordering</span>
              </div>
              <p>Experience personalized meal recommendations</p>
            </motion.div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
