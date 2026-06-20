import { PAYMENT_TYPE_ICONS } from './data'

const KEYPAD_ROWS = [
  ['1', '2', '3'],
  ['4', '5', '6'],
  ['7', '8', '9'],
  ['+/-', '0', 'C'],
]

export default function PaymentPanel({
  paymentMethods,
  paymentMethod,
  onSelectPaymentMethod,
  total,
  loyaltyPoints,
  keypadMode,
  onSetKeypadMode,
  displayValue,
  onDigit,
  onAction,
  selectedItemName,
  splitCount,
  splitOpen,
  onToggleSplit,
  onChangeSplitCount,
  changeDue,
  onCompletePayment,
  completeDisabled,
}) {
  const activeMethods = paymentMethods.filter((m) => m.active)
  const selectedMethod = paymentMethods.find((m) => m.id === paymentMethod)

  return (
    <section className="payment-section">
      <div className="payment-methods">
        {activeMethods.map((method) => (
          <button
            key={method.id}
            type="button"
            className={`payment-method-btn ${paymentMethod === method.id ? 'active' : ''}`}
            onClick={() => onSelectPaymentMethod(method.id)}
          >
            <span className="payment-icon">{PAYMENT_TYPE_ICONS[method.type]}</span>
            {method.name}
          </button>
        ))}
      </div>

      {selectedMethod?.type === 'upi' && (
        <div className="qr-box">
          <div className="qr-pattern" aria-hidden="true">▦</div>
          <span>Scan to Pay{selectedMethod.upiId ? ` · ${selectedMethod.upiId}` : ''}</span>
        </div>
      )}

      <div className="amount-display">
        <span className="amount-label">Amount</span>
        <span className="amount-value">₹{total.toFixed(0)}</span>
        <span className="amount-sub">
          {keypadMode === 'amount' && `Tendered: ₹${displayValue || 0}`}
          {keypadMode === 'qty' && (selectedItemName ? `Qty for ${selectedItemName}: ${displayValue || 0}` : 'Select a cart item to edit qty')}
        </span>
        {changeDue !== null && (
          <span className={`change-due ${changeDue < 0 ? 'negative' : ''}`}>
            {changeDue < 0 ? `Balance Due: ₹${Math.abs(changeDue).toFixed(0)}` : `Change: ₹${changeDue.toFixed(0)}`}
          </span>
        )}
        <span className="loyalty-line">⭐ Points Earned +{loyaltyPoints} Points</span>
      </div>

      {splitOpen && (
        <div className="split-bill-box">
          <span>Split Bill</span>
          <div className="split-controls">
            <button type="button" onClick={() => onChangeSplitCount(Math.max(1, splitCount - 1))}>−</button>
            <span>{splitCount}</span>
            <button type="button" onClick={() => onChangeSplitCount(splitCount + 1)}>+</button>
          </div>
          <span className="split-result">₹{(total / splitCount).toFixed(0)} / person</span>
        </div>
      )}

      <div className="keypad-area">
        <div className="keypad-grid">
          {KEYPAD_ROWS.map((row, rowIdx) => (
            <div className="keypad-row" key={rowIdx}>
              {row.map((key) => (
                <button
                  key={key}
                  type="button"
                  className={`keypad-btn ${key === 'C' ? 'clear' : ''}`}
                  onClick={() => onDigit(key)}
                >
                  {key === 'C' ? '✕' : key}
                </button>
              ))}
            </div>
          ))}
        </div>
        <div className="keypad-side">
          <button type="button" className={keypadMode === 'amount' ? 'active' : ''} onClick={() => onSetKeypadMode('amount')}>
            Price
          </button>
          <button type="button" className={keypadMode === 'qty' ? 'active' : ''} onClick={() => onSetKeypadMode('qty')}>
            Qty
          </button>
        </div>
      </div>

      <div className="quick-buttons">
        <button type="button" onClick={() => onAction('quick-100')}>₹100</button>
        <button type="button" onClick={() => onAction('quick-500')}>₹500</button>
        <button type="button" onClick={() => onAction('quick-1000')}>₹1000</button>
        <button type="button" onClick={() => onAction('custom-price')}>Custom Price</button>
        <button type="button" className={splitOpen ? 'active' : ''} onClick={onToggleSplit}>Split Bill</button>
      </div>

      <button type="button" className="complete-payment-btn" disabled={completeDisabled} onClick={onCompletePayment}>
        ✅ Complete Payment
      </button>
    </section>
  )
}
