import React, { useEffect } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import { AuthProvider } from './hooks/useAuth'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import ProxyList from './pages/ProxyList'
import CredentialsManager from './pages/CredentialsManager'
import FetchJobs from './pages/FetchJobs'
import Settings from './pages/Settings'

function App() {
  const navigate = useNavigate()

  useEffect(() => {
    const handleLogout = () => navigate('/login')
    window.addEventListener('auth:logout', handleLogout)
    return () => window.removeEventListener('auth:logout', handleLogout)
  }, [navigate])

  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/*" element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/proxies" element={<ProxyList />} />
                <Route path="/credentials" element={<CredentialsManager />} />
                <Route path="/jobs" element={<FetchJobs />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        } />
      </Routes>
    </AuthProvider>
  )
}

export default App