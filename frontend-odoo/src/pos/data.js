export const CATEGORY_COLORS = ['#4ADE80', '#FB7185', '#C084FC', '#D4A056', '#60A5FA']

export const TAX_OPTIONS = [5, 18, 28]

export const INITIAL_CATEGORIES = [
  { id: 'coffee', name: 'Coffee', icon: '☕', color: '#60A5FA' },
  { id: 'beverages', name: 'Beverages', icon: '🥤', color: '#D4A056' },
  { id: 'burgers', name: 'Burgers', icon: '🍔', color: '#FB7185' },
  { id: 'pizza', name: 'Pizza', icon: '🍕', color: '#FB7185' },
  { id: 'desserts', name: 'Desserts', icon: '🍰', color: '#C084FC' },
  { id: 'snacks', name: 'Snacks', icon: '🥪', color: '#D4A056' },
  { id: 'meals', name: 'Meals', icon: '🥗', color: '#4ADE80' },
  { id: 'icecream', name: 'Ice Cream', icon: '🍨', color: '#60A5FA' },
]

export const INITIAL_PRODUCTS = [
  { id: 'p1', categoryId: 'coffee', name: 'Cappuccino', price: 180, tax: 5, description: '', icon: '☕', status: 'available', archived: false },
  { id: 'p2', categoryId: 'coffee', name: 'Latte', price: 190, tax: 5, description: '', icon: '☕', status: 'available', archived: false },
  { id: 'p3', categoryId: 'coffee', name: 'Cold Coffee', price: 220, tax: 5, description: '', icon: '🧊', status: 'low', archived: false },
  { id: 'p4', categoryId: 'coffee', name: 'Americano', price: 160, tax: 5, description: '', icon: '☕', status: 'available', archived: false },
  { id: 'p5', categoryId: 'coffee', name: 'Mocha', price: 210, tax: 5, description: '', icon: '☕', status: 'available', archived: false },
  { id: 'p6', categoryId: 'coffee', name: 'Espresso', price: 140, tax: 5, description: '', icon: '☕', status: 'unavailable', archived: false },

  { id: 'p7', categoryId: 'beverages', name: 'Masala Tea', price: 80, tax: 5, description: '', icon: '🍵', status: 'available', archived: false },
  { id: 'p8', categoryId: 'beverages', name: 'Lassi', price: 120, tax: 5, description: '', icon: '🥤', status: 'available', archived: false },
  { id: 'p9', categoryId: 'beverages', name: 'Iced Tea', price: 150, tax: 5, description: '', icon: '🧊', status: 'low', archived: false },
  { id: 'p10', categoryId: 'beverages', name: 'Lemonade', price: 90, tax: 5, description: '', icon: '🍋', status: 'available', archived: false },
  { id: 'p11', categoryId: 'beverages', name: 'Hot Chocolate', price: 170, tax: 5, description: '', icon: '🍫', status: 'available', archived: false },
  { id: 'p12', categoryId: 'beverages', name: 'Milkshake', price: 160, tax: 5, description: '', icon: '🥤', status: 'available', archived: false },

  { id: 'p13', categoryId: 'burgers', name: 'Cheese Burger', price: 220, tax: 18, description: '', icon: '🍔', status: 'available', archived: false },
  { id: 'p14', categoryId: 'burgers', name: 'Veg Burger', price: 180, tax: 18, description: '', icon: '🍔', status: 'available', archived: false },
  { id: 'p15', categoryId: 'burgers', name: 'Chicken Burger', price: 240, tax: 18, description: '', icon: '🍔', status: 'low', archived: false },
  { id: 'p16', categoryId: 'burgers', name: 'Double Patty', price: 280, tax: 18, description: '', icon: '🍔', status: 'available', archived: false },

  { id: 'p17', categoryId: 'pizza', name: 'Margherita', price: 320, tax: 18, description: '', icon: '🍕', status: 'available', archived: false },
  { id: 'p18', categoryId: 'pizza', name: 'Pepperoni', price: 380, tax: 18, description: '', icon: '🍕', status: 'unavailable', archived: false },
  { id: 'p19', categoryId: 'pizza', name: 'Veggie Supreme', price: 350, tax: 18, description: '', icon: '🍕', status: 'available', archived: false },
  { id: 'p20', categoryId: 'pizza', name: 'Farmhouse', price: 360, tax: 18, description: '', icon: '🍕', status: 'available', archived: false },

  { id: 'p21', categoryId: 'desserts', name: 'Brownie', price: 150, tax: 5, description: '', icon: '🍰', status: 'available', archived: false },
  { id: 'p22', categoryId: 'desserts', name: 'Cheesecake', price: 220, tax: 5, description: '', icon: '🍰', status: 'available', archived: false },
  { id: 'p23', categoryId: 'desserts', name: 'Tiramisu', price: 240, tax: 5, description: '', icon: '🍰', status: 'low', archived: false },
  { id: 'p24', categoryId: 'desserts', name: 'Donut', price: 90, tax: 5, description: '', icon: '🍩', status: 'available', archived: false },

  { id: 'p25', categoryId: 'snacks', name: 'Sandwich', price: 140, tax: 5, description: '', icon: '🥪', status: 'available', archived: false },
  { id: 'p26', categoryId: 'snacks', name: 'Fries', price: 110, tax: 5, description: '', icon: '🍟', status: 'available', archived: false },
  { id: 'p27', categoryId: 'snacks', name: 'Nachos', price: 160, tax: 5, description: '', icon: '🥪', status: 'available', archived: false },
  { id: 'p28', categoryId: 'snacks', name: 'Garlic Bread', price: 130, tax: 5, description: '', icon: '🥪', status: 'low', archived: false },

  { id: 'p29', categoryId: 'meals', name: 'Combo Meal', price: 350, tax: 18, description: '', icon: '🍱', status: 'available', archived: false },
  { id: 'p30', categoryId: 'meals', name: 'Thali', price: 300, tax: 18, description: '', icon: '🍱', status: 'available', archived: false },
  { id: 'p31', categoryId: 'meals', name: 'Pasta', price: 280, tax: 18, description: '', icon: '🍝', status: 'available', archived: false },
  { id: 'p32', categoryId: 'meals', name: 'Salad Bowl', price: 220, tax: 5, description: '', icon: '🥗', status: 'unavailable', archived: false },

  { id: 'p33', categoryId: 'icecream', name: 'Vanilla Scoop', price: 90, tax: 5, description: '', icon: '🍨', status: 'available', archived: false },
  { id: 'p34', categoryId: 'icecream', name: 'Choco Lava', price: 150, tax: 5, description: '', icon: '🍨', status: 'available', archived: false },
  { id: 'p35', categoryId: 'icecream', name: 'Sundae', price: 180, tax: 5, description: '', icon: '🍨', status: 'low', archived: false },
  { id: 'p36', categoryId: 'icecream', name: 'Cone', price: 70, tax: 5, description: '', icon: '🍦', status: 'available', archived: false },
]

export const PAYMENT_TYPES = ['cash', 'card', 'upi']

export const PAYMENT_TYPE_ICONS = {
  cash: '💵',
  card: '💳',
  upi: '📱',
}

export const INITIAL_PAYMENT_METHODS = [
  { id: 'pm-cash', name: 'Cash', type: 'cash', upiId: '', active: true },
  { id: 'pm-card', name: 'Card', type: 'card', upiId: '', active: true },
  { id: 'pm-upi', name: 'UPI', type: 'upi', upiId: 'abc@upi.com', active: true },
]

export const DRAWER_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: '🏠' },
  { id: 'products', label: 'Products', icon: '📦' },
  { id: 'categories', label: 'Category', icon: '🏷' },
  { id: 'paymentMethods', label: 'Payment Method', icon: '💳' },
  { id: 'promotions', label: 'Coupon & Promotion', icon: '🎁' },
  { id: 'employees', label: 'User/Employee', icon: '👥' },
  { id: 'kitchen', label: 'KDS', icon: '🍳' },
  { id: 'reports', label: 'Reports', icon: '📈' },
  { id: 'aiInsights', label: 'AI Insights', icon: '✨' },
  { id: 'logout', label: 'Log-Out', icon: '🚪' },
]

export const STATUS_META = {
  available: { color: '#4ADE80', label: 'Available' },
  low: { color: '#FACC15', label: 'Low Stock' },
  unavailable: { color: '#FB7185', label: 'Unavailable' },
}

export const ORDER_STATUS_META = {
  draft: { label: 'Draft', bg: 'rgba(255,255,255,0.14)', color: '#F6EFE7' },
  paid: { label: 'Paid', bg: 'linear-gradient(135deg, #6F4E37, #3B2417)', color: '#F6EFE7' },
}

export const INITIAL_CUSTOMERS = [
  { id: 'c1', name: 'Pramod', email: 'pramod@odoo.com', phone: '+91 9876543210', points: 450 },
  { id: 'c2', name: 'Eric', email: 'eric@odoo.com', phone: '+91 9898989898', points: 120 },
  { id: 'c3', name: 'Sara', email: 'sara@odoo.com', phone: '+91 9988776655', points: 80 },
  { id: 'c4', name: 'Alex', email: 'alex@odoo.com', phone: '+91 9123456780', points: 300 },
  { id: 'c5', name: 'Dowel', email: 'dowel@odoo.com', phone: '+91 9012345678', points: 60 },
]

export const USER_TYPES = ['user', 'employee']

export const USER_STATUS_META = {
  active: { label: 'Active', bg: 'rgba(74,222,128,0.18)', color: '#4ADE80' },
  disabled: { label: 'Disable', bg: 'rgba(255,255,255,0.14)', color: 'rgba(246,239,231,0.7)' },
}

export const INITIAL_USERS = [
  { id: 'u1', name: 'Admin', type: 'user', status: 'active' },
  { id: 'u2', name: 'Eric', type: 'employee', status: 'active' },
  { id: 'u3', name: 'Sara', type: 'user', status: 'disabled' },
]

export const INITIAL_ORDERS = [
  { id: '00001', date: '4/5 11:27', customer: 'Admin', amount: 540, status: 'draft', items: [] },
  { id: '00002', date: '4/5 11:27', customer: 'Eric', amount: 540, status: 'paid', items: [] },
  { id: '00003', date: '4/5 11:27', customer: 'Alex', amount: 540, status: 'draft', items: [] },
  { id: '00004', date: '4/5 11:27', customer: 'Sara', amount: 540, status: 'paid', items: [] },
  { id: '00005', date: '4/5 11:27', customer: 'Dowel', amount: 540, status: 'paid', items: [] },
]
