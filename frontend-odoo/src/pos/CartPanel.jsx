export default function CartPanel({
  cart,
  orderNumber,
  orderTime,
  kitchenStatus,
  selectedCartItemId,
  onSelectCartItem,
  onIncQty,
  onDecQty,
  onRemoveItem,
  onNoteChange,
  onSendToKitchen,
  onOpenCustomer,
  onOpenCouponPopup,
  onSendReceipt,
  subtotal,
  gst,
  serviceTax,
  discountAmount,
  total,
}) {
  return (
    <section className="cart-section">
      <div className="cart-header">
        <span className="cart-title">🛒 Current Order</span>
        <span className="cart-order-no">#{String(orderNumber).padStart(5, '0')}</span>
        <span className="cart-time">{orderTime}</span>
        {kitchenStatus === 'sent' && <span className="kitchen-badge">👨‍🍳 In Kitchen</span>}
      </div>

      <div className="cart-items">
        {cart.length === 0 && <p className="cart-empty">Tap a product to add it to the order.</p>}
        {cart.map((item) => (
          <div
            key={item.cartItemId}
            className={`cart-item ${selectedCartItemId === item.cartItemId ? 'selected' : ''}`}
            onClick={() => onSelectCartItem(item.cartItemId)}
          >
            <div className="cart-item-top">
              <span className="cart-item-name">{item.name}</span>
              <span className="cart-item-line-price">₹{item.price * item.qty}</span>
            </div>
            <div className="cart-item-bottom">
              <span className="cart-item-unit">₹{item.price} each</span>
              <div className="qty-controls" onClick={(e) => e.stopPropagation()}>
                <button type="button" onClick={() => onDecQty(item.cartItemId)}>−</button>
                <span>{item.qty}</span>
                <button type="button" onClick={() => onIncQty(item.cartItemId)}>+</button>
              </div>
              <button
                type="button"
                className="remove-item-btn"
                onClick={(e) => {
                  e.stopPropagation()
                  onRemoveItem(item.cartItemId)
                }}
              >
                ✕
              </button>
            </div>
            <input
              type="text"
              className="note-input"
              placeholder="Special instructions (e.g. No Sugar)"
              value={item.note}
              onClick={(e) => e.stopPropagation()}
              onChange={(e) => onNoteChange(item.cartItemId, e.target.value)}
            />
          </div>
        ))}
      </div>

      <button type="button" className="send-kitchen-btn" onClick={onSendToKitchen} disabled={cart.length === 0}>
        👨‍🍳 Send To Kitchen
      </button>

      <div className="cart-utility-row">
        <button type="button" onClick={onOpenCustomer}>
          <span>👤</span>Customer
        </button>
        <button type="button" onClick={onOpenCouponPopup}>
          <span>💲</span>Discount
        </button>
        <button type="button" onClick={onSendReceipt}>
          <span>📨</span>Send
        </button>
      </div>

      <div className="bill-summary">
        <div className="bill-row">
          <span>Sub Total</span>
          <span>₹{subtotal.toFixed(0)}</span>
        </div>
        <div className="bill-row">
          <span>GST (5%)</span>
          <span>₹{gst.toFixed(0)}</span>
        </div>
        <div className="bill-row">
          <span>Service Tax</span>
          <span>₹{serviceTax.toFixed(0)}</span>
        </div>
        <div className="bill-row">
          <span>Discount</span>
          <span>−₹{discountAmount.toFixed(0)}</span>
        </div>
        <div className="bill-row bill-total">
          <span>Total</span>
          <span>₹{total.toFixed(0)}</span>
        </div>
      </div>
    </section>
  )
}
