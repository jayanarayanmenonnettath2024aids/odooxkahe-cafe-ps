import { useState } from 'react'
import { createPortal } from 'react-dom'
import { CATEGORY_COLORS } from './data'

export default function CategoryFormModal({ initialName, onSave, onDiscard }) {
  const [name, setName] = useState(initialName || '')
  const [color, setColor] = useState(CATEGORY_COLORS[0])
  const [nameError, setNameError] = useState(false)

  const handleSave = () => {
    if (!name.trim()) {
      setNameError(true)
      return
    }
    onSave({ name: name.trim(), color })
  }

  return createPortal(
    <div className="category-edit-backdrop" onClick={onDiscard}>
      <div className="category-edit-modal" onClick={(e) => e.stopPropagation()}>
        <button type="button" className="category-edit-close" onClick={onDiscard}>✕</button>
        <h4>Category</h4>
        <div className="category-edit-row">
          <label className="category-edit-field">
            <span className="field-label">Category Name</span>
            <input
              type="text"
              className={nameError ? 'error' : ''}
              placeholder="e.g Food"
              value={name}
              onChange={(e) => {
                setName(e.target.value)
                if (nameError) setNameError(false)
              }}
            />
            {nameError && <span className="customer-edit-error">Name is required</span>}
          </label>
          <div className="category-color-field">
            <span className="field-label">Color</span>
            <div className="category-color-swatches">
              {CATEGORY_COLORS.map((c) => (
                <button
                  key={c}
                  type="button"
                  className={`color-swatch ${color === c ? 'selected' : ''}`}
                  style={{ background: c }}
                  onClick={() => setColor(c)}
                  aria-label={`Color ${c}`}
                />
              ))}
            </div>
          </div>
        </div>
        <div className="category-edit-actions">
          <button type="button" className="save-btn" onClick={handleSave}>Save</button>
          <button type="button" className="discard-btn" onClick={onDiscard}>Discard</button>
        </div>
      </div>
    </div>,
    document.body,
  )
}
