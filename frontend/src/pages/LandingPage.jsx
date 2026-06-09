import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { LogoIcon, LogoText } from '../components/Logo'

const FEATURES = [
  { icon: '🏷️', title: 'Otomatik Kategorizasyon',   desc: 'Ham banka açıklamalarını 13 harcama kategorisine ayırır.' },
  { icon: '👤', title: 'Harcama Profili',            desc: 'Finansal davranışını kişisel profil olarak sunar.' },
  { icon: '📈', title: 'Gelecek Ay Tahmini',         desc: 'Geçmiş veriye göre harcama eğilimini tahmin eder.' },
  { icon: '🤖', title: 'AI Finansal Teşhis',         desc: 'Bütçeleme, risk ve tasarruf durumunu sınıflandırır.' },
  { icon: '💡', title: 'Açıklanabilir Karar',        desc: 'Modelin neden bu sonucu verdiğini sade dille açıklar.' },
  { icon: '🔮', title: 'Senaryo Testi',              desc: 'Gelir/gider değişirse ne olacağını simüle eder.' },
]

const STEPS = [
  { label: 'Ekstre Yükle',          color: 'bg-gray-100 text-gray-700' },
  { label: 'Kategorizasyon',         color: 'bg-green-100 text-green-700' },
  { label: 'Profil Çıkar',           color: 'bg-green-100 text-green-700' },
  { label: 'Gelecek Ay Tahmini',     color: 'bg-amber-100 text-amber-700' },
  { label: 'AI Teşhis',              color: 'bg-red-100 text-red-700' },
  { label: 'Rapor',                  color: 'bg-green-200 text-green-800' },
]

export default function LandingPage() {
  const navigate = useNavigate()
  const { enterDemo } = useAuth()

  const handleDemo = () => { enterDemo('ahmet'); navigate('/dashboard') }

  return (
    <div className="min-h-screen bg-white">

      {/* Navbar */}
      <nav className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between border-b border-gray-100">
        <div className="flex items-center gap-2.5">
          <LogoIcon size={32} />
          <LogoText className="text-lg font-black tracking-tight" />
        </div>
        <div className="flex gap-2">
          <button onClick={() => navigate('/login')}    className="btn-ghost text-sm">Giriş Yap</button>
          <button onClick={() => navigate('/register')} className="btn-primary text-sm">Kayıt Ol</button>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-3xl mx-auto px-6 py-20 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold mb-6 border border-green-200">
          ✦ Açıklanabilir yapay zekâ destekli kişisel finans asistanı
        </div>
        <h1 className="text-4xl font-bold text-gray-900 leading-snug mb-4">
          FinWise ile finansal verinizi anlayın,<br/>
          <span className="text-brand">bütçenizi yönetin.</span>
        </h1>
        <p className="text-lg text-brand font-semibold mb-3 tracking-wide">
          Harcamalarını anla, geleceğini planla.
        </p>
        <p className="text-base text-gray-500 max-w-xl mx-auto mb-10 leading-relaxed">
          FinWise, banka ekstrelerinizi yapay zeka ile analiz ederek harcama kategorilerinizi,
          profilinizi ve finansal karar önerilerini açıklanabilir şekilde sunar.
        </p>
        <div className="flex justify-center gap-3">
          <button onClick={() => navigate('/register')} className="btn-primary px-8 py-3">
            Başla — Ücretsiz
          </button>
          <button onClick={handleDemo} className="btn-secondary px-8 py-3">
            🎭 Demo İncele
          </button>
        </div>
        <p className="mt-3 text-xs text-gray-400">Kredi kartı veya kurulum gerekmez</p>
      </section>

      {/* Pipeline akışı */}
      <section className="max-w-4xl mx-auto px-6 mb-16">
        <div className="bg-gray-50 rounded-2xl p-7 border border-gray-200">
          <h2 className="text-center text-brand-900 font-bold text-base mb-6">Nasıl Çalışır?</h2>
          <div className="flex flex-wrap justify-center items-center gap-2 text-xs">
            {STEPS.map((s, i) => (
              <div key={s.label} className="flex items-center gap-2">
                <span className={`px-3 py-1.5 rounded-lg font-semibold ${s.color}`}>{s.label}</span>
                {i < STEPS.length - 1 && <span className="text-gray-300">→</span>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Özellikler */}
      <section className="max-w-5xl mx-auto px-6 pb-20">
        <h2 className="text-center text-2xl font-bold text-gray-900 mb-8">Özellikler</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {FEATURES.map(f => (
            <div key={f.title} className="card hover:border-brand-200 transition-colors">
              <div className="text-2xl mb-2">{f.icon}</div>
              <h3 className="font-semibold text-gray-900 mb-1 text-sm">{f.title}</h3>
              <p className="text-xs text-gray-500 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="bg-brand-900 text-white py-14 text-center">
        <div className="flex justify-center mb-4">
          <LogoIcon size={44} />
        </div>
        <h2 className="text-2xl font-bold mb-2">Finansal sağlığınızı anlamaya hazır mısınız?</h2>
        <p className="text-white/60 text-sm mb-7">
          Harcamalarını anla, geleceğini planla.
        </p>
        <div className="flex justify-center gap-3">
          <button onClick={() => navigate('/register')} className="bg-green-400 text-brand-900 px-7 py-2.5 rounded-lg font-bold hover:bg-green-300 transition text-sm">
            Kayıt Ol
          </button>
          <button onClick={handleDemo} className="bg-white/10 border border-white/25 text-white px-7 py-2.5 rounded-lg font-semibold hover:bg-white/20 transition text-sm">
            Demo İncele
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 py-5 text-center text-xs text-gray-400">
        FinWise © 2026 · Prototip sürüm · Kesin finansal tavsiye sunmaz.
      </footer>
    </div>
  )
}
