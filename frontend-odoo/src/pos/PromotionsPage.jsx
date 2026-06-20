import { useState, useEffect } from 'react'
import { apiFetch } from '../api'
import './PromotionsPage.css'

export default function PromotionsPage() {
  const [tab, setTab] = useState('coupons')
  const [coupons, setCoupons] = useState([])
  const [promotions, setPromotions] = useState([])
  
  const [couponForm, setCouponForm] = useState({ code: '', discount_type: 'PERCENTAGE', discount_value: '' })
  const [promoForm, setPromoForm] = useState({ name: '', promotion_scope: 'ORDER', minimum_quantity: '', minimum_order_amount: '', discount_type: 'PERCENTAGE', discount_value: '' })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [c, p] = await Promise.all([
        apiFetch('/coupons'),
        apiFetch('/promotions')
      ])
      setCoupons(c || [])
      setPromotions(p || [])
    } catch (e) {
      console.error(e)
    }
  }

  const createCoupon = async (e) => {
    e.preventDefault()
    try {
      await apiFetch('/coupons', {
        method: 'POST',
        body: JSON.stringify({
          ...couponForm,
          discount_value: parseFloat(couponForm.discount_value)
        })
      })
      setCouponForm({ code: '', discount_type: 'PERCENTAGE', discount_value: '' })
      loadData()
    } catch (e) { alert(e.message) }
  }

  const deleteCoupon = async (id) => {
    try {
      await apiFetch(`/coupons/${id}`, { method: 'DELETE' })
      loadData()
    } catch (e) { alert(e.message) }
  }

  const toggleCoupon = async (c) => {
    try {
      await apiFetch(`/coupons/${c.id}`, { method: 'PUT', body: JSON.stringify({ is_active: !c.is_active }) })
      loadData()
    } catch (e) { alert(e.message) }
  }

  const createPromotion = async (e) => {
    e.preventDefault()
    try {
      const payload = {
        name: promoForm.name,
        promotion_scope: promoForm.promotion_scope,
        discount_type: promoForm.discount_type,
        discount_value: parseFloat(promoForm.discount_value)
      }
      if (promoForm.promotion_scope === 'PRODUCT' && promoForm.minimum_quantity) payload.minimum_quantity = parseInt(promoForm.minimum_quantity, 10)
      if (promoForm.promotion_scope === 'ORDER' && promoForm.minimum_order_amount) payload.minimum_order_amount = parseFloat(promoForm.minimum_order_amount)
      
      await apiFetch('/promotions', {
        method: 'POST',
        body: JSON.stringify(payload)
      })
      setPromoForm({ name: '', promotion_scope: 'ORDER', minimum_quantity: '', minimum_order_amount: '', discount_type: 'PERCENTAGE', discount_value: '' })
      loadData()
    } catch (e) { alert(e.message) }
  }

  const deletePromotion = async (id) => {
    try {
      await apiFetch(`/promotions/${id}`, { method: 'DELETE' })
      loadData()
    } catch (e) { alert(e.message) }
  }

  const togglePromotion = async (p) => {
    try {
      await apiFetch(`/promotions/${p.id}`, { method: 'PUT', body: JSON.stringify({ is_active: !p.is_active }) })
      loadData()
    } catch (e) { alert(e.message) }
  }

  return (
    <section className="promotions-page">
      <span className="promotions-page-eyebrow">Marketing</span>
      <h1 className="promotions-page-title">Coupons & Promotions</h1>

      <div className="promotions-tabs">
        <button className={`promo-tab-btn ${tab === 'coupons' ? 'active' : ''}`} onClick={() => setTab('coupons')}>Coupons</button>
        <button className={`promo-tab-btn ${tab === 'promotions' ? 'active' : ''}`} onClick={() => setTab('promotions')}>Auto Promotions</button>
      </div>
      
      <div className="promotions-content">
        {tab === 'coupons' ? (
          <>
            <form className="promo-form" onSubmit={createCoupon}>
              <h3>Create New Coupon</h3>
              <div className="promo-form-row">
                <input required placeholder="Code (e.g. FLAT50)" value={couponForm.code} onChange={(e) => setCouponForm({...couponForm, code: e.target.value.toUpperCase().replace(/\s/g, '')})} />
                <select value={couponForm.discount_type} onChange={(e) => setCouponForm({...couponForm, discount_type: e.target.value})}>
                  <option value="PERCENTAGE">% Off</option>
                  <option value="FIXED_AMOUNT">₹ Off</option>
                </select>
                <input required type="number" step="0.01" placeholder="Discount Value" value={couponForm.discount_value} onChange={(e) => setCouponForm({...couponForm, discount_value: e.target.value})} />
                <button type="submit" className="promo-btn-primary">Add Coupon</button>
              </div>
            </form>

            <table className="promo-table">
              <thead><tr><th>Code</th><th>Type</th><th>Value</th><th>Active</th><th>Actions</th></tr></thead>
              <tbody>
                {coupons.map(c => (
                  <tr key={c.id}>
                    <td><strong>{c.code}</strong></td>
                    <td>{c.discount_type === 'PERCENTAGE' ? 'Percentage' : 'Fixed Amount'}</td>
                    <td>{c.discount_type === 'PERCENTAGE' ? `${c.discount_value}%` : `₹${c.discount_value}`}</td>
                    <td>
                      <label className="promo-switch">
                        <input type="checkbox" checked={c.is_active} onChange={() => toggleCoupon(c)} />
                        <span className="promo-slider promo-round"></span>
                      </label>
                    </td>
                    <td><button type="button" className="promo-btn-danger" onClick={() => deleteCoupon(c.id)}>🗑</button></td>
                  </tr>
                ))}
                {coupons.length === 0 && <tr><td colSpan="5" className="promo-empty">No coupons found. Create one above.</td></tr>}
              </tbody>
            </table>
          </>
        ) : (
          <>
            <form className="promo-form" onSubmit={createPromotion}>
              <h3>Create New Auto Promotion</h3>
              <div className="promo-form-row">
                <input required placeholder="Name (e.g. 10% off over ₹1000)" value={promoForm.name} onChange={(e) => setPromoForm({...promoForm, name: e.target.value})} style={{ flex: 2 }} />
                <select value={promoForm.promotion_scope} onChange={(e) => setPromoForm({...promoForm, promotion_scope: e.target.value})}>
                  <option value="ORDER">Order Total &gt; X</option>
                  <option value="PRODUCT">Total Qty &gt; X</option>
                </select>
                {promoForm.promotion_scope === 'ORDER' ? (
                  <input required type="number" step="0.01" placeholder="Min Amount" value={promoForm.minimum_order_amount} onChange={(e) => setPromoForm({...promoForm, minimum_order_amount: e.target.value})} />
                ) : (
                  <input required type="number" placeholder="Min Qty" value={promoForm.minimum_quantity} onChange={(e) => setPromoForm({...promoForm, minimum_quantity: e.target.value})} />
                )}
                <select value={promoForm.discount_type} onChange={(e) => setPromoForm({...promoForm, discount_type: e.target.value})}>
                  <option value="PERCENTAGE">% Off</option>
                  <option value="FIXED_AMOUNT">₹ Off</option>
                </select>
                <input required type="number" step="0.01" placeholder="Value" value={promoForm.discount_value} onChange={(e) => setPromoForm({...promoForm, discount_value: e.target.value})} />
                <button type="submit" className="promo-btn-primary">Add Promotion</button>
              </div>
            </form>

            <table className="promo-table">
              <thead><tr><th>Name</th><th>Condition</th><th>Discount</th><th>Active</th><th>Actions</th></tr></thead>
              <tbody>
                {promotions.map(p => (
                  <tr key={p.id}>
                    <td><strong>{p.name}</strong></td>
                    <td>{p.promotion_scope === 'ORDER' ? `Order > ₹${p.minimum_order_amount}` : `Qty > ${p.minimum_quantity} items`}</td>
                    <td>{p.discount_type === 'PERCENTAGE' ? `${p.discount_value}%` : `₹${p.discount_value}`}</td>
                    <td>
                      <label className="promo-switch">
                        <input type="checkbox" checked={p.is_active} onChange={() => togglePromotion(p)} />
                        <span className="promo-slider promo-round"></span>
                      </label>
                    </td>
                    <td><button type="button" className="promo-btn-danger" onClick={() => deletePromotion(p.id)}>🗑</button></td>
                  </tr>
                ))}
                {promotions.length === 0 && <tr><td colSpan="5" className="promo-empty">No auto promotions found. Create one above.</td></tr>}
              </tbody>
            </table>
          </>
        )}
      </div>
    </section>
  )
}
