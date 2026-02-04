import React, { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import api from '../services/api'

const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [devEmail, setDevEmail] = useState('')
  const [devMode, setDevMode] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Check if token in URL (from SAML redirect)
    const token = searchParams.get('token')
    if (token) {
      localStorage.setItem('token', token)
      navigate('/canvases')
      return
    }

    // Check if already logged in
    const existingToken = localStorage.getItem('token')
    if (existingToken) {
      navigate('/canvases')
    }
  }, [searchParams, navigate])

  const handleSamlLogin = () => {
    // Redirect to SAML login endpoint
    window.location.href = '/api/v1/auth/saml/login'
  }

  const handleDevLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!devEmail.trim()) return

    setLoading(true)
    try {
      const response = await api.post('/dev-auth/login', {
        email: devEmail,
      })
      localStorage.setItem('token', response.data.access_token)
      navigate('/canvases')
    } catch (error) {
      console.error('Login failed:', error)
      alert('Login failed. Make sure the backend is running in debug mode.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>🤖 Deep Thought</h1>
        <p className="tagline">
          The Answer to Life, the Universe, and Enterprise Sales Deals
        </p>

        <button className="btn btn-primary" onClick={handleSamlLogin}>
          Sign in with SAML
        </button>

        <div style={{ margin: '1rem 0', color: '#64748b', fontSize: '0.875rem' }}>
          or
        </div>

        {!devMode ? (
          <button
            className="btn btn-secondary"
            onClick={() => setDevMode(true)}
            style={{ fontSize: '0.875rem' }}
          >
            Development Login
          </button>
        ) : (
          <form onSubmit={handleDevLogin} style={{ marginTop: '1rem', width: '100%' }}>
            <input
              type="email"
              value={devEmail}
              onChange={(e) => setDevEmail(e.target.value)}
              placeholder="Enter email (dev only)"
              required
              style={{
                width: '100%',
                padding: '0.75rem',
                marginBottom: '0.75rem',
                border: '1px solid #e2e8f0',
                borderRadius: '0.375rem',
              }}
            />
            <button
              type="submit"
              className="btn btn-secondary"
              disabled={loading}
              style={{ width: '100%' }}
            >
              {loading ? 'Logging in...' : 'Dev Login'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}

export default LoginPage
