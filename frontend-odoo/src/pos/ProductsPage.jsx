import { useState } from 'react'
import ProductFormModal from './ProductFormModal'
import './ProductsPage.css'

export default function ProductsPage({ products, categories, onSaveProduct, onSetArchived, onCreateCategory }) {
  const [query, setQuery] = useState('')
  const [selectedIds, setSelectedIds] = useState([])
  const [actionOpen, setActionOpen] = useState(false)
  const [editingProduct, setEditingProduct] = useState(null) // product object, or {} for new
  const [formOpen, setFormOpen] = useState(false)

  const categoryById = (id) => categories.find((c) => c.id === id)

  const q = query.trim().toLowerCase()
  const filtered = products.filter((p) => {
    if (!q) return true
    // Support both normalized (categoryId) and raw (category_id)
    const catId = p.categoryId ?? p.category_id
    const categoryName = categoryById(catId)?.name.toLowerCase() || ''
    return p.name.toLowerCase().includes(q) || categoryName.includes(q)
  })

  const toggleSelect = (id) => {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]))
  }

  const openNew = () => {
    setEditingProduct(null)
    setFormOpen(true)
  }

  const openEdit = (product) => {
    setEditingProduct(product)
    setFormOpen(true)
  }

  const handleSave = (fields) => {
    onSaveProduct(editingProduct?.id, fields)
    setFormOpen(false)
  }

  const applyAction = (archived) => {
    onSetArchived(selectedIds, archived)
    setSelectedIds([])
    setActionOpen(false)
  }

  return (
    <section className="products-page">
      <h1 className="products-title">Products</h1>

      <div className="products-toolbar">
        <button type="button" className="products-new-btn" onClick={openNew}>
          <span>🗋+</span> New
        </button>

        {selectedIds.length > 0 && (
          <div className="products-action-wrap">
            <button type="button" className="products-action-btn" onClick={() => setActionOpen((v) => !v)}>
              ⭐ Action ({selectedIds.length})
            </button>
            {actionOpen && (
              <div className="products-action-menu">
                <button type="button" onClick={() => applyAction(true)}>Archive</button>
                <button type="button" onClick={() => applyAction(false)}>Activate</button>
              </div>
            )}
          </div>
        )}

        <div className="products-search">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search product or category..."
          />
          <span className="search-icon" aria-hidden="true">🔍</span>
        </div>
      </div>

      <div className="products-table">
        <div className="products-row products-head">
          <span />
          <span>Name</span>
          <span>Category</span>
          <span>Price</span>
          <span>Tax</span>
        </div>
        {filtered.map((p) => {
          // Support both normalized (categoryId) and raw (category_id)
          const catId = p.categoryId ?? p.category_id
          const category = categoryById(catId)
          const taxDisplay = p.tax ?? p.tax_percentage ?? 0
          return (
            <div key={p.id} className={`products-row products-data ${p.archived ? 'archived' : ''}`}>
              <span className="products-checkbox-cell">
                <input
                  type="checkbox"
                  checked={selectedIds.includes(p.id)}
                  onChange={() => toggleSelect(p.id)}
                />
              </span>
              <span className="products-name-cell" onClick={() => openEdit(p)}>
                {p.name}
                {p.archived && <span className="archived-tag">Archived</span>}
              </span>
              <span onClick={() => openEdit(p)}>
                {category && (
                  <span className="category-pill" style={{ background: category.color }}>{category.name}</span>
                )}
                {!category && p.category_name && (
                  <span className="category-pill" style={{ background: '#D4A056' }}>{p.category_name}</span>
                )}
              </span>
              <span onClick={() => openEdit(p)}>₹{p.price}</span>
              <span onClick={() => openEdit(p)}>{taxDisplay}%</span>
            </div>
          )
        })}
        {filtered.length === 0 && <p className="products-empty">No products found.</p>}
      </div>

      {formOpen && (
        <ProductFormModal
          product={editingProduct}
          categories={categories}
          onSave={handleSave}
          onDiscard={() => setFormOpen(false)}
          onCreateCategory={onCreateCategory}
        />
      )}
    </section>
  )
}
