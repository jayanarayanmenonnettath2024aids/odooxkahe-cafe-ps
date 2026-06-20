import { useState, useEffect } from 'react';
import MenuScreen from './MenuScreen';
import CartCheckoutScreen from './CartCheckoutScreen';
import OrderTrackingScreen from './OrderTrackingScreen';
import './SelfOrderApp.css';

const API_BASE = 'http://localhost:8000/api/v1';

export default function SelfOrderApp({ tableToken }) {
  const [config, setConfig] = useState(null);
  const [table, setTable] = useState(null);
  const [view, setView] = useState('splash'); // splash, menu, cart, tracking
  const [cart, setCart] = useState([]);
  const [orderId, setOrderId] = useState(null);
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);

  useEffect(() => {
    async function init() {
      try {
        const [configRes, tableRes, catRes, prodRes] = await Promise.all([
          fetch(`${API_BASE}/s/config`).then(r => r.json()),
          fetch(`${API_BASE}/s/${tableToken}`).then(r => r.json()),
          fetch(`${API_BASE}/categories`).then(r => r.json()),
          fetch(`${API_BASE}/products`).then(r => r.json())
        ]);
        setConfig(configRes.data);
        setTable(tableRes.data);
        setCategories(catRes || []);
        setProducts(prodRes || []);
        
        // Show splash screen for 2 seconds
        setTimeout(() => setView('menu'), 2000);
      } catch (err) {
        console.error("Failed to load self-ordering data:", err);
      }
    }
    init();
  }, [tableToken]);

  const addToCart = (product) => {
    setCart((prev) => {
      const existing = prev.find(item => item.product_id === product.id);
      if (existing) {
        return prev.map(item => item.product_id === product.id ? { ...item, quantity: item.quantity + 1 } : item);
      }
      return [...prev, { product_id: product.id, name: product.name, price: product.price, quantity: 1 }];
    });
  };

  const updateQuantity = (productId, delta) => {
    setCart((prev) => prev.map(item => {
      if (item.product_id === productId) {
        return { ...item, quantity: Math.max(0, item.quantity + delta) };
      }
      return item;
    }).filter(item => item.quantity > 0));
  };

  if (!config || !table) {
    return <div className="self-order-loading">Loading...</div>;
  }

  if (view === 'splash') {
    return (
      <div className="self-order-splash" style={{ backgroundColor: config.splash_background_color || '#D4A056' }}>
        {config.splash_image_url && <img src={config.splash_image_url} alt="Splash" className="splash-image" />}
        <h1>{config.store_name || 'Cafe POS'}</h1>
        <p>Table: {table.table_number}</p>
      </div>
    );
  }

  return (
    <div className="self-order-app">
      <header className="self-order-header" style={{ backgroundColor: config.splash_background_color || '#D4A056' }}>
        <h2>{config.store_name}</h2>
        <span>Table {table.table_number}</span>
      </header>

      <main className="self-order-content">
        {view === 'menu' && (
          <MenuScreen 
            categories={categories} 
            products={products} 
            cart={cart} 
            addToCart={addToCart} 
            onViewCart={() => setView('cart')} 
          />
        )}
        {view === 'cart' && (
          <CartCheckoutScreen 
            cart={cart} 
            updateQuantity={updateQuantity}
            onBack={() => setView('menu')}
            onOrderPlaced={(id) => {
              setOrderId(id);
              setView('tracking');
            }}
            tableToken={tableToken}
            config={config}
          />
        )}
        {view === 'tracking' && (
          <OrderTrackingScreen 
            orderId={orderId}
            onNewOrder={() => {
              setCart([]);
              setOrderId(null);
              setView('menu');
            }}
          />
        )}
      </main>
    </div>
  );
}
