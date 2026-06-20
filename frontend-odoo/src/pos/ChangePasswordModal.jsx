import { useState } from 'react'

export default function ChangePasswordModal({ userName, onConfirm, onClose }) {
  const [password, setPassword] = useState('')

  return (
    <div className="change-password-backdrop" onClick={onClose}>
      <div className="change-password-modal" onClick={(e) => e.stopPropagation()}>
        <div className="change-password-header">
          <h3>Change Password</h3>
          <button type="button" className="change-password-close" onClick={onClose}>✕</button>
        </div>
        <p className="change-password-subtext">Change password for {userName}</p>
        <input
          type="password"
          placeholder="new password enter here"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button
          type="button"
          className="change-password-enter-btn"
          disabled={!password.trim()}
          onClick={() => onConfirm(password.trim())}
        >
          Enter
        </button>
      </div>
    </div>
  )
}
