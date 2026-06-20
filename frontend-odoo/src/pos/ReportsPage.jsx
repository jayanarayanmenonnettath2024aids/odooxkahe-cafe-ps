import { useEffect, useMemo, useState } from 'react'
import { apiFetch } from '../api'
import './ReportsPage.css'

const PIE_COLORS = ['#E8A85C', '#C2703D', '#5B9BD5', '#4ADE80', '#9CA3AF']

function currency(n) {
  return `₹${(Math.round(n * 100) / 100).toFixed(2)}`
}

export default function ReportsPage({ orders = [], products = [], categories = [], customers = [] }) {
  const [periodFilter, setPeriodFilter] = useState('today')
  const [userFilter, setUserFilter] = useState('all')
  const [productFilter, setProductFilter] = useState('all')
  const [exportOpen, setExportOpen] = useState(false)
  const [openDropdown, setOpenDropdown] = useState(null)
  
  const [dashboard, setDashboard] = useState({
    total_orders: 0,
    total_revenue: 0,
    average_order_value: 0,
    top_products: [],
    top_categories: [],
    sales_trend: []
  })

  useEffect(() => {
    async function loadDashboard() {
      try {
        const data = await apiFetch(`/reports/dashboard?period=${periodFilter}`)
        setDashboard(data)
      } catch (e) {
        console.error('Failed to load dashboard', e)
      }
    }
    loadDashboard()
  }, [periodFilter])

  const filterChip = (label, value, options, onChange, key) => (
    <div className="report-filter-chip">
      <button type="button" onClick={() => setOpenDropdown(openDropdown === key ? null : key)}>
        {label}{value !== 'all' ? `: ${value}` : ''}
      </button>
      {value !== 'all' && (
        <span className="chip-clear" onClick={() => onChange('all')}>✕</span>
      )}
      {openDropdown === key && (
        <div className="report-filter-dropdown">
          <button type="button" onClick={() => { onChange('all'); setOpenDropdown(null) }}>All</button>
          {options.map((opt) => (
            <button key={opt.value} type="button" onClick={() => { onChange(opt.value); setOpenDropdown(null) }}>
              {opt.label}
            </button>
          ))}
        </div>
      )}
    </div>
  )

  const exportCsv = async () => {
    try {
      // Just download the file blob from backend
      const res = await fetch(`http://localhost:8000/reports/export?format=xlsx`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      })
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'brewnest-report.xlsx'
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) { console.error('Export failed', e) }
    setExportOpen(false)
  }

  const salesByBucket = dashboard.sales_trend.map(s => ({ label: s.date.slice(-5), value: s.revenue })) || []
  const maxSales = Math.max(1, ...salesByBucket.map((b) => b.value))
  const chartWidth = 280
  const chartHeight = 110
  const points = salesByBucket.map((b, i) => {
    const x = (i / Math.max(1, salesByBucket.length - 1)) * chartWidth
    const y = chartHeight - (b.value / maxSales) * (chartHeight - 16)
    return `${x},${y}`
  }).join(' ')
  const areaPoints = `0,${chartHeight} ${points} ${chartWidth},${chartHeight}`

  const categoryStats = dashboard.top_categories.map(c => ({
    name: c.category_name, value: c.revenue, pct: dashboard.total_revenue ? Math.round((c.revenue/dashboard.total_revenue)*100) : 0
  }))

  let cumulativeDeg = 0
  const pieGradient = categoryStats.map((c, i) => {
    const start = cumulativeDeg
    cumulativeDeg += (c.pct / 100) * 360
    return `${PIE_COLORS[i % PIE_COLORS.length]} ${start}deg ${cumulativeDeg}deg`
  }).join(', ')

  const totalOrders = dashboard.total_orders
  const revenue = dashboard.total_revenue
  const avgOrder = dashboard.average_order_value

  // Build top orders from the orders passed in (normalized shape)
  const topOrders = (orders || []).slice(0, 10).map(o => ({
    id: o.id || o.order_number,
    date: o.date || (o.created_at ? new Date(o.created_at).toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }) : '-'),
    customer: o.customer || o.customer_name || 'Guest',
    amount: o.amount ?? o.total_amount ?? 0,
    employee: o.employee_name || '-',
    session: o.session_id || '-',
  }))

  const productStats = dashboard.top_products.map(p => ({
    name: p.product_name, qty: p.quantity_sold, revenue: p.revenue
  }))

  return (
    <section className="reports-page">
      <span className="reports-eyebrow">Reporting: Real time reporting based on selection</span>
      <h1 className="reports-title">Reports</h1>

      <div className="reports-filters">
        {filterChip('Select period', periodFilter, [{ value: 'today', label: 'Today' }], setPeriodFilter, 'period')}
        {filterChip('User', userFilter, customers.map((c) => ({ value: c.name, label: c.name })), setUserFilter, 'user')}
        {filterChip('Session', 'all', [], () => {}, 'session')}
        {filterChip('Product', productFilter, products.map((p) => ({ value: p.id, label: p.name })), setProductFilter, 'product')}

        <div className="report-export-wrap">
          <button type="button" className="report-export-btn" onClick={() => setExportOpen((v) => !v)}>⭐</button>
          {exportOpen && (
            <div className="report-export-menu">
              <button type="button" onClick={() => { window.print(); setExportOpen(false) }}>PDF</button>
              <button type="button" onClick={exportCsv}>XLS</button>
            </div>
          )}
        </div>
      </div>

      <div className="reports-kpis">
        <div className="reports-kpi">
          <span className="kpi-label">Total order</span>
          <span className="kpi-value">{totalOrders}</span>
        </div>
        <div className="reports-kpi">
          <span className="kpi-label">Revenue</span>
          <span className="kpi-value">{currency(revenue)}</span>
        </div>
        <div className="reports-kpi">
          <span className="kpi-label">Average Order</span>
          <span className="kpi-value">{currency(avgOrder)}</span>
        </div>
      </div>

      <div className="reports-charts">
        <div className="reports-chart-card">
          <h3>Sales</h3>
          <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="sales-chart">
            <polygon points={areaPoints} fill="rgba(212,160,86,0.25)" />
            <polyline points={points} fill="none" stroke="#D4A056" strokeWidth="2" />
          </svg>
          <div className="sales-chart-labels">
            {salesByBucket.map((b) => <span key={b.label}>{b.label}</span>)}
          </div>
        </div>

        <div className="reports-chart-card">
          <h3>Top selling Category</h3>
          <div className="pie-row">
            <div className="pie-chart" style={{ background: categoryStats.length ? `conic-gradient(${pieGradient})` : 'rgba(255,255,255,0.08)' }} />
            <ul className="pie-legend">
              {categoryStats.map((c, i) => (
                <li key={c.name}>
                  <span className="legend-dot" style={{ background: PIE_COLORS[i % PIE_COLORS.length] }} />
                  {c.name} {c.pct}%
                </li>
              ))}
              {categoryStats.length === 0 && <li className="legend-empty">No sales data yet.</li>}
            </ul>
          </div>
        </div>
      </div>

      <div className="reports-table-card">
        <h3>Top Orders</h3>
        <div className="reports-table">
          <div className="reports-table-row reports-table-head">
            <span>Order</span>
            <span>Sessions</span>
            <span>Point of Sale</span>
            <span>Date</span>
            <span>Customer</span>
            <span>Employee</span>
            <span>Total</span>
          </div>
          {topOrders.map((o) => (
            <div className="reports-table-row" key={o.id}>
              <span className="order-link">#{o.id}</span>
              <span>Session-{o.session}</span>
              <span>POS</span>
              <span>{o.date}</span>
              <span>{o.customer}</span>
              <span>{o.employee}</span>
              <span>{currency(o.amount)}</span>
            </div>
          ))}
          {topOrders.length === 0 && <p className="reports-empty">No orders yet.</p>}
        </div>
      </div>

      <div className="reports-bottom-tables">
        <div className="reports-table-card">
          <h3>Top Product</h3>
          <div className="reports-table reports-table-small">
            <div className="reports-table-row reports-table-head">
              <span>Product</span>
              <span>Qty</span>
              <span>Revenue</span>
            </div>
            {productStats.map((p) => (
              <div className="reports-table-row" key={p.name}>
                <span>{p.name}</span>
                <span>{p.qty}</span>
                <span>{currency(p.revenue)}</span>
              </div>
            ))}
            {productStats.length === 0 && <p className="reports-empty">No product sales yet.</p>}
          </div>
        </div>

        <div className="reports-table-card">
          <h3>Top Category</h3>
          <div className="reports-table reports-table-2col">
            <div className="reports-table-row reports-table-head">
              <span>Category</span>
              <span>Revenue</span>
            </div>
            {categoryStats.map((c) => (
              <div className="reports-table-row" key={c.name}>
                <span>{c.name}</span>
                <span>{currency(c.value)}</span>
              </div>
            ))}
            {categoryStats.length === 0 && <p className="reports-empty">No category sales yet.</p>}
          </div>
        </div>
      </div>
    </section>
  )
}
