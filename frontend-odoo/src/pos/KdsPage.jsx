import { useEffect, useMemo, useState } from 'react'
import { apiFetch } from '../api'
import './KdsPage.css'

const PAGE_SIZE = 6

export default function KdsPage() {
  const [tickets, setTickets] = useState([])
  const [activeTab, setActiveTab] = useState('to-cook')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [selectedProducts, setSelectedProducts] = useState([])
  const [selectedCategories, setSelectedCategories] = useState([])
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)

  const loadOrders = async () => {
    try {
      const orders = await apiFetch('/kds/orders')
      // map backend order to frontend ticket structure
      const mapped = orders.map(o => ({
        id: o.id.toString(),
        order_type: o.order_type,
        table_id: o.table_id,
        manuallyCompleted: o.status === 'READY',
        items: o.items.map(i => ({
          id: i.id,
          name: i.product_name,
          qty: i.quantity,
          category: 'Kitchen', // default if missing
          prepared: i.kitchen_status === 'COMPLETED'
        }))
      }))
      setTickets(mapped)
    } catch(e) { console.error('KDS Error:', e) }
  }

  useEffect(() => {
    loadOrders()
    const token = localStorage.getItem('access_token')
    const ws = new WebSocket(`ws://localhost:8000/ws?token=${token}&channels=kds`)
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (['ORDER_SENT_TO_KITCHEN', 'ORDER_PREPARING', 'ORDER_COMPLETED', 'KDS_UPDATE'].includes(data.event)) {
        loadOrders()
      }
    }
    return () => ws.close()
  }, [])

  const persist = async (next) => {
    setTickets(next)
    // we also need to push state updates back to server asynchronously
    // but local optimistic updates first
  }

  const toggleItemPrepared = async (ticketId, itemIndex) => {
    const ticket = tickets.find(t => t.id === ticketId)
    if (!ticket) return
    const item = ticket.items[itemIndex]
    if (item.prepared) return // Backend doesn't support un-preparing currently
    
    // Optimistic UI
    persist(tickets.map((t) => {
      if (t.id !== ticketId) return t
      return { ...t, items: t.items.map((it, i) => (i === itemIndex ? { ...it, prepared: true } : it)) }
    }))

    // Backend update
    try {
      await apiFetch(`/kds/item/${item.id}/complete`, {
        method: 'PATCH'
      })
    } catch(e) { console.error('Failed to update kitchen status', e) }
  }

  const toggleTicketCompleted = async (ticketId) => {
    const ticket = tickets.find(t => t.id === ticketId)
    if (!ticket) return
    if (ticket.manuallyCompleted) return // Cannot un-complete currently

    // Optimistic UI
    persist(tickets.map((t) => (t.id === ticketId ? { ...t, manuallyCompleted: true } : t)))

    // Backend update
    try {
      await apiFetch(`/kds/order/${ticketId}/next-stage`, {
        method: 'PATCH'
      })
    } catch(e) { console.error('Failed to update ticket status', e) }
  }

  // Need ticketStage function since we removed loadTickets import which exported it
  const ticketStage = (ticket) => {
    if (ticket.manuallyCompleted) return 'completed'
    const total = ticket.items.length
    if (total === 0) return 'to-cook'
    const prepCount = ticket.items.filter(i => i.prepared).length
    if (prepCount === total) return 'completed'
    if (prepCount > 0) return 'preparing'
    return 'to-cook'
  }

  const counts = useMemo(() => {
    const all = tickets.length
    let toCook = 0
    let preparing = 0
    let completed = 0
    tickets.forEach((t) => {
      const stage = ticketStage(t)
      if (stage === 'completed') completed += 1
      else {
        toCook += 1
        if (stage === 'preparing') preparing += 1
      }
    })
    return { all, toCook, preparing, completed }
  }, [tickets])

  const productOptions = useMemo(() => {
    const set = new Set()
    tickets.forEach((t) => t.items.forEach((i) => set.add(i.name)))
    return [...set].sort()
  }, [tickets])

  const categoryOptions = useMemo(() => {
    const set = new Set()
    tickets.forEach((t) => t.items.forEach((i) => i.category && set.add(i.category)))
    return [...set].sort()
  }, [tickets])

  const q = query.trim().toLowerCase()

  const filtered = tickets.filter((t) => {
    const stage = ticketStage(t)
    if (activeTab === 'to-cook' && stage === 'completed') return false
    if (activeTab === 'preparing' && stage !== 'preparing') return false
    if (activeTab === 'completed' && stage !== 'completed') return false

    if (selectedProducts.length > 0 && !t.items.some((i) => selectedProducts.includes(i.name))) return false
    if (selectedCategories.length > 0 && !t.items.some((i) => selectedCategories.includes(i.category))) return false

    if (q && !t.id.includes(q) && !t.items.some((i) => i.name.toLowerCase().includes(q))) return false

    return true
  })

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  const safePage = Math.min(page, totalPages)
  const pageStart = (safePage - 1) * PAGE_SIZE
  const pageTickets = filtered.slice(pageStart, pageStart + PAGE_SIZE)
  const rangeEnd = Math.min(pageStart + PAGE_SIZE, filtered.length)

  const toggleFilter = (list, setList, value) => {
    setPage(1)
    setList(list.includes(value) ? list.filter((v) => v !== value) : [...list, value])
  }

  const clearFilters = () => {
    setSelectedProducts([])
    setSelectedCategories([])
    setQuery('')
    setPage(1)
  }

  return (
    <div className="kds-page">
      <header className="kds-topnav">
        <div className="kds-logo">☕ BrewNest</div>
        <h2 className="kds-title">KDS</h2>
        <div className="kds-header-icons">
          <span className="kds-icon-btn">🧾</span>
          <span className="kds-icon-btn">⊘</span>
          <span className="kds-icon-btn">🗋+</span>
        </div>
        <div className="kds-header-right">
          <span className="kds-icon-btn round">👤</span>
          <span className="kds-icon-btn round">☰</span>
        </div>
      </header>

      <div className="kds-toolbar">
        <button type="button" className="kds-sidebar-toggle" onClick={() => setSidebarOpen((v) => !v)}>☰</button>

        <div className="kds-tabs">
          <button type="button" className={`kds-tab ${activeTab === 'all' ? 'active' : ''}`} onClick={() => { setActiveTab('all'); setPage(1) }}>
            All <span className="kds-badge">{counts.all}</span>
          </button>
          <span className="kds-tab-divider">|</span>
          <button type="button" className={`kds-tab ${activeTab === 'to-cook' ? 'active' : ''}`} onClick={() => { setActiveTab('to-cook'); setPage(1) }}>
            To Cook <span className="kds-badge">{counts.toCook}</span>
          </button>
          <button type="button" className={`kds-tab ${activeTab === 'preparing' ? 'active' : ''}`} onClick={() => { setActiveTab('preparing'); setPage(1) }}>
            Preparing <span className="kds-badge">{counts.preparing}</span>
          </button>
          <button type="button" className={`kds-tab ${activeTab === 'completed' ? 'active' : ''}`} onClick={() => { setActiveTab('completed'); setPage(1) }}>
            Completed <span className="kds-badge">{counts.completed}</span>
          </button>
        </div>

        <div className="kds-search">
          <input
            type="text"
            value={query}
            onChange={(e) => { setQuery(e.target.value); setPage(1) }}
            placeholder="Search......"
          />
          <span className="search-icon" aria-hidden="true">🔍</span>
        </div>

        <div className="kds-pagination">
          <span>{filtered.length === 0 ? '0-0' : `${pageStart + 1}-${rangeEnd}`}</span>
          <button type="button" disabled={safePage <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>‹</button>
          <button type="button" disabled={safePage >= totalPages} onClick={() => setPage((p) => Math.min(totalPages, p + 1))}>›</button>
        </div>
      </div>

      <div className="kds-body">
        {sidebarOpen && (
          <aside className="kds-sidebar">
            <button type="button" className="kds-clear-filter" onClick={clearFilters}>
              Clear Filter <span>✕</span>
            </button>

            <div className="kds-filter-group">
              <h4>Product</h4>
              {productOptions.map((p) => (
                <button
                  key={p}
                  type="button"
                  className={`kds-filter-item ${selectedProducts.includes(p) ? 'selected' : ''}`}
                  onClick={() => toggleFilter(selectedProducts, setSelectedProducts, p)}
                >
                  {p}
                </button>
              ))}
            </div>

            <div className="kds-filter-group">
              <h4>Category</h4>
              {categoryOptions.map((c) => (
                <button
                  key={c}
                  type="button"
                  className={`kds-filter-item ${selectedCategories.includes(c) ? 'selected' : ''}`}
                  onClick={() => toggleFilter(selectedCategories, setSelectedCategories, c)}
                >
                  {c}
                </button>
              ))}
            </div>
          </aside>
        )}

        <div className="kds-grid">
          {pageTickets.map((ticket) => {
            const stage = ticketStage(ticket)
            return (
              <div
                key={ticket.id}
                className={`kds-ticket ${stage}`}
                onClick={() => toggleTicketCompleted(ticket.id)}
              >
                <div className="kds-ticket-header">
                  <div className="kds-ticket-number" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <span>#{ticket.id}</span>
                    <span style={{ fontSize: '14px', color: '#e0e0e0', fontWeight: 'normal' }}>
                      {ticket.order_type === 'DINE_IN' ? `🍽️ Dine-in (Table ${ticket.table_id || '?'})` : '🛍️ Takeaway'}
                    </span>
                  </div>
                  <div className="kds-ticket-time">
                    {ticket.time}
                  </div>
                </div>
                {ticket.items.map((item, index) => (
                  <div
                    key={index}
                    className={`kds-ticket-item ${item.prepared ? 'prepared' : ''}`}
                    onClick={(e) => {
                      e.stopPropagation()
                      toggleItemPrepared(ticket.id, index)
                    }}
                  >
                    {item.qty} X {item.name}
                  </div>
                ))}
              </div>
            )
          })}
          {pageTickets.length === 0 && <p className="kds-empty">No tickets in this view.</p>}
        </div>
      </div>
    </div>
  )
}
