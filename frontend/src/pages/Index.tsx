import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { 
  UtensilsCrossed, 
  Clock, 
  ChefHat, 
  Sparkles,
  ArrowRight,
  Users,
  Timer,
  BarChart3
} from 'lucide-react';

const features = [
  {
    icon: Clock,
    title: 'Time-Based Filtering',
    description: 'Filter menu by your available time - only see items ready when you need them'
  },
  {
    icon: Timer,
    title: 'Real-Time Queue',
    description: 'Live order tracking with accurate wait time predictions powered by AI'
  },
  {
    icon: ChefHat,
    title: 'Kitchen Dashboard',
    description: 'Streamlined order management for efficient food preparation'
  },
  {
    icon: BarChart3,
    title: 'Smart Analytics',
    description: 'Data-driven insights for better inventory and demand planning'
  }
];

export default function Index() {
  const navigate = useNavigate();

  const handleStaffLogin = () => {
    console.log('Staff Login clicked');
    navigate('/login', { state: { isStaff: true } });
  };

  const handleSignIn = () => {
    console.log('Sign In clicked');
    navigate('/login');
  };

  const handleGetStarted = () => {
    console.log('Get Started clicked');
    navigate('/register');
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background Elements */}
        <div className="absolute inset-0 gradient-primary opacity-5" />
        <div className="absolute top-20 right-20 w-96 h-96 bg-primary/20 rounded-full blur-3xl" />
        <div className="absolute bottom-20 left-20 w-64 h-64 bg-secondary/20 rounded-full blur-3xl" />

        <div className="container mx-auto px-4 py-8">
          {/* Navbar */}
          <nav className="flex items-center justify-between mb-16">
            <div className="flex items-center gap-3">
              <div className="p-2 gradient-primary rounded-xl">
                <UtensilsCrossed className="h-6 w-6 text-primary-foreground" />
              </div>
              <span className="font-bold text-xl text-foreground">Smart Canteen</span>
            </div>

            <div className="flex items-center gap-3 relative z-10">
              <Button 
                type="button"
                variant="ghost" 
                onClick={handleSignIn}
              >
                Sign In
              </Button>
              <Button 
                type="button"
                className="bg-primary hover:bg-primary/90" 
                onClick={handleGetStarted}
              >
                Get Started
              </Button>
            </div>
          </nav>

          {/* Hero Content */}
          <div className="max-w-4xl mx-auto text-center py-20">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent text-accent-foreground text-sm font-medium mb-8">
                <Sparkles className="h-4 w-4" />
                AI-Powered Queue Optimization
              </div>
              
              <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-foreground leading-tight mb-6">
                Order Smart,
                <br />
                <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                  Skip the Queue
                </span>
              </h1>
              
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
                Revolutionary canteen management with real-time wait time predictions, 
                time-based menu filtering, and intelligent queue optimization.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center relative z-10">
                <Button
                  type="button"
                  size="lg"
                  className="bg-primary hover:bg-primary/90"
                  onClick={handleGetStarted}
                >
                  Start Ordering
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
                <Button
                  type="button"
                  size="lg"
                  variant="outline"
                  onClick={handleStaffLogin}
                >
                  <Users className="mr-2 h-5 w-5" />
                  Staff Login
                </Button>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Smart Features for Everyone
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Whether you're a hungry customer or kitchen staff, our platform 
              optimizes every step of the food ordering experience.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="bg-card rounded-2xl p-6 border shadow-soft hover:shadow-card transition-all group"
              >
                <div className="w-12 h-12 rounded-xl gradient-primary flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <feature.icon className="h-6 w-6 text-primary-foreground" />
                </div>
                <h3 className="font-semibold text-lg text-foreground mb-2">
                  {feature.title}
                </h3>
                <p className="text-muted-foreground text-sm">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="relative overflow-hidden rounded-3xl gradient-primary p-12 text-center"
          >
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl" />
            <div className="absolute bottom-0 left-0 w-96 h-96 bg-white/5 rounded-full blur-3xl" />
            
            <div className="relative z-10">
              <h2 className="text-3xl md:text-4xl font-bold text-primary-foreground mb-4">
                Ready to Skip the Queue?
              </h2>
              <p className="text-primary-foreground/80 max-w-xl mx-auto mb-8">
                Join thousands of users already enjoying faster, smarter food ordering.
              </p>
              <Button
                type="button"
                size="lg"
                className="bg-background text-foreground hover:bg-background/90"
                onClick={handleGetStarted}
              >
                Get Started Free
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <UtensilsCrossed className="h-5 w-5 text-primary" />
              <span className="font-semibold text-foreground">Smart Canteen</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © 2026 Smart Canteen. AI-powered queue optimization.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
