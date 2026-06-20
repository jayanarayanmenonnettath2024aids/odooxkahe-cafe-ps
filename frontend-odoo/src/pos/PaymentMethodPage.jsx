import { useState } from 'react'
import { PAYMENT_TYPES } from './data'
import PaymentMethodFormModal from './PaymentMethodFormModal'
import './PaymentMethodPage.css'

export default function PaymentMethodPage({ paymentMethods, onSavePaymentMethod, onDeletePaymentMethod, onReorderPaymentMethods }) {
  const [dragId, setDragId] = useState(null)
  const [editing, setEditing] = useState(null)
  const [formOpen, setFormOpen] = useState(false)

  const reorder = (targetId) => {
    if (!dragId || dragId === targetId) return
    const next = [...paymentMethods]
    const fromIndex = next.findIndex((m) => m.id === targetId)
    const movedIndex = next.findIndex((m) => m.id === dragId)
    const [moved] = next.splice(movedIndex, 1)
    next.splice(fromIndex, 0, moved)
    onReorderPaymentMethods(next)
    setDragId(null)
  }

  const openNew = () => {
    setEditing(null)
    setFormOpen(true)
  }

  const openEdit = (method) => {
    setEditing(method)
    setFormOpen(true)
  }

  const handleSave = (fields) => {
    onSavePaymentMethod(editing?.id, fields)
    setFormOpen(false)
  }

  return (
    <section className="payment-method-page">
      <span className="payment-method-page-eyebrow">Products</span>
      <h1 className="payment-method-page-title">Payment Method</h1>

      <button type="button" className="payment-method-new-btn" onClick={openNew}>
        <span>🗋+</span> New
      </button>

      <div className="payment-method-table">
        <div className="payment-method-row payment-method-head">
          <span />
          <span>Name</span>
          <span>Type</span>
          <span>Id</span>
          <span>Activate</span>
          <span />
        </div>
        {paymentMethods.map((m) => (
          <div
            key={m.id}
            className={`payment-method-row payment-method-data ${dragId === m.id ? 'dragging' : ''}`}
            draggable
            onDragStart={() => setDragId(m.id)}
            onDragOver={(e) => e.preventDefault()}
            onDrop={() => reorder(m.id)}
          >
            <span className="drag-handle">⠿⠿</span>
            <span className="payment-method-name" onClick={() => openEdit(m)}>{m.name}</span>
            <select
              value={m.type}
              onChange={(e) => onSavePaymentMethod(m.id, { type: e.target.value })}
            >
              {PAYMENT_TYPES.map((t) => (
                <option key={t} value={t}>{t.toUpperCase()}</option>
              ))}
            </select>
            <input
              type="text"
              className="payment-method-id-input"
              placeholder={m.type === 'upi' ? 'abc@upi.com' : '—'}
              disabled={m.type !== 'upi'}
              value={m.upiId}
              onChange={(e) => onSavePaymentMethod(m.id, { upiId: e.target.value })}
            />
            <input
              type="checkbox"
              checked={m.active}
              onChange={(e) => onSavePaymentMethod(m.id, { active: e.target.checked })}
            />
            <button type="button" className="payment-method-delete-btn" onClick={() => onDeletePaymentMethod(m.id)} title="Delete">
              🗑
            </button>
          </div>
        ))}
        {paymentMethods.length === 0 && <p className="payment-method-empty">No payment methods yet. Click New to add one.</p>}
      </div>

      {formOpen && (
        <PaymentMethodFormModal
          method={editing}
          onSave={handleSave}
          onDiscard={() => setFormOpen(false)}
        />
      )}
    </section>
  )
}
