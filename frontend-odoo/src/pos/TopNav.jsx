import { useState } from 'react'
import CustomerModule from './CustomerModule'

const TABLE_NUMBERS = Array.from({ length: 16 }, (_, i) => i + 1)

export default function TopNav({
  searchQuery,
  onSearchChange,
  table,
  tableViewOpen,
  onToggleTableView,
  onSelectTable,
  view,
  onToggleView,
  onGoHome,
  onNewOrder,
  reservationOpen,
  onToggleReservation,
  loyaltyOpen,
  onToggleLoyalty,
  customer,
  customers,
  activeCustomerId,
  customerOpen,
  onToggleCustomer,
  onSelectCustomer,
  onSaveCustomer,
  onDeleteCustomer,
  onToggleDrawer,
  onSubmitReservation,
}) {
  const [resData, setResData] = useState({
    date: '',
    time: '',
    partySize: 2,
    customer_name: '',
    customer_email: '',
    customer_phone: ''
  });

  const handleReservationSubmit = () => {
    if (!resData.date || !resData.time || !resData.customer_name || !resData.customer_phone) {
      alert("Please fill in Name, Phone, Date, and Time.");
      return;
    }
    onSubmitReservation({
      customer_name: resData.customer_name,
      customer_email: resData.customer_email,
      customer_phone: resData.customer_phone,
      reservation_date: resData.date,
      start_time: resData.time + ":00",
      end_time: resData.time + ":00", // Simplification
      guest_count: parseInt(resData.partySize, 10),
      table_id: table !== 'No' ? table : null
    });
  };

  return (
    <header className="pos-topnav">
      <div className="topnav-section topnav-left">
        <button type="button" className="pos-logo" onClick={onGoHome} title="Back to POS">
          <span className="pos-logo-title">☕ BrewNest</span>
          <span className="pos-logo-sub">Premium Coffee Lounge</span>
        </button>
      </div>

      <div className="topnav-section topnav-search">
        <span className="search-icon" aria-hidden="true">🔍</span>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search coffee, snacks, desserts..."
        />
      </div>

      <div className="topnav-section topnav-actions">
        <div className="quick-action-wrap">
          <button
            type="button"
            className={`icon-btn ${view === 'orders' ? 'active' : ''}`}
            title="Orders"
            onClick={onToggleView}
          >
            🧾
          </button>
        </div>

        <div className="quick-action-wrap">
          <button type="button" className="icon-btn" title="New Order" onClick={onNewOrder}>➕</button>
        </div>

        <div className="quick-action-wrap">
          <button type="button" className="icon-btn" title="Reservation" onClick={onToggleReservation}>📅</button>
          {reservationOpen && (
            <div className="popover reservation-popover" style={{ width: '320px' }}>
              <h4>Table Reservation</h4>
              <label>Name<input type="text" value={resData.customer_name} onChange={e => setResData({...resData, customer_name: e.target.value})} placeholder="John Doe" /></label>
              <label>Email<input type="email" value={resData.customer_email} onChange={e => setResData({...resData, customer_email: e.target.value})} placeholder="john@example.com" /></label>
              <label>Phone<input type="tel" value={resData.customer_phone} onChange={e => setResData({...resData, customer_phone: e.target.value})} placeholder="1234567890" /></label>
              <label>Date<input type="date" value={resData.date} onChange={e => setResData({...resData, date: e.target.value})} /></label>
              <label>Time<input type="time" value={resData.time} onChange={e => setResData({...resData, time: e.target.value})} /></label>
              <label>Party Size<input type="number" min="1" value={resData.partySize} onChange={e => setResData({...resData, partySize: e.target.value})} /></label>
              <button type="button" className="popover-confirm" onClick={handleReservationSubmit}>Confirm & Send Email</button>
            </div>
          )}
        </div>

        <div className="quick-action-wrap">
          <button type="button" className="icon-btn" title="Loyalty Card" onClick={onToggleLoyalty}>🎁</button>
          {loyaltyOpen && (
            <div className="popover loyalty-popover">
              <h4>Loyalty Card</h4>
              <p className="loyalty-name">{customer.name}</p>
              <p className="loyalty-points">⭐ {customer.points} Points</p>
              <button type="button" className="popover-confirm">Redeem 50 pts</button>
            </div>
          )}
        </div>

        <div className="quick-action-wrap">
          <button
            type="button"
            className={`icon-btn table-btn ${tableViewOpen ? 'active' : ''}`}
            onClick={onToggleTableView}
            title="Current Table"
          >
            🪑 {table} V
          </button>
          {tableViewOpen && (
            <div className="popover table-view-popover">
              <h4>Table View</h4>
              <span className="table-view-current">🪑 {table} V</span>
              <div className="table-grid">
                {TABLE_NUMBERS.map((n) => (
                  <button
                    key={n}
                    type="button"
                    className={`table-cell ${table === n ? 'selected' : ''}`}
                    onClick={() => onSelectTable(n)}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="topnav-section topnav-right">
        <div className="quick-action-wrap">
          <button type="button" className="icon-btn round" title="Customer Profile" onClick={onToggleCustomer}>
            👤
          </button>
          {customerOpen && (
            <div className="popover customer-popover">
              <CustomerModule
                customers={customers}
                activeCustomerId={activeCustomerId}
                onSelectCustomer={onSelectCustomer}
                onSaveCustomer={onSaveCustomer}
                onDeleteCustomer={onDeleteCustomer}
              />
            </div>
          )}
        </div>
        <button type="button" className="icon-btn round" title="Menu" onClick={onToggleDrawer}>
          ☰
        </button>
      </div>
    </header>
  )
}
