import { useEffect, useRef, useState } from 'react'
import { CATEGORY_COLORS } from './data'
import './CategoryPage.css'

export default function CategoryPage({ categories, onAddCategory, onUpdateCategory, onDeleteCategory, onReorderCategories }) {
  const [dragId, setDragId] = useState(null)
  const lastInputRef = useRef(null)
  const prevLengthRef = useRef(categories.length)

  useEffect(() => {
    if (categories.length > prevLengthRef.current) {
      lastInputRef.current?.focus()
    }
    prevLengthRef.current = categories.length
  }, [categories.length])

  const handleDrop = (targetId) => {
    if (!dragId || dragId === targetId) return
    const next = [...categories]
    const fromIndex = next.findIndex((c) => c.id === dragId)
    const toIndex = next.findIndex((c) => c.id === targetId)
    const [moved] = next.splice(fromIndex, 1)
    next.splice(toIndex, 0, moved)
    onReorderCategories(next)
    setDragId(null)
  }

  return (
    <section className="category-page">
      <span className="category-page-eyebrow">Products</span>
      <h1 className="category-page-title">Category</h1>

      <button type="button" className="category-new-btn" onClick={onAddCategory}>
        <span>🗋+</span> New
      </button>

      <div className="category-table">
        <div className="category-table-row category-table-head">
          <span />
          <span>Product Category</span>
          <span>Color</span>
          <span />
        </div>
        {categories.map((c, index) => (
          <div
            key={c.id}
            className={`category-table-row category-table-data ${dragId === c.id ? 'dragging' : ''}`}
            draggable
            onDragStart={() => setDragId(c.id)}
            onDragOver={(e) => e.preventDefault()}
            onDrop={() => handleDrop(c.id)}
          >
            <span className="drag-handle">⠿⠿</span>
            <input
              ref={index === categories.length - 1 ? lastInputRef : null}
              type="text"
              className="category-name-input"
              placeholder="Category name"
              value={c.name}
              onChange={(e) => onUpdateCategory(c.id, { name: e.target.value })}
            />
            <div className="category-color-swatches">
              {CATEGORY_COLORS.map((color) => (
                <button
                  key={color}
                  type="button"
                  className={`color-swatch ${c.color === color ? 'selected' : ''}`}
                  style={{ background: color }}
                  onClick={() => onUpdateCategory(c.id, { color })}
                  aria-label={`Set color ${color}`}
                />
              ))}
            </div>
            <button type="button" className="category-delete-btn" onClick={() => onDeleteCategory(c.id)} title="Delete category">
              🗑
            </button>
          </div>
        ))}
        {categories.length === 0 && <p className="category-empty">No categories yet. Click New to add one.</p>}
      </div>
    </section>
  )
}
