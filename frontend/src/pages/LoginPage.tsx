import React from 'react'

const LoginPage: React.FC = () => {
  const handleLogin = () => {
    // Redirect to SAML login endpoint
    window.location.href = '/api/v1/auth/saml/login'
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>🤖 Deep Thought</h1>
        <p className="tagline">
          The Answer to Life, the Universe, and Enterprise Sales Deals
        </p>
        <button className="btn btn-primary" onClick={handleLogin}>
          Sign in with SAML
        </button>
      </div>
    </div>
  )
}

export default LoginPage
