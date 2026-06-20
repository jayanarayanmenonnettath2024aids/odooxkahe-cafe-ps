import { useState } from 'react'
import { TAX_OPTIONS } from './data'
import CategoryFormModal from './CategoryFormModal'

const emptyDraft = { name: '', price: '', tax: TAX_OPTIONS[0], categoryId: '', description: '' }

export default function ProductFormModal({ product, categories, onSave, onDiscard, onCreateCategory }) {
  // Support both normalized (categoryId) and raw (category_id)
  const initialCategoryId = product?.categoryId ?? product?.category_id
  const initialCategory = categories.find((c) => c.id === initialCategoryId)
  const [form, setForm] = useState(product ? {
    ...product,
    categoryId: initialCategoryId,
    tax: product.tax ?? product.tax_percentage ?? TAX_OPTIONS[0],
  } : { ...emptyDraft })
  const [categoryQuery, setCategoryQuery] = useState(initialCategory?.name || '')
  const [categoryOpen, setCategoryOpen] = useState(false)
  const [showCategoryModal, setShowCategoryModal] = useState(false)
  const [nameError, setNameError] = useState(false)

  const q = categoryQuery.trim().toLowerCase()
  const matchingCategories = categories.filter((c) => !q || c.name.toLowerCase().includes(q))
  const exactMatch = categories.find((c) => c.name.toLowerCase() === q)

  const selectCategory = (category) => {
    setForm({ ...form, categoryId: category.id })
    setCategoryQuery(category.name)
    setCategoryOpen(false)
  }

  const handleCategoryCreated = (fields) => {
    const newId = onCreateCategory(fields)
    setForm({ ...form, categoryId: newId })
    setCategoryQuery(fields.name)
    setShowCategoryModal(false)
  }

  const handleSave = () => {
    if (!form.name.trim()) {
      setNameError(true)
      return
    }
    onSave({
      name: form.name.trim(),
      price: Number(form.price) || 0,
      tax_percentage: Number(form.tax),   // backend expects tax_percentage
      category_id: form.categoryId || null,  // backend expects category_id
      description: form.description?.trim() || '',
      is_active: true,
    })
  }

  return (
    <div className="product-edit-backdrop" onClick={onDiscard}>
      <div className="product-edit-modal" onClick={(e) => e.stopPropagation()}>
        <button type="button" className="product-edit-close" onClick={onDiscard}>✕</button>
        <h3>{product ? 'Edit Product' : 'New Product'}</h3>

        <label className="product-edit-field">
          <span className="field-label">Product Name</span>
          <input
            type="text"
            className={nameError ? 'error' : ''}
            placeholder="e.g. Masala Tea"
            value={form.name}
            onChange={(e) => {
              setForm({ ...form, name: e.target.value })
              if (nameError) setNameError(false)
            }}
          />
          {nameError && <span className="customer-edit-error">Name is required</span>}
        </label>

        <div className="product-edit-row">
          <label className="product-edit-field">
            <span className="field-label">Price</span>
            <div className="price-input">
              <span>₹</span>
              <input
                type="number"
                min="0"
                placeholder="0"
                value={form.price}
                onChange={(e) => setForm({ ...form, price: e.target.value })}
              />
            </div>
          </label>

          <label className="product-edit-field">
            <span className="field-label">Tax</span>
            <select value={form.tax} onChange={(e) => setForm({ ...form, tax: e.target.value })}>
              {TAX_OPTIONS.map((t) => (
                <option key={t} value={t}>{t}%</option>
              ))}
            </select>
          </label>
        </div>

        <div className="product-edit-field category-combobox">
          <span className="field-label">Category</span>
          <input
            type="text"
            placeholder="Select or type to create"
            value={categoryQuery}
            onFocus={() => setCategoryOpen(true)}
            onBlur={() => setTimeout(() => setCategoryOpen(false), 150)}
            onChange={(e) => {
              setCategoryQuery(e.target.value)
              setCategoryOpen(true)
              setForm({ ...form, categoryId: '' })
            }}
          />
          {categoryOpen && (
            <div className="category-dropdown">
              {matchingCategories.map((c) => (
                <button type="button" key={c.id} onClick={() => selectCategory(c)}>
                  <span className="category-dot" style={{ background: c.color }} />
                  {c.name}
                </button>
              ))}
              {!exactMatch && q && (
                <button type="button" className="create-category-option" onClick={() => setShowCategoryModal(true)}>
                  ➕ Create &amp; Edit "{categoryQuery.trim()}"
                </button>
              )}
              {matchingCategories.length === 0 && !q && (
                <p className="category-dropdown-empty">Type to search or create a category</p>
              )}
            </div>
          )}
        </div>

        <label className="product-edit-field">
          <span className="field-label">Product Description</span>
          <textarea
            placeholder="e.g Burger with cheese"
            rows={3}
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
        </label>

        <div className="product-edit-actions">
          <button type="button" className="discard-btn" onClick={onDiscard}>Discard</button>
          <button type="button" className="save-btn" onClick={handleSave}>Save</button>
        </div>
      </div>

      {showCategoryModal && (
        <CategoryFormModal
          initialName={categoryQuery.trim()}
          onSave={handleCategoryCreated}
          onDiscard={() => setShowCategoryModal(false)}
        />
      )}
    </div>
  )
}
