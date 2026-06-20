import { useState } from 'react'
import { PAYMENT_TYPES } from './data'

const emptyDraft = { name: '', type: PAYMENT_TYPES[0], upiId: '', active: true }

export default function PaymentMethodFormModal({ method, onSave, onDiscard }) {
  const [form, setForm] = useState(method ? { ...method } : { ...emptyDraft })
  const [nameError, setNameError] = useState(false)

  const handleSave = () => {
    if (!form.name.trim()) {
      setNameError(true)
      return
    }
    onSave({ ...form, name: form.name.trim(), upiId: form.upiId.trim() })
  }

  return (
    <div className="payment-method-edit-backdrop" onClick={onDiscard}>
      <div className="payment-method-edit-modal" onClick={(e) => e.stopPropagation()}>
        <button type="button" className="payment-method-edit-close" onClick={onDiscard}>✕</button>

        <label className="payment-method-edit-field">
          <span className="field-label">Payment method Name</span>
          <input
            type="text"
            className={nameError ? 'error' : ''}
            placeholder="e.g. UPI - Merchant"
            value={form.name}
            onChange={(e) => {
              setForm({ ...form, name: e.target.value })
              if (nameError) setNameError(false)
            }}
          />
          {nameError && <span className="customer-edit-error">Name is required</span>}
        </label>

        <label className="payment-method-edit-field">
          <span className="field-label">Type</span>
          <select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
            {PAYMENT_TYPES.map((t) => (
              <option key={t} value={t}>{t.toUpperCase()}</option>
            ))}
          </select>
        </label>

        {form.type === 'upi' && (
          <div className="upi-extra-box">
            <label className="payment-method-edit-field">
              <span className="field-label">UPI ID</span>
              <input
                type="text"
                placeholder="abc@upi.com"
                value={form.upiId}
                onChange={(e) => setForm({ ...form, upiId: e.target.value })}
              />
            </label>
            <span className="field-label">QR Preview</span>
            <div className="qr-preview-box">
              <span className="qr-preview-label">UPI QR</span>
              <div className="qr-preview-pattern" aria-hidden="true">▦</div>
              <span className="qr-preview-caption">SCAN ME</span>
            </div>
          </div>
        )}

        <label className="payment-method-activate">
          <input
            type="checkbox"
            checked={form.active}
            onChange={(e) => setForm({ ...form, active: e.target.checked })}
          />
          Activate
        </label>

        <div className="payment-method-edit-actions">
          <button type="button" className="discard-btn" onClick={onDiscard}>Discard</button>
          <button type="button" className="save-btn" onClick={handleSave}>Save</button>
        </div>
      </div>
    </div>
  )
}
