import { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000/api/v1';

export default function OrderTrackingScreen({ orderId, onNewOrder }) {
  const [status, setStatus] = useState('DRAFT');

  useEffect(() => {
    if (!orderId) return;

    // Initial fetch
    fetch(`${API_BASE}/s/order/${orderId}/status`)
      .then(r => r.json())
      .then(res => setStatus(res.data.status));

    const interval = setInterval(() => {
      fetch(`${API_BASE}/s/order/${orderId}/status`)
        .then(r => r.json())
        .then(res => setStatus(res.data.status))
        .catch(console.error);
    }, 5000); // poll every 5s

    return () => clearInterval(interval);
  }, [orderId]);

  const getStatusText = () => {
    switch (status) {
      case 'DRAFT': return 'Order Placed';
      case 'SENT_TO_KITCHEN': return 'Sent to Kitchen';
      case 'PREPARING': return 'Preparing Food';
      case 'READY': return 'Food is Ready!';
      case 'PAID': return 'Order Paid';
      default: return 'Processing...';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'DRAFT': return '📝';
      case 'SENT_TO_KITCHEN': return '👨‍🍳';
      case 'PREPARING': return '🔥';
      case 'READY': return '✅';
      case 'PAID': return '🎉';
      default: return '⏳';
    }
  };

  return (
    <div className="tracking-screen">
      <div className="status-circle">
        {getStatusIcon()}
      </div>
      <h2>{getStatusText()}</h2>
      <p>Order #{orderId}</p>
      
      <button className="new-order-btn" onClick={onNewOrder}>
        Place Another Order
      </button>
    </div>
  );
}
