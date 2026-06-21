import { useState, useEffect } from 'react'
import { apiFetch } from '../api'
import './AiInsightsPage.css'

export default function AiInsightsPage({ onBack }) {
  const [demandForecast, setDemandForecast] = useState([])
  const [inventoryAlerts, setInventoryAlerts] = useState([])
  const [menuRecs, setMenuRecs] = useState(null)
  const [feedback, setFeedback] = useState(null)
  const [peakHours, setPeakHours] = useState([])
  
  // For Table Recommendation demo
  const [guests, setGuests] = useState(4)
  const [tableRec, setTableRec] = useState(null)

  useEffect(() => {
    async function loadInsights() {
      try {
        const [demand, inventory, menu, fb, peak] = await Promise.all([
          apiFetch('/ai/demand-forecast'),
          apiFetch('/ai/inventory-alerts'),
          apiFetch('/ai/menu-recommendations'),
          apiFetch('/ai/feedback-analysis'),
          apiFetch('/ai/peak-hours')
        ])
        setDemandForecast(demand || [])
        setInventoryAlerts(inventory || [])
        setMenuRecs(menu)
        setFeedback(fb)
        setPeakHours(peak || [])
      } catch (err) {
        console.error("Failed to load AI Insights", err)
      }
    }
    loadInsights()
  }, [])

  useEffect(() => {
    async function fetchTableRec() {
      try {
        const rec = await apiFetch(`/ai/table-recommendation?guests=${guests}`)
        setTableRec(rec)
      } catch (err) {
        console.error("Failed to load table rec", err)
      }
    }
    fetchTableRec()
  }, [guests])

  return (
    <div className="ai-page">
      <header className="ai-header">
        <button className="ai-back-btn" onClick={onBack}>← Back to POS</button>
        <h2>✨ AI Insights & Business Intelligence</h2>
        <p>Operational insights generated from historical data</p>
      </header>

      <div className="ai-grid">
        {/* Demand Forecast */}
        <div className="ai-card">
          <div className="ai-card-header">
            <h3>📈 Demand Forecast</h3>
            <span className="ai-subtitle">Expected Orders Tomorrow</span>
          </div>
          <div className="ai-card-body">
            <ul className="ai-list">
              {demandForecast.map((item, i) => (
                <li key={i} className="ai-list-item">
                  <span className="ai-item-name">{item.product}</span>
                  <span className="ai-item-val">
                    {item.forecast_tomorrow} <span className={item.forecast_tomorrow > item.weekly_average ? 'trend-up' : 'trend-down'}>
                      {item.forecast_tomorrow > item.weekly_average ? '↑' : '↓'}
                    </span>
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Inventory Alerts */}
        <div className="ai-card">
          <div className="ai-card-header">
            <h3>⚠ Smart Inventory Alerts</h3>
            <span className="ai-subtitle">Stock depletion warning</span>
          </div>
          <div className="ai-card-body">
            <ul className="ai-list">
              {inventoryAlerts.map((item, i) => (
                <li key={i} className="ai-list-item">
                  <span className="ai-item-name">{item.item}</span>
                  <span className={`ai-badge ${item.alert.toLowerCase()}`}>
                    {item.days_remaining} Days Remaining
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Menu Recommendations */}
        <div className="ai-card">
          <div className="ai-card-header">
            <h3>🍔 Smart Menu Recommendations</h3>
            <span className="ai-subtitle">Customers who order {menuRecs?.selected_product} also buy:</span>
          </div>
          <div className="ai-card-body">
            <ul className="ai-list">
              {menuRecs?.recommended_products.map((item, i) => (
                <li key={i} className="ai-list-item">
                  <span className="ai-item-name">⭐ {item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Feedback Analysis */}
        <div className="ai-card">
          <div className="ai-card-header">
            <h3>😊 Customer Feedback Analysis</h3>
            <span className="ai-subtitle">Sentiment Overview</span>
          </div>
          <div className="ai-card-body">
            <div className="ai-sentiment-bar">
              <div className="ai-sent-pos" style={{width: `${feedback?.positive || 0}%`}}></div>
              <div className="ai-sent-neu" style={{width: `${feedback?.neutral || 0}%`}}></div>
              <div className="ai-sent-neg" style={{width: `${feedback?.negative || 0}%`}}></div>
            </div>
            <div className="ai-sentiment-stats">
              <span className="c-pos">Positive: {feedback?.positive}%</span>
              <span className="c-neu">Neutral: {feedback?.neutral}%</span>
              <span className="c-neg">Negative: {feedback?.negative}%</span>
            </div>
            
            <div className="ai-feedback-topics">
              <div className="topic-col">
                <h4>Top Positive</h4>
                <ul>
                  {feedback?.top_positive.map((t,i) => <li key={i}>☕ {t}</li>)}
                </ul>
              </div>
              <div className="topic-col">
                <h4>Top Complaints</h4>
                <ul>
                  {feedback?.top_negative.map((t,i) => <li key={i}>⌛ {t}</li>)}
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Peak Hour Prediction */}
        <div className="ai-card">
          <div className="ai-card-header">
            <h3>🕒 Peak Hour Forecast</h3>
            <span className="ai-subtitle">Expected rush periods</span>
          </div>
          <div className="ai-card-body">
            <ul className="ai-list">
              {peakHours.map((rush, i) => (
                <li key={i} className="ai-list-item">
                  <span className="ai-item-name">{rush.name}</span>
                  <span className="ai-item-val">{rush.time}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Table Allocation */}
        <div className="ai-card">
          <div className="ai-card-header">
            <h3>🪑 Smart Table Allocation</h3>
            <span className="ai-subtitle">Optimize seating arrangements</span>
          </div>
          <div className="ai-card-body">
            <div className="ai-table-input">
              <label>Party Size:</label>
              <input 
                type="number" 
                min="1" max="20" 
                value={guests} 
                onChange={e => setGuests(parseInt(e.target.value) || 1)}
              />
            </div>
            {tableRec && (
              <div className="ai-table-result">
                <div className="ai-result-row">
                  <span>Recommended:</span>
                  <strong>{tableRec.recommended_table}</strong>
                </div>
                <div className="ai-result-row">
                  <span>Efficiency:</span>
                  <strong className={tableRec.efficiency > 80 ? 'c-pos' : 'c-neu'}>
                    {tableRec.efficiency}%
                  </strong>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
