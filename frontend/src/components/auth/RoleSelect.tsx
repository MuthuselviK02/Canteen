import { UserRole } from '@/contexts/AuthContext';
import { User, ChefHat, Shield } from 'lucide-react';
import { cn } from '@/lib/utils';

interface RoleSelectProps {
  value: UserRole;
  onChange: (role: UserRole) => void;
  showAdmin?: boolean;
}

const roles = [
  {
    value: 'user' as UserRole,
    label: 'Student',
    description: 'Order food & view status',
    icon: User,
    color: 'primary'
  },
  {
    value: 'faculty' as UserRole,
    label: 'Faculty',
    description: 'Special menu access & priority',
    icon: User,
    color: 'secondary'
  },
  {
    value: 'kitchen' as UserRole,
    label: 'Kitchen Staff',
    description: 'Manage preparation',
    icon: ChefHat,
    color: 'accent'
  }
];

export function RoleSelect({ value, onChange, showAdmin }: RoleSelectProps) {
  const allRoles = showAdmin
    ? [...roles, {
      value: 'admin' as UserRole,
      label: 'Admin',
      description: 'Full system access',
      icon: Shield,
      color: 'accent'
    }]
    : roles;

  return (
    <div className="grid grid-cols-2 gap-3">
      {allRoles.map((role) => (
        <button
          key={role.value}
          type="button"
          onClick={() => onChange(role.value)}
          className={cn(
            "flex flex-col items-center p-4 rounded-xl border-2 transition-all duration-300",
            value === role.value
              ? "border-primary bg-accent shadow-soft"
              : "border-border hover:border-primary/50 hover:bg-muted/50"
          )}
        >
          <div className={cn(
            "p-3 rounded-lg mb-2",
            value === role.value
              ? "gradient-primary text-primary-foreground"
              : "bg-muted text-muted-foreground"
          )}>
            <role.icon className="h-5 w-5" />
          </div>
          <span className={cn(
            "font-semibold text-sm",
            value === role.value ? "text-foreground" : "text-muted-foreground"
          )}>
            {role.label}
          </span>
          <span className="text-xs text-muted-foreground text-center mt-1">
            {role.description}
          </span>
        </button>
      ))}
    </div>
  );
}
