import { useState } from 'react'
import { ORDER_STATUS_META } from './data'
import './OrdersPage.css'

export default function OrdersPage({ orders, onEditOrder, onDeleteOrder }) {
  const [query, setQuery] = useState('')
  const [detailId, setDetailId] = useState(null)

  const q = query.trim().toLowerCase()
  const filtered = orders.filter((order) => {
    if (!q) return true
    const customer = order.customer || order.customer_name || 'Guest'
    const id = String(order.id || order.order_number || '')
    const date = String(order.date || order.created_at || '')
    return (
      customer.toLowerCase().includes(q) ||
      id.toLowerCase().includes(q) ||
      date.toLowerCase().includes(q)
    )
  })

  const detailOrder = orders.find((o) => o.id === detailId) || null

  return (
    <section className="orders-page">
      <h1 className="orders-title">Order</h1>

      <div className="orders-search">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by customer, order number or date..."
        />
        <span className="search-icon" aria-hidden="true">🔍</span>
      </div>

      <div className="orders-table">
        <div className="orders-row orders-head">
          <span>Date</span>
          <span>Order</span>
          <span>Customer</span>
          <span>Amount</span>
          <span>Status</span>
        </div>
        {filtered.map((order) => {
          const statusKey = order.status in ORDER_STATUS_META ? order.status : 'draft'
          const status = ORDER_STATUS_META[statusKey]
          const displayId = String(order.id || order.order_number || '')
          const displayCustomer = order.customer || order.customer_name || 'Guest'
          const displayDate = order.date || (order.created_at ? new Date(order.created_at).toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }) : '-')
          const displayAmount = order.amount ?? order.total_amount ?? 0
          return (
            <button
              key={order.id || order.order_number}
              type="button"
              className="orders-row orders-data"
              onClick={() => setDetailId(displayId)}
            >
              <span>{displayDate}</span>
              <span className="order-link">{displayId}</span>
              <span>{displayCustomer}</span>
              <span className="order-amount">₹{displayAmount}</span>
              <span className="status-pill" style={{ background: status.bg, color: status.color }}>
                {status.label}
              </span>
            </button>
          )
        })}
        {filtered.length === 0 && <p className="orders-empty">No orders found.</p>}
      </div>

      {detailOrder && (
        <div className="orders-modal-backdrop" onClick={() => setDetailId(null)}>
          <div className="orders-modal" onClick={(e) => e.stopPropagation()}>
            <button type="button" className="orders-modal-close" onClick={() => setDetailId(null)}>✕</button>
            <h3>Order #{detailOrder.id}</h3>
            <div className="orders-modal-grid">
              <div>
                <span className="field-label">Date</span>
                <span>{detailOrder.date || detailOrder.created_at || '-'}</span>
              </div>
              <div>
                <span className="field-label">Customer</span>
                <span>{detailOrder.customer || detailOrder.customer_name || 'Guest'}</span>
              </div>
              <div>
                <span className="field-label">Amount</span>
                <span className="order-amount">₹{detailOrder.amount ?? detailOrder.total_amount ?? 0}</span>
              </div>
              <div>
                <span className="field-label">Status</span>
                <span
                  className="status-pill"
                  style={{ background: ORDER_STATUS_META[detailOrder.status in ORDER_STATUS_META ? detailOrder.status : 'draft'].bg, color: ORDER_STATUS_META[detailOrder.status in ORDER_STATUS_META ? detailOrder.status : 'draft'].color }}
                >
                  {ORDER_STATUS_META[detailOrder.status in ORDER_STATUS_META ? detailOrder.status : 'draft'].label}
                </span>
              </div>
            </div>

            <span className="field-label">Products</span>
            <div className="orders-modal-products">
              {detailOrder.items.length === 0 && <p className="orders-empty">No product details for this order.</p>}
              {detailOrder.items.map((item) => (
                <div className="orders-modal-product-row" key={item.cartItemId || item.productId}>
                  <span>{item.name} × {item.qty}</span>
                  <span>₹{item.price * item.qty}</span>
                </div>
              ))}
            </div>

            {detailOrder.status === 'draft' ? (
              <button
                type="button"
                className="orders-modal-action edit"
                onClick={() => {
                  onEditOrder(detailOrder)
                  setDetailId(null)
                }}
              >
                Edit Order
              </button>
            ) : (
              <button
                type="button"
                className="orders-modal-action delete"
                onClick={() => {
                  onDeleteOrder(detailOrder.id)
                  setDetailId(null)
                }}
              >
                Delete
              </button>
            )}
          </div>
        </div>
      )}
    </section>
  )
}
