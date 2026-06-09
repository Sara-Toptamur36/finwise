import { useAuth } from '../context/AuthContext'

const PERSONA_LABELS = {
  ahmet:  'Ahmet Bey — Yüksek Bütçe Riski',
  ayse:   'Ayşe Hanım — Tasarrufçu Profil',
  zeynep: 'Zeynep Hanım — Bütçeleme Yapmalı',
}

export default function Header() {
  const { user, isDemo, demoPersona } = useAuth()

  return (
    <header className="h-13 bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        {isDemo ? (
          <span className="badge-demo">🎭 Demo Modu</span>
        ) : (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-700 border border-green-200">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
            Kişisel Analiz
          </span>
        )}
        {isDemo && (
          <span className="text-xs text-gray-400">
            {PERSONA_LABELS[demoPersona] || demoPersona}
          </span>
        )}
      </div>

      <div className="flex items-center gap-3">
        {user && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-brand text-white flex items-center justify-center text-sm font-semibold">
              {user.name?.charAt(0)?.toUpperCase()}
            </div>
            <span className="text-sm text-gray-700 font-medium">{user.name}</span>
          </div>
        )}
      </div>
    </header>
  )
}
