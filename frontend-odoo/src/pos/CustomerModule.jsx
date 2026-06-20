import { useState } from 'react'
import { createPortal } from 'react-dom'

const emptyDraft = { name: '', email: '', phone: '' }

export default function CustomerModule({ customers, activeCustomerId, onSelectCustomer, onSaveCustomer, onDeleteCustomer }) {
  const [query, setQuery] = useState('')
  const [openMenuId, setOpenMenuId] = useState(null)
  const [editing, setEditing] = useState(null) // { id: string|null, name, email, phone }
  const [nameError, setNameError] = useState(false)

  const q = query.trim().toLowerCase()
  const filtered = customers.filter((c) =>
    !q || c.name.toLowerCase().includes(q) || c.email.toLowerCase().includes(q) || c.phone.toLowerCase().includes(q),
  )

  const startEdit = (customer) => {
    setEditing(customer ? { ...customer } : { id: null, ...emptyDraft })
    setNameError(false)
    setOpenMenuId(null)
  }

  const handleSave = () => {
    if (!editing.name.trim()) {
      setNameError(true)
      return
    }
    onSaveCustomer(editing.id, { name: editing.name.trim(), email: editing.email.trim(), phone: editing.phone.trim() })
    setEditing(null)
  }

  const handleDelete = () => {
    onDeleteCustomer(editing.id)
    setEditing(null)
  }

  return (
    <div className="customer-module">
      <div className="customer-module-header">
        <span className="customer-module-title"><span className="customer-module-icon">🪪</span> Customer</span>
      </div>

      <div className="customer-toolbar">
        <button type="button" className="customer-add-btn" title="New customer" onClick={() => startEdit(null)}>➕</button>
        <div className="customer-search">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search customer..."
          />
          <span className="search-icon" aria-hidden="true">🔍</span>
        </div>
      </div>

      <div className="customer-list">
        {filtered.map((c) => (
          <div key={c.id} className={`customer-row ${activeCustomerId === c.id ? 'active' : ''}`}>
            <div
              className="customer-row-main"
              onClick={() => onSelectCustomer(c.id)}
            >
              <span className="customer-row-name">{c.name}</span>
              <span className="customer-row-line">📧 {c.email}</span>
              <span className="customer-row-line">📞 {c.phone}</span>
            </div>
            <div className="customer-row-menu">
              <button
                type="button"
                className="customer-kebab"
                onClick={(e) => {
                  e.stopPropagation()
                  setOpenMenuId((prev) => (prev === c.id ? null : c.id))
                }}
              >
                ⋮
              </button>
              {openMenuId === c.id && (
                <div className="customer-kebab-menu">
                  <button type="button" onClick={() => startEdit(c)}>Edit</button>
                </div>
              )}
            </div>
          </div>
        ))}
        {filtered.length === 0 && <p className="customer-empty">No customers found.</p>}
      </div>

      {editing && createPortal(
        <div className="customer-edit-backdrop" onClick={() => setEditing(null)}>
          <div className="customer-edit-modal" onClick={(e) => e.stopPropagation()}>
            <button type="button" className="customer-edit-close" onClick={() => setEditing(null)}>✕</button>
            <input
              type="text"
              className={`customer-edit-name ${nameError ? 'error' : ''}`}
              placeholder="e.g Eric Smith"
              value={editing.name}
              onChange={(e) => {
                setEditing({ ...editing, name: e.target.value })
                if (nameError) setNameError(false)
              }}
            />
            {nameError && <span className="customer-edit-error">Name is required</span>}
            <label className="customer-edit-field">
              <span>📧</span>
              <input
                type="email"
                placeholder="email@odoo.com"
                value={editing.email}
                onChange={(e) => setEditing({ ...editing, email: e.target.value })}
              />
            </label>
            <label className="customer-edit-field">
              <span>📞</span>
              <input
                type="tel"
                placeholder="+91 9898989898"
                value={editing.phone}
                onChange={(e) => setEditing({ ...editing, phone: e.target.value })}
              />
            </label>
            <div className="customer-edit-actions">
              <button type="button" className="discard-btn" onClick={() => setEditing(null)}>Discard</button>
              <button type="button" className="save-btn" onClick={handleSave}>Save</button>
            </div>
            {editing.id && (
              <button type="button" className="customer-delete-btn" onClick={handleDelete}>DELETE</button>
            )}
          </div>
        </div>,
        document.body,
      )}
    </div>
  )
}
