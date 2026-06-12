import { Link, NavLink, useNavigate } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'Home', end: true },
  { to: '/detect', label: 'Analyzer' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/assistant', label: 'AI Assistant' },
  { to: '/campaigns', label: 'Campaigns' },
]

export default function Navbar() {
  const navigate = useNavigate()
  const isLoggedIn = !!localStorage.getItem('access_token')

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    navigate('/')
  }

  return (
    <nav className="navbar navbar-expand-lg navbar-hsds sticky-top">
      <div className="container">
        <Link className="navbar-brand" to="/">
          <span className="brand-icon">🛡️</span>
          <span>TextGuard</span>
        </Link>

        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#nav"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon" />
        </button>

        <div className="collapse navbar-collapse" id="nav">
          <ul className="navbar-nav mx-auto">
            {navItems.map((item) => (
              <li className="nav-item" key={item.to}>
                <NavLink className="nav-link" to={item.to} end={item.end}>
                  {item.label}
                </NavLink>
              </li>
            ))}
            {isLoggedIn && (
              <li className="nav-item">
                <NavLink className="nav-link" to="/admin">Admin</NavLink>
              </li>
            )}
          </ul>

          <div className="d-flex align-items-center gap-3 py-3 py-lg-0">
            <span className="badge-ai-powered">✨ AI Powered</span>
            {isLoggedIn ? (
              <>
                <div className="avatar-circle">
                  A
                  <span className="online-dot" />
                </div>
                <button className="btn btn-outline-hsds btn-sm" onClick={handleLogout}>
                  Logout
                </button>
              </>
            ) : (
              <Link className="btn btn-hsds btn-sm" to="/login">Login</Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
