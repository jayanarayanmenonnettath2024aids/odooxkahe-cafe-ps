import { DRAWER_ITEMS } from './data'

export default function RightDrawer({ open, activeItem, onSelect, onClose }) {
  return (
    <>
      <div className={`drawer-backdrop ${open ? 'open' : ''}`} onClick={onClose} />
      <aside className={`right-drawer ${open ? 'open' : ''}`}>
        <h3>Menu</h3>
        <ul>
          {DRAWER_ITEMS.map((item) => (
            <li key={item.id}>
              <button
                type="button"
                className={activeItem === item.id ? 'active' : ''}
                onClick={() => onSelect(item.id)}
              >
                <span>{item.icon}</span>
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      </aside>
    </>
  )
}
