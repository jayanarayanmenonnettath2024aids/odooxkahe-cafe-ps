import { STATUS_META } from './data'

export default function ProductGrid({ products, activeCategory, searchQuery, onAddToCart, pulsedProductId }) {
  const query = searchQuery.trim().toLowerCase()
  const visibleProducts = products.filter((product) => {
    if (product.archived) return false
    const matchesCategory = !query && product.categoryId === activeCategory
    const matchesSearch = query && product.name.toLowerCase().includes(query)
    return query ? matchesSearch : matchesCategory
  })

  return (
    <section className="product-grid-section">
      <div className="specials-banner">
        ✨ Today's Special: Buy 1 Get 1 on Cold Coffee — all day!
      </div>

      <div className="product-grid">
        {visibleProducts.map((product) => {
          const status = STATUS_META[product.status]
          const isUnavailable = product.status === 'unavailable'
          return (
            <button
              key={product.id}
              type="button"
              className={`product-card ${pulsedProductId === product.id ? 'pulsed' : ''} ${isUnavailable ? 'disabled' : ''}`}
              disabled={isUnavailable}
              onClick={() => onAddToCart(product)}
            >
              <div className="product-image">{product.icon}</div>
              <div className="product-name">{product.name}</div>
              <div className="product-price">₹{product.price}</div>
              <div className="product-status">
                <span className="status-dot" style={{ background: status.color }} />
                {status.label}
              </div>
            </button>
          )
        })}
        {visibleProducts.length === 0 && (
          <p className="no-products">No items found.</p>
        )}
      </div>
    </section>
  )
}
