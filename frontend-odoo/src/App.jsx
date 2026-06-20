import { useState, useEffect } from 'react'
import PosDashboard from './pos/PosDashboard'
import KdsPage from './pos/KdsPage'
import AuthPage from './components/AuthPage'
import SelfOrderApp from './self-ordering/SelfOrderApp'
import CustomerDisplayApp from './customer-display/CustomerDisplayApp'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('access_token'))

  useEffect(() => {
    const handleAuthChange = () => {
      setIsAuthenticated(!!localStorage.getItem('access_token'))
    }
    window.addEventListener('auth_changed', handleAuthChange)
    return () => window.removeEventListener('auth_changed', handleAuthChange)
  }, [])

  const path = window.location.pathname.toLowerCase()
  const isKdsRoute = path === '/kds'
  const isSelfOrderRoute = path.startsWith('/s/')
  const isCustomerDisplayRoute = path.startsWith('/customer-display')

  // Public routes
  if (isSelfOrderRoute) {
    const tableToken = path.replace('/s/', '')
    return <SelfOrderApp tableToken={tableToken} />
  }

  if (isCustomerDisplayRoute) {
    return <CustomerDisplayApp />
  }

  if (!isAuthenticated) {
    return <AuthPage onLogin={() => setIsAuthenticated(true)} />
  }

  return isKdsRoute ? <KdsPage /> : <PosDashboard />
}

export default App
