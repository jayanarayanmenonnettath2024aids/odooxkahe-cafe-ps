export default function CategorySidebar({ categories, activeCategory, onSelectCategory }) {
  return (
    <nav className="category-sidebar">
      {categories.map((category) => (
        <button
          key={category.id}
          type="button"
          className={`category-btn ${activeCategory === category.id ? 'active' : ''}`}
          onClick={() => onSelectCategory(category.id)}
        >
          <span className="category-icon">{category.icon}</span>
          <span className="category-name">{category.name}</span>
        </button>
      ))}
    </nav>
  )
}
