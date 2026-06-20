import { useState, useEffect } from 'react'
import PosDashboard from './pos/PosDashboard'
import KdsPage from './pos/KdsPage'
import AuthPage from './components/AuthPage'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('access_token'))

  useEffect(() => {
    const handleAuthChange = () => {
      setIsAuthenticated(!!localStorage.getItem('access_token'))
    }
    window.addEventListener('auth_changed', handleAuthChange)
    return () => window.removeEventListener('auth_changed', handleAuthChange)
  }, [])

  const isKdsRoute = window.location.pathname.toLowerCase() === '/kds'

  if (!isAuthenticated) {
    return <AuthPage onLogin={() => setIsAuthenticated(true)} />
  }

  return isKdsRoute ? <KdsPage /> : <PosDashboard />
}

export default App
