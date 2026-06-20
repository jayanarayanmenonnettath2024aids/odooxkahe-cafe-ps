import { useState, useMemo } from 'react';

const API_BASE = 'http://localhost:8000/api/v1';

export default function CartCheckoutScreen({ cart, updateQuantity, onBack, onOrderPlaced, tableToken, config }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const total = useMemo(() => cart.reduce((sum, item) => sum + (item.price * item.quantity), 0), [cart]);

  const placeOrder = async (paidOnline = false, rzpRef = null) => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE}/s/${tableToken}/order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          table_token: tableToken,
          items: cart.map(i => ({ product_id: i.product_id, quantity: i.quantity })),
          payment_mode: paidOnline ? 'ONLINE' : 'PAY_AT_COUNTER',
          transaction_reference: rzpRef
        })
      });
      const data = await res.json();
      if (res.ok) {
        onOrderPlaced(data.data.order_id);
      } else {
        throw new Error(data.detail || 'Failed to place order');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadRazorpayScript = () => {
    return new Promise((resolve) => {
      if (window.Razorpay) return resolve(true);
      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  };

  const handlePayOnline = async () => {
    setLoading(true);
    setError('');
    try {
      const isLoaded = await loadRazorpayScript();
      if (!isLoaded) throw new Error('Failed to load payment gateway');

      // 1. Create order
      const orderRes = await fetch(`${API_BASE}/pos/razorpay/create-order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount: total })
      });
      const orderData = await orderRes.json();
      
      if (!orderRes.ok) throw new Error(orderData.detail || 'Failed to create payment session');

      const options = {
        key: orderData.data.key,
        amount: orderData.data.amount,
        currency: "INR",
        name: config.store_name || "Cafe POS",
        description: "Mobile Order",
        order_id: orderData.data.razorpay_order_id,
        handler: async function (response) {
          try {
            // Verify signature
            const verifyRes = await fetch(`${API_BASE}/pos/razorpay/verify`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature
              })
            });
            if (!verifyRes.ok) throw new Error("Payment verification failed");
            
            // Place order with PAID status
            await placeOrder(true, response.razorpay_payment_id);
          } catch (e) {
            setError(e.message);
          }
        },
        theme: { color: config.splash_background_color || "#D4A056" }
      };

      const rzp = new window.Razorpay(options);
      rzp.on('payment.failed', function (response){
        setError('Payment Failed: ' + response.error.description);
      });
      rzp.open();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (cart.length === 0) {
    return (
      <div className="cart-screen">
        <div className="cart-header">
          <button className="back-btn" onClick={onBack}>←</button>
          <h2>Your Cart</h2>
        </div>
        <div className="empty-cart">Your cart is empty.</div>
      </div>
    );
  }

  return (
    <div className="cart-screen">
      <div className="cart-header">
        <button className="back-btn" onClick={onBack}>←</button>
        <h2>Your Cart</h2>
      </div>

      <div className="cart-items">
        {cart.map(item => (
          <div key={item.product_id} className="cart-item">
            <div className="cart-item-info">
              <h4>{item.name}</h4>
              <p>₹{item.price.toFixed(0)}</p>
            </div>
            <div className="qty-controls">
              <button onClick={() => updateQuantity(item.product_id, -1)}>−</button>
              <span>{item.quantity}</span>
              <button onClick={() => updateQuantity(item.product_id, 1)}>+</button>
            </div>
          </div>
        ))}
      </div>

      <div className="cart-summary">
        <div className="summary-row total">
          <span>Total</span>
          <span>₹{total.toFixed(0)}</span>
        </div>
      </div>

      {error && <div style={{ color: 'red', marginTop: '1rem', textAlign: 'center' }}>{error}</div>}

      <div className="payment-options">
        {config.online_ordering_enabled !== false && (
          <button className="pay-btn pay-online" disabled={loading} onClick={handlePayOnline}>
            {loading ? 'Processing...' : `Pay Online (₹${total.toFixed(0)})`}
          </button>
        )}
        
        {config.pay_at_counter_enabled !== false && (
          <button className="pay-btn pay-counter" disabled={loading} onClick={() => placeOrder(false)}>
            {loading ? 'Processing...' : 'Place Order & Pay at Counter'}
          </button>
        )}
      </div>
    </div>
  );
}
