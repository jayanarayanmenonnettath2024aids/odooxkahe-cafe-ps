import { useEffect, useRef, useState } from 'react'
import { USER_TYPES, USER_STATUS_META } from './data'
import ChangePasswordModal from './ChangePasswordModal'
import './UserPage.css'

export default function UserPage({ users, onAddUser, onUpdateUser, onDeleteUsers, onArchiveUsers, onChangePassword }) {
  const [query, setQuery] = useState('')
  const [selectedIds, setSelectedIds] = useState([])
  const [actionOpen, setActionOpen] = useState(false)
  const [passwordTarget, setPasswordTarget] = useState(null)
  const lastInputRef = useRef(null)
  const prevLengthRef = useRef(users.length)

  useEffect(() => {
    if (users.length > prevLengthRef.current) {
      lastInputRef.current?.focus()
    }
    prevLengthRef.current = users.length
  }, [users.length])

  const q = query.trim().toLowerCase()
  const filtered = users.filter((u) => {
    const uStatus = u.status || (u.is_active ? 'active' : 'disabled')
    const uType = u.type || (u.role?.toLowerCase() === 'admin' ? 'user' : 'employee')
    if (!q) return true
    return u.name.toLowerCase().includes(q) || uType.includes(q) || uStatus.includes(q)
  })

  const toggleSelect = (id) => {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]))
  }

  const handleDelete = () => {
    onDeleteUsers(selectedIds)
    setSelectedIds([])
    setActionOpen(false)
  }

  const handleArchive = () => {
    onArchiveUsers(selectedIds)
    setSelectedIds([])
    setActionOpen(false)
  }

  const handleChangePasswordClick = () => {
    const target = users.find((u) => u.id === selectedIds[0])
    setPasswordTarget(target)
    setActionOpen(false)
  }

  return (
    <section className="user-page">
      <h1 className="user-page-title">User/employee</h1>

      <div className="user-toolbar">
        <button type="button" className="user-new-btn" onClick={onAddUser}>
          <span>🗋+</span> New
        </button>

        {selectedIds.length > 0 && (
          <div className="user-action-wrap">
            <button type="button" className="user-action-btn" onClick={() => setActionOpen((v) => !v)}>
              ⭐ Action ({selectedIds.length})
            </button>
            {actionOpen && (
              <div className="user-action-menu">
                <button type="button" onClick={handleDelete}>Delete</button>
                <button type="button" onClick={handleArchive}>Archived</button>
                <button type="button" onClick={handleChangePasswordClick}>Change password</button>
              </div>
            )}
          </div>
        )}

        <div className="user-search">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by name, type or status..."
          />
          <span className="search-icon" aria-hidden="true">🔍</span>
        </div>
      </div>

      <div className="user-table">
        <div className="user-row user-head">
          <span />
          <span />
          <span>Name</span>
          <span>Type</span>
          <span>Status</span>
        </div>
        {filtered.map((u, index) => {
          const uStatus = u.status || (u.is_active ? 'active' : 'disabled')
          const uType = u.type || (u.role?.toLowerCase() === 'admin' ? 'user' : 'employee')
          const status = USER_STATUS_META[uStatus] || USER_STATUS_META.active
          return (
            <div key={u.id} className="user-row user-data">
              <span className="user-checkbox-cell">
                <input type="checkbox" checked={selectedIds.includes(u.id)} onChange={() => toggleSelect(u.id)} />
              </span>
              <span className="user-avatar">👤</span>
              <input
                ref={index === filtered.length - 1 ? lastInputRef : null}
                type="text"
                className="user-name-input"
                placeholder="User name"
                value={u.name}
                onChange={(e) => onUpdateUser(u.id, { name: e.target.value })}
              />
              <select value={uType} onChange={(e) => onUpdateUser(u.id, { type: e.target.value })}>
                {USER_TYPES.map((t) => (
                  <option key={t} value={t}>{t === 'user' ? 'User' : 'Employee'}</option>
                ))}
              </select>
              <button
                type="button"
                className="user-status-pill"
                style={{ background: status.bg, color: status.color }}
                onClick={() => onUpdateUser(u.id, { status: uStatus === 'active' ? 'disabled' : 'active' })}
              >
                {status.label}
              </button>
            </div>
          )
        })}
        {filtered.length === 0 && <p className="user-empty">No users found.</p>}
      </div>

      {passwordTarget && (
        <ChangePasswordModal
          userName={passwordTarget.name}
          onClose={() => setPasswordTarget(null)}
          onConfirm={(password) => {
            onChangePassword(passwordTarget.id, password)
            setPasswordTarget(null)
          }}
        />
      )}
    </section>
  )
}
