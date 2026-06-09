import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { LogoIcon, LogoText } from '../components/Logo'
import PasswordInput from '../components/PasswordInput'

function ResetModal({ onClose }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm">
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <h2 className="font-bold text-gray-900 text-sm">Şifremi Unuttum</h2>
          <button onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition text-lg leading-none">
            ×
          </button>
        </div>

        <div className="p-5 space-y-4">
          {/* Güvenlik açıklaması */}
          <div className="flex gap-3 p-3 bg-amber-50 border border-amber-200 rounded-xl">
            <span className="text-xl leading-none mt-0.5">🔒</span>
            <div>
              <p className="text-xs font-semibold text-amber-800 mb-1">E-posta Doğrulaması Gerekli</p>
              <p className="text-xs text-amber-700 leading-relaxed">
                Güvenliğiniz için şifre sıfırlama işlemi yalnızca e-posta doğrulamasıyla yapılabilir.
                Bu uygulama şu an e-posta gönderimi desteklemediğinden otomatik sıfırlama devre dışıdır.
              </p>
            </div>
          </div>

          {/* Yönlendirme seçenekleri */}
          <div className="space-y-2">
            <p className="text-xs font-semibold text-gray-600">Ne yapabilirsiniz?</p>

            <div className="flex gap-2.5 p-3 bg-green-50 border border-green-100 rounded-lg">
              <span className="text-base leading-none mt-0.5">✅</span>
              <p className="text-xs text-gray-700">
                <strong>Şifrenizi hatırlıyorsanız</strong> — giriş yapıp{' '}
                <span className="text-brand font-medium">Ayarlar → Şifre Değiştir</span> bölümünden
                güvenli şekilde değiştirebilirsiniz.
              </p>
            </div>

            <div className="flex gap-2.5 p-3 bg-gray-50 border border-gray-100 rounded-lg">
              <span className="text-base leading-none mt-0.5">ℹ️</span>
              <p className="text-xs text-gray-700">
                <strong>Şifrenizi tamamen unuttunuza</strong> — uygulama yöneticisiyle iletişime
                geçin veya yeni bir hesap oluşturun.
              </p>
            </div>
          </div>

          <button onClick={onClose} className="btn-primary w-full text-sm">
            Anladım, Geri Dön
          </button>
        </div>
      </div>
    </div>
  )
}

export default function LoginPage() {
  const { login, enterDemo } = useAuth()
  const navigate = useNavigate()
  const [email,      setEmail]      = useState('')
  const [password,   setPassword]   = useState('')
  const [error,      setError]      = useState('')
  const [loading,    setLoading]    = useState(false)
  const [showReset,  setShowReset]  = useState(false)

  const handleSubmit = async e => {
    e.preventDefault()
    setError(''); setLoading(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (e) {
      setError(e.response?.data?.detail || 'Giriş başarısız. Lütfen tekrar deneyin.')
    } finally {
      setLoading(false)
    }
  }

  const handleDemo = () => { enterDemo('ahmet'); navigate('/dashboard') }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      {showReset && <ResetModal onClose={() => setShowReset(false)} />}

      <div className="w-full max-w-sm">

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-3">
            <LogoIcon size={48} />
          </div>
          <LogoText className="text-2xl font-black tracking-tight" />
          <p className="text-sm text-gray-400 mt-1">Hesabınıza giriş yapın veya demo inceleyin.</p>
        </div>

        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1.5">E-posta</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)}
                className="input-field" placeholder="ornek@mail.com" required />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1.5">Şifre</label>
              <PasswordInput value={password} onChange={e => setPassword(e.target.value)} required autoComplete="current-password" />
              <div className="text-right mt-1">
                <button type="button" onClick={() => setShowReset(true)}
                  className="text-xs text-brand hover:underline cursor-pointer font-medium">
                  Şifremi Unuttum
                </button>
              </div>
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-600">
                ⚠️ {error}
              </div>
            )}

            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? 'Giriş yapılıyor...' : 'Giriş Yap'}
            </button>
          </form>

          <div className="my-4 flex items-center gap-3">
            <div className="flex-1 h-px bg-gray-200" />
            <span className="text-xs text-gray-400">veya</span>
            <div className="flex-1 h-px bg-gray-200" />
          </div>

          <button onClick={handleDemo} className="btn-secondary w-full text-sm">
            🎭 Demo İncele
          </button>

          <p className="text-center text-xs text-gray-400 mt-4">
            Hesabın yok mu?{' '}
            <Link to="/register" className="text-brand font-semibold hover:underline">Kayıt Ol</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
