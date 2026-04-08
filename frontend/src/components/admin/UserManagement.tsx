import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
    DialogDescription,
} from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Users, Plus, Trash2, Mail, User, Shield, ChefHat } from 'lucide-react';
import { API_URL, buildApiUrl, buildImageUrl } from '@/utils/api';
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';

interface UserData {
    id: number;
    fullname: string;
    email: string;
    role: string;
    is_active: boolean;
}

export function UserManagement() {
    const { user } = useAuth();
    const [users, setUsers] = useState<UserData[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isDialogOpen, setIsDialogOpen] = useState(false);

    // Form state
    const [newName, setNewName] = useState('');
    const [newEmail, setNewEmail] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [newRole, setNewRole] = useState('STAFF');

    const fetchUsers = async () => {
        try {
            const token = localStorage.getItem('canteen_token');
            const response = await fetch(buildApiUrl('/api/admin/users/'), {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.ok) {
                const data = await response.json();
                setUsers(data);
            } else {
                toast.error('Failed to fetch users');
            }
        } catch (error) {
            console.error('Error fetching users:', error);
            toast.error('Error connecting to server');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    const handleAddUser = async () => {
        if (!newName || !newEmail || !newPassword) {
            toast.error('Please fill in all fields');
            return;
        }

        try {
            const token = localStorage.getItem('canteen_token');
            const response = await fetch(buildApiUrl('/api/admin/users/'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    fullname: newName,
                    email: newEmail,
                    password: newPassword,
                    role: newRole
                })
            });

            if (response.ok) {
                toast.success('User added successfully');
                setNewName('');
                setNewEmail('');
                setNewPassword('');
                setNewRole('STAFF');
                setIsDialogOpen(false);
                fetchUsers();
            } else {
                const error = await response.json();
                toast.error(error.detail || 'Failed to add user');
            }
        } catch (error) {
            console.error('Error adding user:', error);
            toast.error('Error connecting to server');
        }
    };

    const handleDeleteUser = async (id: number) => {
        if (!confirm('Are you sure you want to delete this user?')) return;

        try {
            const token = localStorage.getItem('canteen_token');
            const response = await fetch(`buildApiUrl('/api/')admin/users/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                toast.success('User deleted successfully');
                setUsers(users.filter(u => u.id !== id));
            } else {
                const error = await response.json();
                toast.error(error.detail || 'Failed to delete user');
            }
        } catch (error) {
            console.error('Error deleting user:', error);
            toast.error('Error connecting to server');
        }
    };

    const getRoleBadge = (role: string) => {
        switch (role) {
            case 'SUPER_ADMIN':
                return <Badge className="bg-purple-500"><Shield className="h-3 w-3 mr-1" /> Super Admin</Badge>;
            case 'ADMIN':
                return <Badge className="bg-blue-500"><Shield className="h-3 w-3 mr-1" /> Admin</Badge>;
            case 'STAFF':
                return <Badge variant="secondary"><ChefHat className="h-3 w-3 mr-1" /> Staff</Badge>;
            default:
                return <Badge variant="outline"><User className="h-3 w-3 mr-1" /> User</Badge>;
        }
    };

    const canManageRole = (targetRole: string) => {
        if (user?.role === 'SUPER_ADMIN') return true;
        if (user?.role === 'ADMIN' && targetRole === 'STAFF') return true;
        return false;
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-card rounded-2xl border shadow-soft"
        >
            <div className="p-6 border-b">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-2 gradient-secondary rounded-lg">
                            <Users className="h-5 w-5 text-secondary-foreground" />
                        </div>
                        <div>
                            <h2 className="font-bold text-lg text-foreground">User Management</h2>
                            <p className="text-sm text-muted-foreground">
                                Manage Admins and Kitchen Staff
                            </p>
                        </div>
                    </div>

                    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                        <DialogTrigger asChild>
                            <Button className="gradient-primary text-primary-foreground">
                                <Plus className="h-4 w-4 mr-2" />
                                Add User
                            </Button>
                        </DialogTrigger>
                        <DialogContent className="bg-card">
                            <DialogHeader>
                                <DialogTitle>Add New User</DialogTitle>
                                <DialogDescription>
                                    Create a new user account with the appropriate role and permissions.
                                </DialogDescription>
                            </DialogHeader>
                            <div className="space-y-4 pt-4">
                                <div className="space-y-2">
                                    <Label htmlFor="fullname">Full Name</Label>
                                    <Input
                                        id="fullname"
                                        placeholder="Enter full name"
                                        value={newName}
                                        onChange={(e) => setNewName(e.target.value)}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="email">Email Address</Label>
                                    <Input
                                        id="email"
                                        type="email"
                                        placeholder="Enter email"
                                        value={newEmail}
                                        onChange={(e) => setNewEmail(e.target.value)}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="password">Password</Label>
                                    <Input
                                        id="password"
                                        type="password"
                                        placeholder="Enter password"
                                        value={newPassword}
                                        onChange={(e) => setNewPassword(e.target.value)}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="role">Role</Label>
                                    <Select value={newRole} onValueChange={setNewRole}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select role" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="STAFF">Kitchen Staff</SelectItem>
                                            {user?.role === 'SUPER_ADMIN' && (
                                                <SelectItem value="ADMIN">Admin</SelectItem>
                                            )}
                                        </SelectContent>
                                    </Select>
                                </div>
                                <Button
                                    className="w-full gradient-primary text-primary-foreground"
                                    onClick={handleAddUser}
                                >
                                    Create User
                                </Button>
                            </div>
                        </DialogContent>
                    </Dialog>
                </div>
            </div>

            <div className="p-6">
                {users.length === 0 ? (
                    <div className="text-center py-8">
                        <Users className="h-12 w-12 mx-auto mb-3 text-muted-foreground/50" />
                        <p className="text-muted-foreground">No users found</p>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {users.map((userData, index) => (
                            <motion.div
                                key={userData.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.05 }}
                                className="flex items-center justify-between p-4 bg-muted/50 rounded-xl hover:bg-muted transition-colors"
                            >
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-full gradient-secondary flex items-center justify-center text-secondary-foreground font-bold">
                                        {userData.fullname.charAt(0)}
                                    </div>
                                    <div>
                                        <p className="font-medium text-foreground flex items-center gap-2">
                                            {userData.fullname}
                                            {userData.id === user?.id && <span className="text-xs text-muted-foreground">(You)</span>}
                                        </p>
                                        <p className="text-sm text-muted-foreground">{userData.email}</p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-2">
                                    {getRoleBadge(userData.role)}

                                    {userData.id !== user?.id && canManageRole(userData.role) && (
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="text-destructive hover:text-destructive hover:bg-destructive/10"
                                            onClick={() => handleDeleteUser(userData.id)}
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    )}
                                </div>
                            </motion.div>
                        ))}
                    </div>
                )}
            </div>
        </motion.div>
    );
}
