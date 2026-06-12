import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authAPI } from '../api/client'

export default function Login() {
  const [isRegister, setIsRegister] = useState(false)
  const [form, setForm] = useState({ email: '', password: '', password_confirm: '', username: '', first_name: '' })
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      if (isRegister) {
        await authAPI.register(form)
      }
      const { data } = await authAPI.login({ email: form.email, password: form.password })
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      navigate('/dashboard')
    } catch (err) {
      const msg = err.response?.data
      setError(typeof msg === 'object' ? JSON.stringify(msg) : 'Authentication failed.')
    }
  }

  return (
    <div className="page-container">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-md-5">
            <div className="card card-hsds p-4">
              <h3 className="text-center mb-4">{isRegister ? 'Register' : 'Login'}</h3>
              {error && <div className="alert alert-danger small">{error}</div>}
              <form onSubmit={handleSubmit}>
                {isRegister && (
                  <>
                    <div className="mb-3">
                      <input className="form-control form-control-hsds" placeholder="Username" required
                        value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
                    </div>
                    <div className="mb-3">
                      <input className="form-control form-control-hsds" placeholder="First Name" required
                        value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
                    </div>
                  </>
                )}
                <div className="mb-3">
                  <input type="email" className="form-control form-control-hsds" placeholder="Email" required
                    value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
                </div>
                <div className="mb-3">
                  <input type="password" className="form-control form-control-hsds" placeholder="Password" required
                    value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
                </div>
                {isRegister && (
                  <div className="mb-3">
                    <input type="password" className="form-control form-control-hsds" placeholder="Confirm Password" required
                      value={form.password_confirm} onChange={(e) => setForm({ ...form, password_confirm: e.target.value })} />
                  </div>
                )}
                <button type="submit" className="btn btn-hsds w-100 mb-3">
                  {isRegister ? 'Create Account' : 'Login'}
                </button>
              </form>
              <p className="text-center small text-muted mb-0">
                {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
                <button className="btn btn-link btn-sm p-0" style={{ color: 'var(--hsds-primary)' }} onClick={() => setIsRegister(!isRegister)}>
                  {isRegister ? 'Login' : 'Register'}
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
