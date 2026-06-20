import { useState, useEffect } from 'react';
import './CustomerDisplayApp.css';

const API_BASE = 'http://localhost:8000/api/v1';

export default function CustomerDisplayApp() {
  const [config, setConfig] = useState(null);
  const [order, setOrder] = useState(null);
  const sessionId = localStorage.getItem('pos_session_id') || '1'; // Ideally passed from cashier

  useEffect(() => {
    // 1. Fetch store config for marketing side
    fetch(`${API_BASE}/s/config`)
      .then(r => r.json())
      .then(res => setConfig(res.data))
      .catch(console.error);

    // 2. Connect to WebSocket
    const wsUrl = `ws://localhost:8000/api/v1/ws/customer_display:session:${sessionId}`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === 'active_order_changed') {
        if (data.data && data.data.cart_data) {
          setOrder(data.data.cart_data);
        } else if (data.data && data.data.order_id) {
          fetchOrder(data.data.order_id);
        }
      }
    };

    return () => ws.close();
  }, [sessionId]);

  const fetchOrder = async (orderId) => {
    try {
      const res = await fetch(`${API_BASE}/customer-display/${orderId}`);
      const data = await res.json();
      setOrder(data.data);
    } catch (err) {
      console.error("Failed to fetch order", err);
    }
  };

  const marketingSide = (
    <div className="cd-marketing" style={{ backgroundColor: config?.splash_background_color || '#D4A056' }}>
      {config?.splash_image_url ? (
        <img src={config.splash_image_url} alt="Promo" className="cd-promo-image" />
      ) : (
        <div className="cd-welcome">
          <h1>Welcome to {config?.store_name || 'Cafe POS'}</h1>
          <p>Scan the QR code on your table to order, or order at the counter.</p>
        </div>
      )}
    </div>
  );

  if (!order || !order.items || order.items.length === 0) {
    return (
      <div className="customer-display empty">
        {marketingSide}
        <div className="cd-cart-side">
          <div className="cd-empty-state">
            <h2>Welcome!</h2>
            <p>Your order will appear here</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="customer-display">
      {marketingSide}
      <div className="cd-cart-side">
        <div className="cd-header">
          <h2>{order.order_number ? `Order #${order.order_number}` : 'Current Order'}</h2>
        </div>
        
        <div className="cd-items">
          {order.items.map((item, idx) => (
            <div key={idx} className="cd-item">
              <div className="cd-item-qty">{item.quantity || item.qty}x</div>
              <div className="cd-item-name">{item.product_name || item.name}</div>
              <div className="cd-item-price">₹{((item.unit_price || item.price) * (item.quantity || item.qty)).toFixed(0)}</div>
            </div>
          ))}
        </div>

        <div className="cd-summary">
          <div className="cd-row">
            <span>Subtotal</span>
            <span>₹{order.subtotal.toFixed(0)}</span>
          </div>
          <div className="cd-row">
            <span>Tax</span>
            <span>₹{order.tax_amount.toFixed(0)}</span>
          </div>
          {order.discount_amount > 0 && (
            <div className="cd-row discount">
              <span>Discount</span>
              <span>-₹{order.discount_amount.toFixed(0)}</span>
            </div>
          )}
          <div className="cd-row total">
            <span>Total To Pay</span>
            <span>₹{order.total_amount.toFixed(0)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
