import { useState, useMemo } from 'react';

export default function MenuScreen({ categories, products, cart, addToCart, onViewCart }) {
  const [activeCategory, setActiveCategory] = useState(categories[0]?.id);

  const displayedProducts = useMemo(() => {
    return products.filter(p => p.category_id === activeCategory && p.is_active);
  }, [products, activeCategory]);

  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <div className="menu-screen">
      <div className="category-tabs">
        {categories.map(cat => (
          <button 
            key={cat.id} 
            className={`cat-tab ${activeCategory === cat.id ? 'active' : ''}`}
            onClick={() => setActiveCategory(cat.id)}
          >
            {cat.name}
          </button>
        ))}
      </div>

      <div className="product-list">
        {displayedProducts.map(product => (
          <div key={product.id} className="mobile-product-card">
            <h3>{product.name}</h3>
            <span className="price">₹{product.price.toFixed(0)}</span>
            <button onClick={() => addToCart(product)}>+ Add</button>
          </div>
        ))}
      </div>

      {totalItems > 0 && (
        <button className="view-cart-fab" onClick={onViewCart}>
          🛒 View Cart ({totalItems})
        </button>
      )}
    </div>
  );
}
