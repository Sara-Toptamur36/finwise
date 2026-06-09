import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { LogoIcon, LogoText } from './Logo'

const NAV = [
  { to: '/dashboard', label: 'Ana Panel',         icon: '🏠' },
  { to: '/analyze',   label: 'Analiz Et',          icon: '🔍' },
  { to: '/scenario',  label: 'Senaryo Testi',      icon: '🔮' },
  { to: '/reports',   label: 'Raporlarım',         icon: '📄' },
  { to: '/guide',     label: 'Kullanım Kılavuzu',  icon: '📖' },
  { to: '/settings',  label: 'Ayarlar',            icon: '⚙️'  },
]

const PERSONAS = [
  { id: 'ahmet',  label: 'Ahmet Bey'    },
  { id: 'ayse',   label: 'Ayşe Hanım'  },
  { id: 'zeynep', label: 'Zeynep Hanım' },
]

export default function Sidebar() {
  const { logout, isDemo, demoPersona, setDemoPersona } = useAuth()
  const navigate = useNavigate()

  return (
    <aside className="w-56 bg-brand-900 text-white flex flex-col shrink-0">

      {/* Logo */}
      <div className="px-5 py-4 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <LogoIcon size={32} />
          <div className="leading-tight">
            <LogoText dark className="text-base font-black tracking-tight block" />
            <span className="text-xs text-white/40 font-normal">Finans Asistanı</span>
          </div>
        </div>

        {isDemo && (
          <div className="mt-2 px-2 py-1 bg-amber-400/20 border border-amber-400/30 rounded text-xs text-amber-300">
            🎭 Demo Modu
          </div>
        )}
      </div>

      {/* Demo persona seçici */}
      {isDemo && (
        <div className="px-4 py-3 border-b border-white/10 bg-white/5">
          <p className="text-xs text-white/50 mb-1.5">Demo Profili</p>
          <select
            value={demoPersona}
            onChange={e => { setDemoPersona(e.target.value); navigate('/dashboard') }}
            className="w-full bg-white/10 border border-white/20 rounded-lg px-2 py-1.5 text-xs text-white focus:outline-none focus:ring-1 focus:ring-green-400"
          >
            {PERSONAS.map(p => (
              <option key={p.id} value={p.id} className="text-gray-900 bg-white">{p.label}</option>
            ))}
          </select>
        </div>
      )}

      {/* Navigasyon */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {NAV.map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-green-500/25 text-white font-semibold'
                  : 'text-white/65 hover:bg-white/10 hover:text-white'
              }`
            }
          >
            <span className="text-base">{icon}</span>
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Çıkış */}
      <div className="px-3 py-4 border-t border-white/10">
        <button
          onClick={logout}
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-white/50 hover:bg-white/10 hover:text-white transition-colors"
        >
          <span>🚪</span>
          <span>Çıkış Yap</span>
        </button>
      </div>
    </aside>
  )
}
