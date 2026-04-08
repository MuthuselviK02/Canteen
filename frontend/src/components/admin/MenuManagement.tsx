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
import { UtensilsCrossed, Plus, Trash2, Edit, IndianRupee, Clock, Flame } from 'lucide-react';
import { API_URL, buildApiUrl, buildImageUrl } from '@/utils/api';
import { toast } from 'sonner';
import { Category, CATEGORIES_API, getCategoryLabel, getCategoryKey, FALLBACK_CATEGORIES } from '@/core/categories';

interface MenuItem {
    id: number;
    name: string;
    description: string;
    price: number;
    category: string;
    image_url: string;
    is_available: boolean;
    base_prep_time: number;
    calories: number;
    is_spicy: boolean;
    is_vegetarian: boolean;
    present_stocks: number;
}

const API_BASE_URL = API_URL.replace(/\/$/, '');

export function MenuManagement() {
    const [items, setItems] = useState<MenuItem[]>([]);
    const [categories, setCategories] = useState<Category[]>(FALLBACK_CATEGORIES);
    const [isLoading, setIsLoading] = useState(true);
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Form state
    const [formData, setFormData] = useState<Partial<MenuItem>>({
        name: '',
        description: '',
        price: undefined,
        category: 'main_course',
        image_url: `${API_BASE_URL}/static/images/default_food.jpg`,
        is_available: true,
        base_prep_time: 15,
        calories: 0,
        is_spicy: false,
        is_vegetarian: true,
        present_stocks: 0
    });
    const [editingId, setEditingId] = useState<number | null>(null);

    const isPriceValid = typeof formData.price === 'number' && formData.price > 0;
    const isPrepTimeValid = typeof formData.base_prep_time === 'number' && formData.base_prep_time > 0;
    const isNameValid = !!formData.name?.trim();
    const isDescriptionValid = !!formData.description?.trim();
    const canSubmit = isNameValid && isDescriptionValid && isPriceValid && isPrepTimeValid && !isSubmitting;

    // Fetch categories from API
    const fetchCategories = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}${CATEGORIES_API.ALL}`);
            if (response.ok) {
                const data = await response.json();
                setCategories(data);
            } else {
                console.warn('Failed to fetch categories, using fallback');
                setCategories(FALLBACK_CATEGORIES);
            }
        } catch (error) {
            console.error('Error fetching categories:', error);
            setCategories(FALLBACK_CATEGORIES);
        }
    };

    const fetchMenu = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/menu/`);
            if (response.ok) {
                const data = await response.json();
                setItems(data);
            } else {
                toast.error('Failed to fetch menu');
            }
        } catch (error) {
            console.error('Error fetching menu:', error);
            toast.error('Error connecting to server');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchCategories();
        fetchMenu();
    }, []);

    const handleSubmit = async () => {
        if (!canSubmit) {
            toast.error('Please fill in all required fields with valid values');
            return;
        }

        try {
            setIsSubmitting(true);
            const token = localStorage.getItem('canteen_token');
            const url = editingId
                ? `${API_BASE_URL}/api/admin/menu/${editingId}`
                : `${API_BASE_URL}/api/admin/menu/`;

            const method = editingId ? 'PUT' : 'POST';

            const payload = {
                ...formData,
                price: Number(formData.price),
                base_prep_time: Number(formData.base_prep_time),
                calories: Number(formData.calories || 0)
            };

            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                toast.success(`Menu item ${editingId ? 'updated' : 'created'} successfully`);
                setFormData({
                    name: '',
                    description: '',
                    price: undefined,
                    category: 'main_course',
                    image_url: `${API_BASE_URL}/static/images/default_food.jpg`,
                    is_available: true,
                    base_prep_time: 15,
                    calories: 0,
                    is_spicy: false,
                    is_vegetarian: true,
                    present_stocks: 0
                });
                setEditingId(null);
                setIsDialogOpen(false);
                fetchMenu();
                // Emit custom event to notify Menu page to refresh
                window.dispatchEvent(new CustomEvent('menu-updated'));
            } else {
                let errorMsg = 'Operation failed';
                try {
                    const error = await response.json();
                    errorMsg = error.detail || errorMsg;
                } catch (e) {
                    console.error('Failed to parse error response', e);
                    errorMsg = `Server error: ${response.status} ${response.statusText}`;
                }
                toast.error(errorMsg || 'Unable to save item. Please try again.');
            }
        } catch (error) {
            console.error('Error saving menu item:', error);
            toast.error('Unable to reach the server. Please try again shortly.');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm('Are you sure you want to delete this item?')) return;

        try {
            const token = localStorage.getItem('canteen_token');
            const response = await fetch(`${API_BASE_URL}/api/admin/menu/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                toast.success('Menu item deleted successfully');
                setItems(items.filter(i => i.id !== id));
                // Emit custom event to notify Menu page to refresh
                window.dispatchEvent(new CustomEvent('menu-updated'));
            } else {
                const error = await response.json();
                toast.error(error.detail || 'Failed to delete item');
            }
        } catch (error) {
            console.error('Error deleting item:', error);
            toast.error('Error connecting to server');
        }
    };

    const handleEdit = (item: MenuItem) => {
        setFormData(item);
        setEditingId(item.id);
        setIsDialogOpen(true);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-card rounded-2xl border shadow-soft mb-8"
        >
            <div className="p-6 border-b">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-2 gradient-primary rounded-lg">
                            <UtensilsCrossed className="h-5 w-5 text-primary-foreground" />
                        </div>
                        <div>
                            <h2 className="font-bold text-lg text-foreground">Menu Management</h2>
                            <p className="text-sm text-muted-foreground">
                                Manage food items, prices, and availability
                            </p>
                        </div>
                    </div>

                    <Dialog open={isDialogOpen} onOpenChange={(open) => {
                        setIsDialogOpen(open);
                        if (!open) {
                            setEditingId(null);
                            setFormData({
                                name: '',
                                description: '',
                                price: undefined,
                                category: 'main_course',
                                image_url: `${API_BASE_URL}/static/images/default_food.jpg`,
                                is_available: true,
                                base_prep_time: 15,
                                calories: 0,
                                is_spicy: false,
                                is_vegetarian: true,
                                present_stocks: 0
                            });
                        }
                    }}>
                        <DialogTrigger asChild>
                            <Button className="gradient-primary text-primary-foreground">
                                <Plus className="h-4 w-4 mr-2" />
                                Add Item
                            </Button>
                        </DialogTrigger>
                        <DialogContent
                            className="bg-card max-h-[90vh] overflow-y-auto"
                            aria-describedby="menu-item-dialog-description"
                        >
                            <DialogHeader>
                                <DialogTitle>{editingId ? 'Edit Menu Item' : 'Add New Menu Item'}</DialogTitle>
                                <DialogDescription id="menu-item-dialog-description">
                                    Provide the menu item details below. Fields marked with validation messages are required.
                                </DialogDescription>
                            </DialogHeader>
                            <div className="space-y-4 pt-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="name">Item Name</Label>
                                        <Input
                                            id="name"
                                            value={formData.name}
                                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="price">Price (₹)</Label>
                                        <Input
                                            id="price"
                                            type="number"
                                            min={0}
                                            step="0.01"
                                            placeholder="Enter price"
                                            value={formData.price ?? ''}
                                            onChange={(e) => {
                                                const value = e.target.value;
                                                setFormData({
                                                    ...formData,
                                                    price: value === '' ? undefined : Number(value)
                                                });
                                            }}
                                        />
                                        {!isPriceValid && (
                                            <p className="text-xs text-destructive">Price must be greater than 0.</p>
                                        )}
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="description">Description</Label>
                                    <Input
                                        id="description"
                                        value={formData.description}
                                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="category">Category</Label>
                                        <Select value={formData.category} onValueChange={(val) => setFormData({ ...formData, category: val })}>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select category" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {categories.map((category) => (
                                                    <SelectItem key={category.key} value={category.key}>
                                                        {category.label}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="prep_time">Prep Time (mins)</Label>
                                        <Input
                                            id="prep_time"
                                            type="number"
                                            min={1}
                                            value={formData.base_prep_time ?? ''}
                                            onChange={(e) => {
                                                const value = e.target.value;
                                                setFormData({
                                                    ...formData,
                                                    base_prep_time: value === '' ? undefined : Number(value)
                                                });
                                            }}
                                        />
                                        {!isPrepTimeValid && (
                                            <p className="text-xs text-destructive">Prep time must be greater than 0.</p>
                                        )}
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="image">Image URL</Label>
                                    <Input
                                        id="image"
                                        value={formData.image_url}
                                        onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="calories">Calories</Label>
                                    <Input
                                        id="calories"
                                        type="number"
                                        min={0}
                                        placeholder="Enter calories"
                                        value={formData.calories ?? ''}
                                        onChange={(e) => {
                                            const value = e.target.value;
                                            setFormData({
                                                ...formData,
                                                calories: value === '' ? undefined : Number(value)
                                            });
                                        }}
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="present_stocks">Present Stocks</Label>
                                    <Input
                                        id="present_stocks"
                                        type="number"
                                        min={0}
                                        placeholder="Enter stock quantity"
                                        value={formData.present_stocks ?? ''}
                                        onChange={(e) => {
                                            const value = e.target.value;
                                            setFormData({
                                                ...formData,
                                                present_stocks: value === '' ? undefined : Number(value)
                                            });
                                        }}
                                    />
                                </div>

                                <div className="flex gap-4 pt-2">
                                    <div className="flex items-center space-x-2">
                                        <input
                                            type="checkbox"
                                            id="veg"
                                            className="rounded border-gray-300"
                                            checked={formData.is_vegetarian}
                                            onChange={(e) => setFormData({ ...formData, is_vegetarian: e.target.checked })}
                                        />
                                        <Label htmlFor="veg">Vegetarian</Label>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <input
                                            type="checkbox"
                                            id="spicy"
                                            className="rounded border-gray-300"
                                            checked={formData.is_spicy}
                                            onChange={(e) => setFormData({ ...formData, is_spicy: e.target.checked })}
                                        />
                                        <Label htmlFor="spicy">Spicy</Label>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <input
                                            type="checkbox"
                                            id="available"
                                            className="rounded border-gray-300"
                                            checked={formData.is_available}
                                            onChange={(e) => setFormData({ ...formData, is_available: e.target.checked })}
                                        />
                                        <Label htmlFor="available">Available</Label>
                                    </div>
                                </div>

                                <Button
                                    className="w-full gradient-primary text-primary-foreground mt-4"
                                    onClick={handleSubmit}
                                    disabled={!canSubmit}
                                >
                                    {isSubmitting
                                        ? editingId
                                            ? 'Updating...'
                                            : 'Creating...'
                                        : editingId
                                            ? 'Update Item'
                                            : 'Create Item'}
                                </Button>
                            </div>
                        </DialogContent>
                    </Dialog>
                </div>
            </div>

            <div className="p-6">
                {items.length === 0 ? (
                    <div className="text-center py-8">
                        <UtensilsCrossed className="h-12 w-12 mx-auto mb-3 text-muted-foreground/50" />
                        <p className="text-muted-foreground">No menu items found</p>
                    </div>
                ) : (
                    <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
                        {items.map((item, index) => (
                            <motion.div
                                key={item.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.05 }}
                                className="flex items-center justify-between p-4 bg-muted/50 rounded-xl hover:bg-muted transition-colors"
                            >
                                <div className="flex items-center gap-4">
                                    <img
                                        src={item.image_url ? `${API_BASE_URL}${item.image_url}` : `${API_BASE_URL}/static/images/default_food.jpg`}
                                        alt={item.name}
                                        className="w-16 h-16 rounded-lg object-cover"
                                        onError={(e) => {
                                            e.currentTarget.src = `${API_BASE_URL}/static/images/default_food.jpg`;
                                        }}
                                    />
                                    <div>
                                        <h3 className="font-medium text-foreground flex items-center gap-2">
                                            {item.name}
                                            {item.is_vegetarian ? (
                                                <div className="w-2 h-2 rounded-full bg-green-500" title="Vegetarian" />
                                            ) : (
                                                <div className="w-2 h-2 rounded-full bg-red-500" title="Non-Vegetarian" />
                                            )}
                                        </h3>
                                        <p className="text-sm text-muted-foreground line-clamp-1">{item.description}</p>
                                        <div className="flex gap-3 mt-1 text-xs text-muted-foreground">
                                            <span className="flex items-center"><IndianRupee className="h-3 w-3 mr-0.5" />{item.price}</span>
                                            <span className="flex items-center"><Clock className="h-3 w-3 mr-0.5" />{item.base_prep_time}m</span>
                                            <span className="flex items-center">Stock: {item.present_stocks || 0}</span>
                                            <Badge variant="secondary" className="text-xs">
                                                {getCategoryLabel(categories, item.category)}
                                            </Badge>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-2">
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={() => handleEdit(item)}
                                    >
                                        <Edit className="h-4 w-4" />
                                    </Button>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="text-destructive hover:text-destructive hover:bg-destructive/10"
                                        onClick={() => handleDelete(item.id)}
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                )}
            </div>
        </motion.div>
    );
}
