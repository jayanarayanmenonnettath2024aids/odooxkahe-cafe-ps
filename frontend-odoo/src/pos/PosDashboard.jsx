import { useMemo, useRef, useState, useEffect } from 'react'
import TopNav from './TopNav'
import CategorySidebar from './CategorySidebar'
import ProductGrid from './ProductGrid'
import CartPanel from './CartPanel'
import PaymentPanel from './PaymentPanel'
import RightDrawer from './RightDrawer'
import OrdersPage from './OrdersPage'
import ProductsPage from './ProductsPage'
import CategoryPage from './CategoryPage'
import PromotionsPage from './PromotionsPage'
import PaymentMethodPage from './PaymentMethodPage'
import UserPage from './UserPage'
import ReportsPage from './ReportsPage'
import { DRAWER_ITEMS, CATEGORY_COLORS } from './data'

import './PosDashboard.css'

function formatOrderId(orderNumber) {
  return String(orderNumber).padStart(5, '0')
}

function formatNow() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

let cartItemSeq = 0

import { apiFetch, clearTokens } from '../api'

// ── Data Normalizers: map backend shapes → UI shapes ──────────────────────
const CATEGORY_ICON_MAP = {
  'Hot Beverages': '☕', 'Cold Beverages': '🧊', 'Coffee': '☕', 'Tea': '🍵',
  'Beverages': '🥤', 'Burgers': '🍔', 'Pizza': '🍕', 'Desserts': '🍰',
  'Snacks': '🥪', 'Meals': '🍱', 'Breakfast': '🍳', 'Mains': '🥗',
  'Add-ons': '🫙', 'Pasta': '🍝', 'Salads': '🥗', 'Sandwiches': '🥙',
  'Ice Cream': '🍨', 'Juices': '🧃', 'Shakes': '🥤',
}
const CATEGORY_COLOR_POOL = ['#60A5FA','#D4A056','#FB7185','#4ADE80','#C084FC','#F97316','#38BDF8','#A78BFA']

function normalizeCategory(c, index) {
  return {
    ...c,
    icon: CATEGORY_ICON_MAP[c.name] || '🏷',
    color: c.color || CATEGORY_COLOR_POOL[index % CATEGORY_COLOR_POOL.length],
  }
}

const PRODUCT_ICON_MAP = {
  'Cappuccino': '☕', 'Latte': '☕', 'Espresso': '☕', 'Americano': '☕',
  'Mocha': '☕', 'Cold Coffee': '🧊', 'Iced Tea': '🧊', 'Hot Chocolate': '🍫',
  'Masala Tea': '🍵', 'Tea': '🍵', 'Lassi': '🥤', 'Milkshake': '🥤',
  'Lemonade': '🍋', 'Juice': '🧃', 'Cheese Burger': '🍔', 'Veg Burger': '🍔',
  'Chicken Burger': '🍔', 'Double Patty': '🍔', 'Burger': '🍔',
  'Margherita': '🍕', 'Pepperoni': '🍕', 'Veggie Supreme': '🍕', 'Farmhouse': '🍕', 'Pizza': '🍕',
  'Brownie': '🍰', 'Cheesecake': '🍰', 'Tiramisu': '🍰', 'Donut': '🍩',
  'Sandwich': '🥪', 'Fries': '🍟', 'Nachos': '🥪', 'Garlic Bread': '🥪',
  'Combo Meal': '🍱', 'Thali': '🍱', 'Pasta': '🍝', 'Salad Bowl': '🥗',
  'Vanilla Scoop': '🍨', 'Choco Lava': '🍨', 'Sundae': '🍨', 'Cone': '🍦',
}

function normalizeProduct(p) {
  const icon = Object.entries(PRODUCT_ICON_MAP).find(([k]) => p.name?.includes(k))?.[1] || '🍽️'
  return {
    ...p,
    categoryId: p.category_id,     // UI uses categoryId
    tax: p.tax_percentage,          // UI uses tax
    icon,
    status: p.is_active ? 'available' : 'unavailable',  // UI uses status string
    archived: !p.is_active,         // UI uses archived bool
  }
}

function normalizeUser(u) {
  return {
    ...u,
    type: u.role?.toLowerCase() === 'admin' ? 'user' : 'employee',
    status: u.is_active ? 'active' : 'disabled',
  }
}

function normalizePaymentMethod(pm) {
  return {
    ...pm,
    active: pm.enabled,
    upiId: pm.upi_id || '',
    type: pm.name?.toLowerCase().includes('cash') ? 'cash'
        : pm.name?.toLowerCase().includes('card') ? 'card'
        : pm.name?.toLowerCase().includes('upi') ? 'upi' 
        : pm.name?.toLowerCase().includes('razorpay') ? 'razorpay' : 'cash',
  }
}

function normalizeOrder(o) {
  const statusMap = {
    DRAFT: 'draft', SENT_TO_KITCHEN: 'draft', PREPARING: 'draft',
    READY: 'draft', PAID: 'paid', CANCELLED: 'draft'
  }
  return {
    ...o,
    id: String(o.order_number || o.id),
    date: o.created_at ? new Date(o.created_at).toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }) : '-',
    customer: o.customer_name || 'Guest',
    amount: o.total_amount || 0,
    status: statusMap[o.status] || 'draft',
    items: (o.items || []).map(i => ({
      cartItemId: String(i.id),
      productId: i.product_id,
      name: i.product_name || 'Item',
      price: i.unit_price || 0,
      qty: i.quantity || 1,
      note: ''
    }))
  }
}


export default function PosDashboard() {
  const [view, setView] = useState('pos')
  const [orders, setOrders] = useState([])
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [users, setUsers] = useState([])
  const [activeCategory, setActiveCategory] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [cart, setCart] = useState([])
  const [selectedCartItemId, setSelectedCartItemId] = useState(null)
  const [pulsedProductId, setPulsedProductId] = useState(null)

  const [orderNumber, setOrderNumber] = useState(1)
  const [orderTime, setOrderTime] = useState(formatNow())
  const [kitchenStatus, setKitchenStatus] = useState('pending')

  const [paymentMethods, setPaymentMethods] = useState([])
  const [paymentMethod, setPaymentMethod] = useState('')
  const selectedPaymentMethod = paymentMethods.find((m) => String(m.id) === String(paymentMethod))
  const [keypadMode, setKeypadMode] = useState('amount')
  const [amountBuffer, setAmountBuffer] = useState('')
  const [qtyBuffer, setQtyBuffer] = useState('')
  const [promotions, setPromotions] = useState([])
  const [couponPopupOpen, setCouponPopupOpen] = useState(false)
  const [couponCode, setCouponCode] = useState('')
  const [appliedCoupon, setAppliedCoupon] = useState(null)
  const [couponError, setCouponError] = useState('')
  const [splitOpen, setSplitOpen] = useState(false)
  const [splitCount, setSplitCount] = useState(1)

  const [table, setTable] = useState(null)
  const [orderType, setOrderType] = useState('TAKEAWAY')
  const [tableViewOpen, setTableViewOpen] = useState(false)
  const [reservationOpen, setReservationOpen] = useState(false)
  const [loyaltyOpen, setLoyaltyOpen] = useState(false)
  const [customerOpen, setCustomerOpen] = useState(false)
  const [customers, setCustomers] = useState([])
  const [activeCustomerId, setActiveCustomerId] = useState(null)
  const activeCustomer = customers.find((c) => String(c.id) === String(activeCustomerId)) || customers[0] || { id: null, name: 'Guest', email: '', phone: '', points: 0 }

  const [drawerOpen, setDrawerOpen] = useState(false)
  const [activeDrawerItem, setActiveDrawerItem] = useState(null)

  const [toast, setToast] = useState(null)
  const toastTimerRef = useRef(null)
  const pulseTimerRef = useRef(null)
  const categorySeq = useRef(0)
  const userSeq = useRef(0)

  useEffect(() => {
    async function loadData() {
      try {
        const [cats, prods, usrs, pms, custs, ords, promos] = await Promise.all([
          apiFetch('/categories'),
          apiFetch('/products'),
          apiFetch('/employees'),
          apiFetch('/payment-methods'),
          apiFetch('/customers'),
          apiFetch('/pos/orders?limit=100'),
          apiFetch('/promotions/active')
        ])
        const normalizedCats = (cats || []).map((c, i) => normalizeCategory(c, i))
        const normalizedProds = (prods || []).map(normalizeProduct)
        const normalizedUsers = (usrs || []).map(normalizeUser)
        const normalizedPMs = (pms || []).map(normalizePaymentMethod)
        if (!normalizedPMs.some(m => m.type === 'razorpay' || m.type === 'upi' || m.type === 'card')) {
          normalizedPMs.push({
            id: 'razorpay-auto',
            name: 'Razorpay',
            type: 'razorpay',
            active: true
          });
        }
        const normalizedOrds = (ords || []).map(normalizeOrder)

        setCategories(normalizedCats)
        setProducts(normalizedProds)
        setUsers(normalizedUsers)
        setPaymentMethods(normalizedPMs)
        setCustomers(custs || [])
        setOrders(normalizedOrds)
        setPromotions(promos || [])
        
        if (normalizedCats?.length) setActiveCategory(normalizedCats[0].id)
        if (normalizedPMs?.length) setPaymentMethod(normalizedPMs[0].id)
        if (custs?.length) setActiveCustomerId(custs[0].id)
        
        // Try getting active session
        try {
          const session = await apiFetch('/pos/session/current')
          setOrderNumber(session.id)
        } catch (e) {
          // If no active session, ignore
        }
      } catch (err) {
        showToast('Failed to load data: ' + err.message)
        if (err.message === 'Unauthorized' || err.message === 'Session expired') {
          clearTokens()
        }
      }
    }
    loadData()
  }, [])


  const showToast = (text) => {
    clearTimeout(toastTimerRef.current)
    setToast(text)
    toastTimerRef.current = setTimeout(() => setToast(null), 2500)
  }

  const subtotal = useMemo(() => cart.reduce((sum, item) => sum + item.price * item.qty, 0), [cart])
  const gst = useMemo(() => cart.reduce((sum, item) => sum + item.price * item.qty * ((item.tax || 0) / 100), 0), [cart])
  const serviceTax = 0

  const discountAmount = useMemo(() => {
    let amt = 0
    const orderQty = cart.reduce((sum, item) => sum + item.qty, 0)
    for (const promo of promotions) {
      if (promo.promotion_scope === 'ORDER') {
        if (promo.minimum_order_amount && subtotal >= promo.minimum_order_amount) {
          amt = Math.max(amt, promo.discount_type === 'PERCENTAGE' ? subtotal * (promo.discount_value / 100) : promo.discount_value)
        } else if (promo.minimum_quantity && orderQty >= promo.minimum_quantity) {
          amt = Math.max(amt, promo.discount_type === 'PERCENTAGE' ? subtotal * (promo.discount_value / 100) : promo.discount_value)
        }
      }
    }
    if (appliedCoupon) {
      const couponAmt = appliedCoupon.discount_type === 'PERCENTAGE' ? subtotal * (appliedCoupon.discount_value / 100) : appliedCoupon.discount_value
      amt += couponAmt
    }
    return Math.min(amt, subtotal + gst)
  }, [cart, subtotal, gst, promotions, appliedCoupon])
  const total = Math.max(0, subtotal + gst + serviceTax - discountAmount)
  const loyaltyPoints = Math.floor(total / 10)
  const tenderedNum = parseFloat(amountBuffer || '0') || 0
  const isCashSelected = selectedPaymentMethod?.type === 'cash'
  const changeDue = isCashSelected && amountBuffer !== '' ? tenderedNum - total : null
  const completeDisabled = cart.length === 0 || (isCashSelected && (amountBuffer === '' || tenderedNum < total))

  const selectedItem = cart.find((item) => item.cartItemId === selectedCartItemId) || null

  const displayValue = keypadMode === 'amount' ? amountBuffer : qtyBuffer

  const pulseProduct = (productId) => {
    clearTimeout(pulseTimerRef.current)
    setPulsedProductId(productId)
    pulseTimerRef.current = setTimeout(() => setPulsedProductId(null), 250)
  }

  const broadcastCart = async (currentCart) => {
    try {
      const currentSubtotal = currentCart.reduce((sum, item) => sum + item.price * item.qty, 0);
      const currentGst = currentCart.reduce((sum, item) => sum + item.price * item.qty * ((item.tax || 0) / 100), 0);
      const currentTotal = currentSubtotal + currentGst; // Not accounting for dynamic discount here for simplicity
      
      const sessionStr = localStorage.getItem('pos_session_id') || '1';
      await apiFetch('/customer-display/push-active-order', {
        method: 'POST',
        body: JSON.stringify({
          session_id: parseInt(sessionStr),
          cart_data: {
            items: currentCart,
            subtotal: currentSubtotal,
            tax_amount: currentGst,
            discount_amount: 0,
            total_amount: currentTotal
          }
        })
      });
    } catch (e) {
      console.error("Failed to broadcast cart:", e);
    }
  };

  const handleCreateReservation = async (reservationData) => {
    try {
      await apiFetch('/reservations/', {
        method: 'POST',
        body: JSON.stringify(reservationData)
      });
      showToast('Reservation confirmed and email sent!');
      setReservationOpen(false);
    } catch (e) {
      showToast('Failed to create reservation: ' + e.message);
    }
  };

  const addToCart = (product) => {
    let cartItemSeq = 0;
    setCart((prev) => {
      let newCart;
      const existing = prev.find((item) => item.productId === product.id)
      if (existing) {
        newCart = prev.map((item) => (item.productId === product.id ? { ...item, qty: item.qty + 1 } : item))
      } else {
        cartItemSeq += 1
        newCart = [
          ...prev,
          { cartItemId: `cart-${cartItemSeq}`, productId: product.id, name: product.name, price: product.price, tax: product.tax || 0, qty: 1, note: '' },
        ]
      }
      broadcastCart(newCart);
      return newCart;
    })
    pulseProduct(product.id)
  }

  const incQty = (id) => setCart((prev) => {
    const next = prev.map((item) => (item.cartItemId === id ? { ...item, qty: item.qty + 1 } : item));
    broadcastCart(next);
    return next;
  })

  const decQty = (id) =>
    setCart((prev) => {
      const next = prev.flatMap((item) => {
        if (item.cartItemId !== id) return [item]
        if (item.qty <= 1) return []
        return [{ ...item, qty: item.qty - 1 }]
      });
      broadcastCart(next);
      return next;
    })

  const removeItem = (id) => {
    setCart((prev) => {
      const next = prev.filter((item) => item.cartItemId !== id);
      broadcastCart(next);
      return next;
    })
    if (selectedCartItemId === id) setSelectedCartItemId(null)
  }

  const setNote = (id, text) => setCart((prev) => prev.map((item) => (item.cartItemId === id ? { ...item, note: text } : item)))

  const selectCartItem = (id) => setSelectedCartItemId((prev) => (prev === id ? null : id))

  const upsertOrder = (status) => {
    const id = formatOrderId(orderNumber)
    const record = { id, date: orderTime, customer: activeCustomer.name, amount: total, status, items: cart }
    setOrders((prev) => {
      const existing = prev.find((o) => o.id === id)
      if (existing) return prev.map((o) => (o.id === id ? record : o))
      return [record, ...prev]
    })
  }

  const sendToKitchen = async () => {
    if (cart.length === 0) return
    try {
      // Get or create session
      let session
      try {
        session = await apiFetch('/pos/session/current')
      } catch (e) {
        session = await apiFetch('/pos/session/open', {
          method: 'POST',
          body: JSON.stringify({ opening_balance: 0 })
        })
      }

      const items = cart.map((item) => ({
        product_id: item.productId,
        quantity: item.qty,
        notes: item.note || null
      }))

      // Create order with all cart items in one call
      const order = await apiFetch('/pos/orders', {
        method: 'POST',
        body: JSON.stringify({
          session_id: session.id,
          order_type: orderType,
          table_id: table !== 'No' ? table : null,
          customer_id: (activeCustomerId && typeof activeCustomerId === 'number') ? activeCustomerId : null,
          items,
          discount_amount: discountAmount || 0,
          coupon_id: appliedCoupon ? appliedCoupon.id : null,
          promotion_id: (promotions && promotions.length > 0) ? promotions[0].id : null
        })
      })

      // Send the created order to kitchen
      await apiFetch(`/pos/cart/${order.id}/send-to-kitchen`, { method: 'POST' })
      setKitchenStatus('sent')
      setOrderNumber(order.id)
      showToast('Order sent to kitchen 👨\u200d🍳')
    } catch (err) {
      showToast('Failed to send to kitchen: ' + err.message)
    }
  }


  const applyQtyBuffer = (nextBuffer) => {
    setQtyBuffer(nextBuffer)
    if (nextBuffer !== '' && selectedCartItemId) {
      const qty = Math.max(1, Math.min(99, parseInt(nextBuffer, 10) || 1))
      setCart((prev) => prev.map((item) => (item.cartItemId === selectedCartItemId ? { ...item, qty } : item)))
    }
  }

  const onDigit = (key) => {
    if (key === 'C') {
      if (keypadMode === 'amount') setAmountBuffer('')
      else applyQtyBuffer('')
      return
    }
    if (key === '+/-') {
      if (keypadMode === 'amount') setAmountBuffer((prev) => prev.slice(0, -1))
      else applyQtyBuffer(qtyBuffer.slice(0, -1))
      return
    }
    if (keypadMode === 'amount') setAmountBuffer((prev) => (prev.length >= 6 ? prev : prev + key))
    else applyQtyBuffer(qtyBuffer.length >= 2 ? qtyBuffer : qtyBuffer + key)
  }

  const onAction = (type) => {
    if (type.startsWith('quick-')) {
      const value = parseInt(type.split('-')[1], 10)
      setKeypadMode('amount')
      setAmountBuffer((prev) => String((parseFloat(prev || '0') || 0) + value))
    } else if (type === 'custom-price') {
      setKeypadMode('amount')
      setAmountBuffer('')
    }
  }

  const resetForNextOrder = () => {
    setCart([])
    setSelectedCartItemId(null)
    setKitchenStatus('pending')
    setAmountBuffer('')
    setQtyBuffer('')
    setAppliedCoupon(null)
    setCouponCode('')
    setSplitOpen(false)
    setSplitCount(1)
    setOrderNumber((prev) => prev + 1)
    setOrderTime(formatNow())
    broadcastCart([])
  }

  const loadRazorpayScript = () => {
    return new Promise((resolve) => {
      if (window.Razorpay) {
        resolve(true);
        return;
      }
      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  };

  const completePayment = async () => {
    if (completeDisabled) return
    try {
      let activeOrder = typeof orderNumber === 'number' && kitchenStatus === 'sent' ? orderNumber : null

      if (kitchenStatus === 'pending' || !activeOrder) {
        // Need to create order first
        let session
        try {
          session = await apiFetch('/pos/session/current')
        } catch(e) {
          session = await apiFetch('/pos/session/open', { method: 'POST', body: JSON.stringify({ opening_balance: 0 }) })
        }
        const order = await apiFetch('/pos/orders', {
          method: 'POST',
          body: JSON.stringify({
            session_id: session.id,
            order_type: orderType,
            table_id: table !== 'No' ? table : null,
            customer_id: (activeCustomerId && typeof activeCustomerId === 'number') ? activeCustomerId : null,
            items: cart.map(i => ({ product_id: i.productId, quantity: i.qty })),
            discount_amount: discountAmount || 0,
            coupon_id: appliedCoupon ? appliedCoupon.id : null,
            promotion_id: (promotions && promotions.length > 0) ? promotions[0].id : null
          })
        })
        activeOrder = order.id
      }

      // Determine payment method type for fallback
      const pmType = selectedPaymentMethod?.type || 'cash'
      const pmId = selectedPaymentMethod?.id && !String(selectedPaymentMethod.id).startsWith('razorpay') ? Number(selectedPaymentMethod.id) : null

      if (pmType === 'upi' || pmType === 'card' || pmType === 'razorpay') {
        const scriptLoaded = await loadRazorpayScript();
        if (!scriptLoaded) {
          throw new Error('Razorpay SDK failed to load. Check your connection.');
        }

        // Create Razorpay Order
        const rzpRes = await apiFetch('/pos/razorpay/create-order', {
          method: 'POST',
          body: JSON.stringify({ amount: total })
        });
        
        const options = {
          key: rzpRes.key,
          amount: rzpRes.amount,
          currency: "INR",
          name: "Cafe POS",
          description: `Order #${activeOrder}`,
          order_id: rzpRes.razorpay_order_id,
          handler: async function (response) {
            try {
              // Verify Signature
              await apiFetch('/pos/razorpay/verify', {
                method: 'POST',
                body: JSON.stringify({
                  razorpay_order_id: response.razorpay_order_id,
                  razorpay_payment_id: response.razorpay_payment_id,
                  razorpay_signature: response.razorpay_signature
                })
              });
              
              // Proceed to pay in local DB
              await apiFetch(`/pos/receipt/${activeOrder}/pay`, {
                method: 'POST',
                body: JSON.stringify({
                  payment_method_id: pmId,
                  payment_method_type: pmType,
                  amount: total,
                  transaction_reference: response.razorpay_payment_id
                })
              });
              showToast(`Payment of ₹${total.toFixed(0)} received via ${selectedPaymentMethod?.name || 'Razorpay'} 🎉`);
              try {
                const updatedOrders = await apiFetch('/pos/orders?limit=100');
                setOrders((updatedOrders || []).map(normalizeOrder));
              } catch(e) {}
              resetForNextOrder();
            } catch(e) {
              showToast('Payment verification failed: ' + e.message);
            }
          },
          prefill: {
            name: activeCustomer?.name || 'Customer',
            email: activeCustomer?.email || 'guest@example.com',
            contact: activeCustomer?.phone || ''
          },
          theme: {
            color: "#D4A056"
          }
        };
        const rzp = new window.Razorpay(options);
        rzp.on('payment.failed', function (response){
           showToast('Payment Failed: ' + response.error.description);
        });
        rzp.open();
        return; // wait for handler to execute
      }

      await apiFetch(`/pos/receipt/${activeOrder}/pay`, {
        method: 'POST',
        body: JSON.stringify({
          payment_method_id: pmId,
          payment_method_type: pmType,
          amount: isCashSelected && tenderedNum > total ? tenderedNum : total,
          transaction_reference: `TXN-${pmType.toUpperCase()}-${Date.now()}`
        })
      })
      showToast(`Payment of ₹${total.toFixed(0)} received via ${selectedPaymentMethod?.name || 'Cash'} 🎉`)
      // Refresh orders list
      try {
        const updatedOrders = await apiFetch('/pos/orders?limit=100')
        setOrders((updatedOrders || []).map(normalizeOrder))
      } catch(e) {}
      resetForNextOrder()
    } catch (err) {
      showToast('Payment failed: ' + err.message)
    }
  }


  const newOrder = () => {
    resetForNextOrder()
    showToast('Started new order 🆕')
  }

  const editOrder = (order) => {
    setCart(order.items)
    setOrderNumber(parseInt(order.id, 10))
    setOrderTime(order.date)
    setKitchenStatus('pending')
    setSelectedCartItemId(null)
    setAmountBuffer('')
    setDiscountBuffer('')
    setQtyBuffer('')
    setView('pos')
    showToast(`Editing order #${order.id}`)
  }

  const deleteOrder = (id) => {
    setOrders((prev) => prev.filter((o) => o.id !== id))
    showToast(`Order #${id} deleted`)
  }

  const selectTable = (n) => {
    setTable(n)
    if (n && n !== 'No') {
      setOrderType('DINE_IN')
    }
    setTableViewOpen(false)
  }

  const selectCustomer = (id) => {
    setActiveCustomerId(id)
    setCustomerOpen(false)
  }

  const saveCustomer = async (id, fields) => {
    try {
      if (id && !String(id).startsWith('c')) {
        const res = await apiFetch(`/customers/${id}`, { method: 'PUT', body: JSON.stringify(fields) })
        setCustomers((prev) => prev.map((c) => (c.id === id ? { ...c, ...res } : c)))
      } else {
        const res = await apiFetch('/customers', { method: 'POST', body: JSON.stringify({ ...fields, points: 0 }) })
        setCustomers((prev) => [...prev, res])
        setActiveCustomerId(res.id)
      }
    } catch(e) { showToast('Error: ' + e.message) }
  }

  const deleteCustomer = async (id) => {
    try {
      if (!String(id).startsWith('c')) {
        await apiFetch(`/customers/${id}`, { method: 'DELETE' })
      }
      setCustomers((prev) => {
        const next = prev.filter((c) => c.id !== id)
        if (activeCustomerId === id) setActiveCustomerId(next[0]?.id ?? null)
        return next
      })
      showToast('Customer deleted')
    } catch(e) { showToast('Error: ' + e.message) }
  }

  const selectDrawerItem = (id) => {
    setActiveDrawerItem(id)
    setDrawerOpen(false)
    if (id === 'dashboard') {
      setView('pos')
      return
    }
    if (id === 'products') {
      setView('products')
      return
    }
    if (id === 'categories') {
      setView('categories')
      return
    }
    if (id === 'paymentMethods') {
      setView('paymentMethods')
      return
    }
    if (id === 'employees') {
      setView('users')
      return
    }
    if (id === 'kitchen') {
      window.open('/kds', '_blank')
      return
    }
    if (id === 'reports') {
      setView('reports')
      return
    }
    if (id === 'promotions') {
      setView('promotions')
      return
    }
    const item = DRAWER_ITEMS.find((d) => d.id === id)
    showToast(id === 'logout' ? 'Logged out 👋' : `${item.label} (coming soon)`)
  }

  const saveProduct = async (id, fields) => {
    try {
      if (id && !String(id).startsWith('p')) {
        const res = await apiFetch(`/products/${id}`, { method: 'PUT', body: JSON.stringify(fields) })
        setProducts((prev) => prev.map((p) => (p.id === id ? normalizeProduct(res) : p)))
      } else {
        const res = await apiFetch('/products', { method: 'POST', body: JSON.stringify(fields) })
        setProducts((prev) => [...prev, normalizeProduct(res)])
      }
      showToast('Product saved')
    } catch (e) {
      showToast('Error saving product: ' + e.message)
    }
  }


  const setProductsArchived = async (ids, archived) => {
    try {
      await Promise.all(ids.map(id => apiFetch(`/products/${id}`, { 
        method: 'PUT', 
        body: JSON.stringify({ is_active: !archived }) 
      })))
      setProducts((prev) => prev.map((p) => (ids.includes(p.id) ? { ...p, archived } : p)))
      showToast(archived ? 'Product(s) archived' : 'Product(s) activated')
    } catch (e) {
      showToast('Error: ' + e.message)
    }
  }

  const createCategory = async (fields) => {
    try {
      const res = await apiFetch('/categories', { method: 'POST', body: JSON.stringify(fields) })
      setCategories((prev) => [...prev, { ...res, icon: '🏷' }])
      return res.id
    } catch (e) {
      showToast('Error: ' + e.message)
    }
  }

  const addBlankCategory = () => {
    categorySeq.current += 1
    const newId = `cat${categorySeq.current}`
    setCategories((prev) => [...prev, { id: newId, name: '', color: CATEGORY_COLORS[0], icon: '🏷' }])
  }

  const updateCategory = async (id, fields) => {
    if (String(id).startsWith('cat')) {
      // It's a blank unsaved category
      if (fields.name) {
        const res = await apiFetch('/categories', { method: 'POST', body: JSON.stringify(fields) })
        setCategories((prev) => prev.map((c) => (c.id === id ? { ...res, icon: '🏷' } : c)))
      }
    } else {
      try {
        const res = await apiFetch(`/categories/${id}`, { method: 'PUT', body: JSON.stringify(fields) })
        setCategories((prev) => prev.map((c) => (c.id === id ? { ...c, ...res } : c)))
      } catch (e) {
        showToast('Error: ' + e.message)
      }
    }
  }

  const deleteCategoryById = async (id) => {
    try {
      if (!String(id).startsWith('cat')) {
        await apiFetch(`/categories/${id}`, { method: 'DELETE' })
      }
      setCategories((prev) => prev.filter((c) => c.id !== id))
      if (activeCategory === id) setActiveCategory(categories.find((c) => c.id !== id)?.id || '')
      showToast('Category deleted')
    } catch (e) {
      showToast('Error: ' + e.message)
    }
  }

  const savePaymentMethod = async (id, fields) => {
    try {
      if (id && !String(id).startsWith('pm-new')) {
        const res = await apiFetch(`/payment-methods/${id}`, { method: 'PUT', body: JSON.stringify(fields) })
        setPaymentMethods((prev) => prev.map((m) => (m.id === id ? { ...m, ...res } : m)))
        if (id === paymentMethod && fields.active === false) {
          const fallback = paymentMethods.find((m) => m.id !== id && m.active)
          setPaymentMethod(fallback?.id || '')
        }
      } else {
        const res = await apiFetch('/payment-methods', { method: 'POST', body: JSON.stringify(fields) })
        setPaymentMethods((prev) => [...prev, { ...res, active: true }])
      }
      showToast('Payment method saved')
    } catch(e) { showToast('Error: ' + e.message) }
  }

  const deletePaymentMethod = async (id) => {
    try {
      if (!String(id).startsWith('pm-new')) {
        await apiFetch(`/payment-methods/${id}`, { method: 'DELETE' })
      }
      setPaymentMethods((prev) => {
        const next = prev.filter((m) => m.id !== id)
        if (paymentMethod === id) setPaymentMethod(next.find((m) => m.active)?.id || next[0]?.id || '')
        return next
      })
      showToast('Payment method deleted')
    } catch(e) { showToast('Error: ' + e.message) }
  }

  const addUser = () => {
    userSeq.current += 1
    const newId = `u${userSeq.current}`
    setUsers((prev) => [...prev, { id: newId, name: '', type: 'user', status: 'active' }])
  }

  const updateUser = async (id, fields) => {
    try {
      if (String(id).startsWith('u')) {
        const res = await apiFetch('/employees', { method: 'POST', body: JSON.stringify({ ...fields, password: 'password123', role: 'EMPLOYEE' }) })
        setUsers((prev) => prev.map((u) => (u.id === id ? { ...u, ...res } : u)))
      } else {
        const res = await apiFetch(`/employees/${id}`, { method: 'PUT', body: JSON.stringify(fields) })
        setUsers((prev) => prev.map((u) => (u.id === id ? { ...u, ...res } : u)))
      }
    } catch(e) { showToast('Error: ' + e.message) }
  }

  const deleteUsers = async (ids) => {
    try {
      await Promise.all(ids.filter(id => !String(id).startsWith('u')).map(id => apiFetch(`/employees/${id}`, { method: 'DELETE' })))
      setUsers((prev) => prev.filter((u) => !ids.includes(u.id)))
      showToast('User(s) deleted')
    } catch(e) { showToast('Error: ' + e.message) }
  }

  const archiveUsers = async (ids) => {
    try {
      await Promise.all(ids.filter(id => !String(id).startsWith('u')).map(id => apiFetch(`/employees/${id}`, { method: 'PUT', body: JSON.stringify({ is_active: false }) })))
      setUsers((prev) => prev.map((u) => (ids.includes(u.id) ? { ...u, status: 'disabled', is_active: false } : u)))
      showToast('User(s) archived')
    } catch(e) { showToast('Error: ' + e.message) }
  }

  const changeUserPassword = (id) => {
    const user = users.find((u) => u.id === id)
    showToast(`Password updated for ${user?.name || 'user'} 🔒`)
  }

  const handleApplyCoupon = async (e) => {
    e.preventDefault()
    setCouponError('')
    if (!couponCode) return
    try {
      const res = await apiFetch('/coupons/validate', {
        method: 'POST',
        body: JSON.stringify({ code: couponCode, order_total: subtotal })
      })
      if (res.valid && res.coupon) {
        setAppliedCoupon(res.coupon)
        setCouponPopupOpen(false)
        showToast('Coupon applied! 🎟️')
      } else {
        setCouponError(res.message || 'Invalid coupon code')
      }
    } catch (err) {
      setCouponError('Validation failed: ' + err.message)
    }
  }

  return (
    <div className="pos-dashboard">
      <TopNav
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        table={table}
        tableViewOpen={tableViewOpen}
        onToggleTableView={() => setTableViewOpen((v) => !v)}
        onSelectTable={selectTable}
        view={view}
        onToggleView={() => setView((v) => (v === 'orders' ? 'pos' : 'orders'))}
        onGoHome={() => setView('pos')}
        onNewOrder={newOrder}
        reservationOpen={reservationOpen}
        onToggleReservation={() => {
          setReservationOpen((v) => !v)
          setLoyaltyOpen(false)
        }}
        onSubmitReservation={handleCreateReservation}
        loyaltyOpen={loyaltyOpen}
        onToggleLoyalty={() => {
          setLoyaltyOpen((v) => !v)
          setReservationOpen(false)
        }}
        customer={activeCustomer}
        customers={customers}
        activeCustomerId={activeCustomerId}
        customerOpen={customerOpen}
        onToggleCustomer={() => setCustomerOpen((v) => !v)}
        onSelectCustomer={selectCustomer}
        onSaveCustomer={saveCustomer}
        onDeleteCustomer={deleteCustomer}
        onToggleDrawer={() => setDrawerOpen((v) => !v)}
      />

      {view === 'pos' ? (
        <div className="pos-main">
          <CategorySidebar
            categories={categories}
            activeCategory={activeCategory}
            onSelectCategory={(id) => {
              setActiveCategory(id)
              setSearchQuery('')
            }}
          />

          <ProductGrid
            products={products}
            activeCategory={activeCategory}
            searchQuery={searchQuery}
            onAddToCart={addToCart}
            pulsedProductId={pulsedProductId}
          />

          <CartPanel
            cart={cart}
            orderNumber={orderNumber}
            orderTime={orderTime}
            kitchenStatus={kitchenStatus}
            selectedCartItemId={selectedCartItemId}
            onSelectCartItem={selectCartItem}
            onIncQty={incQty}
            onDecQty={decQty}
            onRemoveItem={removeItem}
            onNoteChange={setNote}
            onSendToKitchen={sendToKitchen}
            onOpenCustomer={() => setCustomerOpen(true)}
            onOpenCouponPopup={() => setCouponPopupOpen(true)}
            onSendReceipt={async () => {
              if (!orderNumber || kitchenStatus === 'pending') {
                return showToast('Complete order first')
              }
              try {
                await apiFetch(`/pos/receipt/${orderNumber}/email`, {
                  method: 'POST',
                  body: JSON.stringify({ email: activeCustomer?.email || 'guest@example.com' })
                })
                showToast('Receipt sent to customer 📨')
              } catch (e) {
                showToast('Failed to send receipt: ' + e.message)
              }
            }}
            subtotal={subtotal}
            gst={gst}
            serviceTax={serviceTax}
            discountAmount={discountAmount}
            total={total}
            orderType={orderType}
            onChangeOrderType={setOrderType}
          />

          <PaymentPanel
            paymentMethods={paymentMethods}
            paymentMethod={paymentMethod}
            onSelectPaymentMethod={setPaymentMethod}
            total={total}
            loyaltyPoints={loyaltyPoints}
            keypadMode={keypadMode}
            onSetKeypadMode={setKeypadMode}
            displayValue={displayValue}
            onDigit={onDigit}
            onAction={onAction}
            selectedItemName={selectedItem?.name}
            splitCount={splitCount}
            splitOpen={splitOpen}
            onToggleSplit={() => setSplitOpen((v) => !v)}
            onChangeSplitCount={setSplitCount}
            changeDue={changeDue}
            onCompletePayment={completePayment}
            completeDisabled={completeDisabled}
          />
        </div>
      ) : view === 'orders' ? (
        <OrdersPage orders={orders} onEditOrder={editOrder} onDeleteOrder={deleteOrder} />
      ) : view === 'products' ? (
        <ProductsPage
          products={products}
          categories={categories}
          onSaveProduct={saveProduct}
          onSetArchived={setProductsArchived}
          onCreateCategory={createCategory}
        />
      ) : view === 'categories' ? (
        <CategoryPage
          categories={categories}
          onAddCategory={addBlankCategory}
          onUpdateCategory={updateCategory}
          onDeleteCategory={deleteCategoryById}
          onReorderCategories={setCategories}
        />
      ) : view === 'paymentMethods' ? (
        <PaymentMethodPage
          paymentMethods={paymentMethods}
          onSavePaymentMethod={savePaymentMethod}
          onDeletePaymentMethod={deletePaymentMethod}
          onReorderPaymentMethods={setPaymentMethods}
        />
      ) : view === 'users' ? (
        <UserPage
          users={users}
          onAddUser={addUser}
          onUpdateUser={updateUser}
          onDeleteUsers={deleteUsers}
          onArchiveUsers={archiveUsers}
          onChangePassword={changeUserPassword}
        />
      ) : view === 'promotions' ? (
        <PromotionsPage />
      ) : (
        <ReportsPage
          orders={orders}
          products={products}
          categories={categories}
          customers={customers}
        />
      )}

      {couponPopupOpen && (
        <div className="modal-overlay" onClick={() => setCouponPopupOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Apply Coupon</h2>
            <form onSubmit={handleApplyCoupon}>
              <div className="form-group">
                <label>Coupon Code</label>
                <input
                  type="text"
                  autoFocus
                  value={couponCode}
                  onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
                  placeholder="e.g. FLAT10"
                />
              </div>
              {couponError && <p className="error-text" style={{color: 'red', marginTop: -10}}>{couponError}</p>}
              {appliedCoupon && <p className="success-text" style={{color: 'green', marginTop: -10}}>Currently applied: {appliedCoupon.code}</p>}
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => { setAppliedCoupon(null); setCouponCode(''); setCouponPopupOpen(false) }}>
                  Remove
                </button>
                <button type="submit" className="btn-primary" disabled={!couponCode}>
                  Apply
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <RightDrawer
        open={drawerOpen}
        activeItem={activeDrawerItem}
        onSelect={selectDrawerItem}
        onClose={() => setDrawerOpen(false)}
      />

      {toast && <div className="pos-toast">{toast}</div>}
    </div>
  )
}
