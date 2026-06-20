import { useState } from 'react'
import './AuthPage.css'

const FEATURES = [
  'Freshly Brewed Coffee',
  'Online Ordering',
  'Loyalty Rewards',
  'Quick Table Reservations',
]

const BENEFITS = [
  { icon: '🎁', label: 'Welcome Reward Points' },
  { icon: '☕', label: 'Faster Checkout' },
  { icon: '📅', label: 'Table Reservation Access' },
  { icon: '💎', label: 'Member Exclusive Offers' },
]

const BEANS = Array.from({ length: 12 }, (_, i) => ({
  left: Math.round((i * 97 + 13) % 100),
  delay: (i * 1.7) % 10,
  duration: 10 + (i % 5) * 2,
  size: 16 + (i % 4) * 6,
}))

function PasswordField({ id, label, placeholder, value, onChange, visible, onToggleVisible }) {
  return (
    <div className="form-group">
      <label htmlFor={id}>{label}</label>
      <div className="input-wrapper">
        <span className="field-icon" aria-hidden="true">🔒</span>
        <input
          id={id}
          type={visible ? 'text' : 'password'}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
        />
        <button
          type="button"
          className="toggle-visibility"
          onClick={onToggleVisible}
          aria-label={visible ? 'Hide password' : 'Show password'}
        >
          {visible ? '🙈' : '👁️'}
        </button>
      </div>
    </div>
  )
}

function SocialRow() {
  return (
    <>
      <div className="divider">
        <span>OR CONTINUE WITH</span>
      </div>
      <div className="social-row">
        <button type="button" className="social-btn google" aria-label="Continue with Google">G</button>
        <button type="button" className="social-btn facebook" aria-label="Continue with Facebook">f</button>
        <button type="button" className="social-btn apple" aria-label="Continue with Apple"></button>
      </div>
    </>
  )
}

export default function AuthPage({ onLogin }) {
  const [mode, setMode] = useState('login')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(false)
  const [agreeTerms, setAgreeTerms] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')

  const [loginForm, setLoginForm] = useState({ email: '', password: '' })
  const [registerForm, setRegisterForm] = useState({
    name: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
  })

  const isLogin = mode === 'login'

  const handleLoginSubmit = async (e) => {
    e.preventDefault()
    setErrorMsg('')
    try {
      const res = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginForm)
      })
      const data = await res.json()
      if (res.ok) {
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        onLogin()
      } else {
        setErrorMsg(data.detail || data.message || 'Login failed')
      }
    } catch (err) {
      setErrorMsg(err.message)
    }
  }

  const handleRegisterSubmit = async (e) => {
    e.preventDefault()
    setErrorMsg('')
    if (!agreeTerms) return setErrorMsg('You must agree to the terms')
    if (registerForm.password !== registerForm.confirmPassword) return setErrorMsg('Passwords do not match')
    try {
      const res = await fetch('http://localhost:8000/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: registerForm.name,
          email: registerForm.email,
          password: registerForm.password,
          role: 'EMPLOYEE' // Sign up as employee
        })
      })
      const data = await res.json()
      if (res.ok) {
        setMode('login')
        setLoginForm({ email: registerForm.email, password: '' })
        setErrorMsg('Registration successful! Please login.')
      } else {
        setErrorMsg(data.detail || data.message || 'Registration failed')
      }
    } catch (err) {
      setErrorMsg(err.message)
    }
  }

  return (
    <div className="auth-page">
      <div className="overlay" />
      <div className="beans-bg" aria-hidden="true">
        {BEANS.map((bean, i) => (
          <span
            key={i}
            className="bean"
            style={{
              left: `${bean.left}%`,
              animationDelay: `${bean.delay}s`,
              animationDuration: `${bean.duration}s`,
              fontSize: `${bean.size}px`,
            }}
          >
            ☕
          </span>
        ))}
      </div>

      <div className="auth-container">
        <section className="branding">
          <div className="logo">
            <span className="logo-cup">
              ☕
              <span className="steam s1" />
              <span className="steam s2" />
              <span className="steam s3" />
            </span>
            <h1>Café Delight</h1>
          </div>
          <p className="tagline">"Brewing Happiness, One Cup at a Time"</p>
          <p className="description">
            Experience premium coffee, delicious pastries, and unforgettable moments.
          </p>
          <ul className="features">
            {FEATURES.map((feature) => (
              <li key={feature}>
                <span className="check">✓</span>
                {feature}
              </li>
            ))}
          </ul>
        </section>

        <section className="auth-card">
          {isLogin ? (
            <form className="auth-form" onSubmit={handleLoginSubmit}>
              <h2>Welcome Back ☕</h2>
              <p className="subtext">Sign in to continue your coffee journey.</p>
              {errorMsg && <div style={{color: 'red', marginBottom: 10}}>{errorMsg}</div>}

              <div className="form-group">
                <label htmlFor="login-email">Email</label>
                <div className="input-wrapper">
                  <span className="field-icon" aria-hidden="true">📧</span>
                  <input
                    id="login-email"
                    type="email"
                    placeholder="Enter your email"
                    value={loginForm.email}
                    onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                  />
                </div>
              </div>

              <PasswordField
                id="login-password"
                label="Password"
                placeholder="Enter your password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                visible={showPassword}
                onToggleVisible={() => setShowPassword((v) => !v)}
              />

              <div className="extra-options">
                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                  />
                  Remember Me
                </label>
                <a href="#" className="link">Forgot Password?</a>
              </div>

              <button type="submit" className="primary-btn">Login</button>

              <SocialRow />

              <p className="footer-text">
                Don&apos;t have an account?{' '}
                <button type="button" className="link-btn" onClick={() => setMode('register')}>
                  Create Account
                </button>
              </p>
            </form>
          ) : (
            <form className="auth-form" onSubmit={handleRegisterSubmit}>
              <h2>Join Our Coffee Family ☕</h2>
              <p className="subtext">Create an account and enjoy exclusive benefits.</p>
              {errorMsg && <div style={{color: errorMsg.includes('successful') ? 'green' : 'red', marginBottom: 10}}>{errorMsg}</div>}

              <div className="form-group">
                <label htmlFor="reg-name">Full Name</label>
                <div className="input-wrapper">
                  <span className="field-icon" aria-hidden="true">👤</span>
                  <input
                    id="reg-name"
                    type="text"
                    placeholder="Enter your full name"
                    value={registerForm.name}
                    onChange={(e) => setRegisterForm({ ...registerForm, name: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="reg-email">Email Address</label>
                <div className="input-wrapper">
                  <span className="field-icon" aria-hidden="true">📧</span>
                  <input
                    id="reg-email"
                    type="email"
                    placeholder="Enter your email"
                    value={registerForm.email}
                    onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="reg-phone">Phone Number</label>
                <div className="input-wrapper">
                  <span className="field-icon" aria-hidden="true">📱</span>
                  <input
                    id="reg-phone"
                    type="tel"
                    placeholder="Enter your phone number"
                    value={registerForm.phone}
                    onChange={(e) => setRegisterForm({ ...registerForm, phone: e.target.value })}
                  />
                </div>
              </div>

              <PasswordField
                id="reg-password"
                label="Password"
                placeholder="Create a password"
                value={registerForm.password}
                onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                visible={showPassword}
                onToggleVisible={() => setShowPassword((v) => !v)}
              />

              <PasswordField
                id="reg-confirm-password"
                label="Confirm Password"
                placeholder="Re-enter your password"
                value={registerForm.confirmPassword}
                onChange={(e) => setRegisterForm({ ...registerForm, confirmPassword: e.target.value })}
                visible={showConfirmPassword}
                onToggleVisible={() => setShowConfirmPassword((v) => !v)}
              />

              <label className="checkbox terms">
                <input
                  type="checkbox"
                  checked={agreeTerms}
                  onChange={(e) => setAgreeTerms(e.target.checked)}
                />
                I agree to Terms &amp; Conditions
              </label>

              <button type="submit" className="primary-btn register-btn">Create Account</button>

              <div className="benefits">
                {BENEFITS.map((b) => (
                  <div className="benefit" key={b.label}>
                    <span className="benefit-icon">{b.icon}</span>
                    {b.label}
                  </div>
                ))}
              </div>

              <p className="footer-text">
                Already have an account?{' '}
                <button type="button" className="link-btn" onClick={() => setMode('login')}>
                  Login
                </button>
              </p>
            </form>
          )}
        </section>
      </div>
    </div>
  )
}
