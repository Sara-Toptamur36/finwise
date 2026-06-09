import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user,        setUser]        = useState(null)
  const [token,       setToken]       = useState(() => localStorage.getItem('banka_token'))
  const [isDemo,      setIsDemo]      = useState(false)
  const [demoPersona, setDemoPersona] = useState('ahmet')  // ahmet | ayse | zeynep
  const [loading,     setLoading]     = useState(true)
  const [result,      setResult]      = useState(null)     // mevcut analiz sonucu

  // Token degisince axios header'i guncelle
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      localStorage.setItem('banka_token', token)
    } else {
      delete axios.defaults.headers.common['Authorization']
      localStorage.removeItem('banka_token')
    }
  }, [token])

  // Sayfa yenilendiginde kullaniciyi geri yukle
  useEffect(() => {
    if (token) {
      axios.get('/api/auth/me')
        .then(r => setUser(r.data))
        .catch(() => { setToken(null); setUser(null) })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email, password) => {
    const { data } = await axios.post('/api/auth/login', { email, password })
    setToken(data.token)
    setUser({ name: data.name, email: data.email })
    setIsDemo(false)
  }

  const register = async (name, email, password, kvkk, terms) => {
    const { data } = await axios.post('/api/auth/register', { name, email, password, kvkk, terms })
    setToken(data.token)
    setUser({ name: data.name, email: data.email })
    setIsDemo(false)
  }

  const enterDemo = (personaId = 'ahmet') => {
    setIsDemo(true)
    setDemoPersona(personaId)
    setUser(null)
    setToken(null)
    setResult(null)
  }

  const logout = async () => {
    try { await axios.post('/api/auth/logout') } catch {}
    setToken(null)
    setUser(null)
    setIsDemo(false)
    setResult(null)
  }

  const isAuthenticated = !!user || isDemo

  return (
    <AuthContext.Provider value={{
      user, token, isDemo, demoPersona, loading, result,
      setResult, setDemoPersona,
      login, register, logout, enterDemo, isAuthenticated,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
