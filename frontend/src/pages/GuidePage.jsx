import { useState, useMemo } from 'react'

// ── Veri tanımları ───────────────────────────────────────────────

const QUICK_STEPS = [
  { icon: '👤', title: 'Giriş yapın veya demo seçin',       desc: 'Hesabınızla giriş yapın ya da hazır demo profillerinden birini seçin.' },
  { icon: '📤', title: 'Ekstrenizi yükleyin',               desc: 'CSV veya Excel formatındaki banka ekstrenizi sürükleyip bırakın.' },
  { icon: '🏷️', title: 'İşlemler kategorize edilsin',       desc: 'FinWise, işlemlerinizi otomatik olarak 13 kategoriye ayırır.' },
  { icon: '📊', title: 'Profil ve teşhisi inceleyin',       desc: 'Harcama profilinizi ve AI finansal teşhisinizi görüntüleyin.' },
  { icon: '💡', title: 'Kararın nedenini okuyun',           desc: 'Modelin neden bu teşhisi verdiğini açıklanabilir şekilde görün.' },
  { icon: '📥', title: 'Rapor alın veya senaryo test edin', desc: 'PDF/Excel raporu indirin ya da "gelir artsaydı ne olurdu?" gibi sorular sorun.' },
]

const PIPELINE_ROWS = [
  {
    step: '1',
    user: 'İşlemler anlaşılır hale gelir',
    detail: 'Ham banka açıklamaları temizlenir ve 13 kategoriden birine atanır.',
    tech: 'NLP + Regex + SVC',
    color: 'bg-green-500',
  },
  {
    step: '2',
    user: 'Harcama davranışın çıkarılır',
    detail: 'Gelir-gider ritmi ve kategori alışkanlıkların analiz edilir.',
    tech: 'K-Means Kümeleme',
    color: 'bg-teal-500',
  },
  {
    step: '3',
    user: 'Gelecek ay eğilimi tahmin edilir',
    detail: 'Harcamanın artıp artmayacağı verilere dayalı olarak öngörülür.',
    tech: 'LightGBM Regresyon',
    color: 'bg-amber-500',
  },
  {
    step: '4',
    user: 'AI finansal teşhis oluşur',
    detail: 'Riskli / Bütçeleme Yapmalı / Tasarrufçu sınıflarından biri üretilir.',
    tech: 'XGBoost Sınıflandırma',
    color: 'bg-red-500',
  },
  {
    step: '5',
    user: 'Karar açıklanır',
    detail: 'Modelin neden böyle düşündüğü hangi faktörlerin etkili olduğuyla birlikte gösterilir.',
    tech: 'SHAP Açıklanabilirlik',
    color: 'bg-purple-500',
  },
]

const FILE_FIELDS = [
  { field: 'tarih',     label: 'Tarih',     desc: 'İşlemin gerçekleştiği tarih',    example: '2026-06-12',   required: true  },
  { field: 'tutar',     label: 'Tutar',     desc: 'İşlem tutarı (negatif = gider)', example: '-245.90',       required: true  },
  { field: 'aciklama',  label: 'Açıklama',  desc: 'Bankadaki ham işlem açıklaması', example: 'POS A101 MARKET', required: true },
]

const TERMS = [
  { icon: '🤖', term: 'AI Finansal Teşhis',   def: 'Harcama davranışınıza göre modelin verdiği genel finansal durum sınıfıdır. Riskli, Bütçeleme Yapmalı veya Tasarrufçu olarak belirlenir.' },
  { icon: '🎯', term: 'Kategori Güveni',       def: 'Bir işlemin doğru kategoriye atanma konusunda modelin ne kadar emin olduğunu gösterir. Düşük güven → Güvenli Bekletme sınıfına alınır.' },
  { icon: '🔒', term: 'Güvenli Bekletme',      def: 'Model emin değilse yanlış karar vermek yerine işlemi ayrı bir sınıfta bekletir. Bu işlemler kullanıcı tarafından incelenebilir.' },
  { icon: '👤', term: 'Harcama Profili',        def: 'Gelir-gider dengeniz, harcama ritminiz ve baskın kategorilerinizin özetidir. K-Means algoritmasıyla oluşturulur.' },
  { icon: '🔮', term: 'Senaryo Güveni',         def: 'Denediğiniz simülasyonun gerçekçi bir aralıkta olup olmadığını gösterir. Çok uç senaryolarda güven düşer.' },
  { icon: '🎭', term: 'Demo Modu',              def: 'Sentetik ve anonim örnek profillerle sistemi risksiz deneme alanıdır. Gerçek veri yüklenmez.' },
  { icon: '📊', term: 'SHAP Açıklaması',        def: 'Model kararına en çok etki eden faktörleri gösteren açıklama yöntemidir. Nedensellik değil, katkı analizini yansıtır.' },
  { icon: '🏷️', term: 'Finansal Segment',       def: 'Benzer harcama davranışına sahip kullanıcıların yer aldığı davranış grubudur. 4 farklı küme mevcuttur.' },
]

const FAQS = [
  {
    q: 'Hangi dosya formatları destekleniyor?',
    a: 'CSV (.csv), Excel (.xlsx, .xls) formatları desteklenmektedir. Dosyanızda en az tarih, tutar ve açıklama sütunlarının bulunması gerekir.',
  },
  {
    q: 'Verilerim güvende mi?',
    a: 'Yüklenen dosyalar yalnızca aktif analiz oturumu süresince bellekte tutulur. Sunucu kapatıldığında veya oturum sonlandırıldığında kalıcı olarak silinir. Verileriniz üçüncü taraflarla paylaşılmaz.',
  },
  {
    q: 'Güvenli Bekletme sınıfındaki işlemler ne anlama gelir?',
    a: 'Model bu işlemleri yeterli güvenle sınıflandıramadığında, yanlış kategori vermek yerine bekletmeyi tercih eder. Bu işlemleri kendiniz gözden geçirmeniz önerilir.',
  },
  {
    q: 'Demo modu ile gerçek analiz arasındaki fark nedir?',
    a: 'Demo modunda sentetik ve anonim verilerle sistem denenir; gerçek dosya yüklenemez. Kendi verilerinizi analiz etmek için hesap oluşturup giriş yapmanız gerekir.',
  },
  {
    q: 'Senaryo testi ne işe yarar?',
    a: '"Gelirim %20 artarsa ne olur?" veya "Market harcamalarımı kessem teşhis değişir mi?" gibi soruları simüle etmenizi sağlar. Gerçek finansal bir taahhüt değildir.',
  },
  {
    q: 'Sonuçlar kesin finansal tavsiye midir?',
    a: 'Hayır. FinWise bir karar destek sistemidir. Üretilen analizler, tahminler ve öneriler yalnızca bilgilendirme amaçlıdır. Finansal kararlarınız için yetkili bir danışmana başvurun.',
  },
]

// ── Arama fonksiyonu ─────────────────────────────────────────────
function highlight(text, query) {
  if (!query) return text
  const idx = text.toLowerCase().indexOf(query.toLowerCase())
  if (idx === -1) return text
  return (
    <>
      {text.slice(0, idx)}
      <mark className="bg-yellow-200 text-yellow-900 rounded px-0.5">{text.slice(idx, idx + query.length)}</mark>
      {text.slice(idx + query.length)}
    </>
  )
}

// ── Bölüm başlığı ────────────────────────────────────────────────
function SectionTitle({ number, title, desc }) {
  return (
    <div className="flex items-start gap-4 mb-6">
      <div className="w-9 h-9 rounded-xl bg-brand text-white font-bold text-sm flex items-center justify-center flex-shrink-0 mt-0.5">
        {number}
      </div>
      <div>
        <h2 className="text-xl font-bold text-gray-900">{title}</h2>
        {desc && <p className="text-sm text-gray-500 mt-0.5">{desc}</p>}
      </div>
    </div>
  )
}

// ── SSS satırı ──────────────────────────────────────────────────
function FaqRow({ q, a, query }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-gray-50 transition-colors"
      >
        <span className="font-medium text-gray-800 text-sm">{highlight(q, query)}</span>
        <span className={`text-gray-400 text-lg ml-4 transition-transform flex-shrink-0 ${open ? 'rotate-45' : ''}`}>+</span>
      </button>
      {open && (
        <div className="px-5 pb-4 text-sm text-gray-600 leading-relaxed border-t border-gray-100 pt-3">
          {highlight(a, query)}
        </div>
      )}
    </div>
  )
}

// ── Ana sayfa ────────────────────────────────────────────────────
export default function GuidePage() {
  const [query, setQuery] = useState('')

  const visibleTerms = useMemo(() =>
    !query ? TERMS : TERMS.filter(t =>
      t.term.toLowerCase().includes(query.toLowerCase()) ||
      t.def.toLowerCase().includes(query.toLowerCase())
    ), [query])

  const visibleFaqs = useMemo(() =>
    !query ? FAQS : FAQS.filter(f =>
      f.q.toLowerCase().includes(query.toLowerCase()) ||
      f.a.toLowerCase().includes(query.toLowerCase())
    ), [query])

  return (
    <div className="max-w-3xl mx-auto space-y-10 py-4">

      {/* Başlık */}
      <div>
        <h1 className="text-2xl font-bold text-brand">Kullanım Kılavuzu</h1>
        <p className="text-gray-500 mt-1 text-sm">FinWise'yı 2 dakikada anlayın. Ne yükleyeceğinizi öğrenin, sonuçları doğru yorumlayın.</p>
      </div>

      {/* Arama */}
      <div className="relative">
        <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 text-base">🔍</span>
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder='Kılavuzda ara: "Güvenli Bekletme", "SHAP", "Demo Modu"...'
          className="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-xl text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent bg-white shadow-sm"
        />
        {query && (
          <button onClick={() => setQuery('')} className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-lg leading-none">×</button>
        )}
      </div>

      {/* ── 1. Hızlı Başlangıç ─────────────────────────────────── */}
      {!query && (
        <section>
          <SectionTitle number="1" title="Hızlı Başlangıç" desc="3 dakikada ilk analizinizi tamamlayın." />
          <div className="relative">
            {/* Timeline çizgisi */}
            <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-gray-200 z-0" />
            <div className="space-y-4 relative z-10">
              {QUICK_STEPS.map((s, i) => (
                <div key={i} className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-full bg-brand text-white flex items-center justify-center text-base font-bold flex-shrink-0 shadow-sm ring-4 ring-white">
                    {i + 1}
                  </div>
                  <div className="card flex-1 py-3 px-4 flex items-start gap-3">
                    <span className="text-xl flex-shrink-0">{s.icon}</span>
                    <div>
                      <p className="font-semibold text-gray-800 text-sm">{s.title}</p>
                      <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">{s.desc}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* ── 2. Sistem Nasıl Çalışır? ───────────────────────────── */}
      {!query && (
        <section>
          <SectionTitle number="2" title="Sistem Nasıl Çalışır?" desc="Her adımda size ne olduğunu ve arka planda hangi teknolojinin çalıştığını görün." />
          <div className="card overflow-hidden p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 border-b border-gray-200">
                    <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 w-6">#</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500">Size ne olur?</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden md:table-cell">Açıklama</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500">Teknik Karşılığı</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {PIPELINE_ROWS.map(r => (
                    <tr key={r.step} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div className={`w-6 h-6 rounded-full ${r.color} text-white text-xs font-bold flex items-center justify-center`}>{r.step}</div>
                      </td>
                      <td className="px-4 py-3 font-medium text-gray-800">{r.user}</td>
                      <td className="px-4 py-3 text-gray-500 text-xs leading-relaxed hidden md:table-cell">{r.detail}</td>
                      <td className="px-4 py-3">
                        <span className="inline-flex items-center px-2 py-1 rounded-md bg-gray-100 text-gray-600 text-xs font-mono">{r.tech}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
              <p className="text-xs text-gray-400 italic">Performans değerleri model değerlendirme ekranında gösterilir.</p>
            </div>
          </div>
        </section>
      )}

      {/* ── 3. Dosya Yükleme ───────────────────────────────────── */}
      {!query && (
        <section>
          <SectionTitle number="3" title="Hangi Dosyaları Yükleyebilirim?" desc="CSV veya Excel formatındaki banka ekstrenizi yükleyebilirsiniz." />
          <div className="space-y-4">
            <div className="card">
              <p className="text-sm text-gray-600 leading-relaxed mb-4">
                Sistemin analiz yapabilmesi için dosyanızda en az <strong>üç temel alan</strong> bulunmalıdır.
                Sütun adları tam eşleşmese de sistem otomatik olarak tespit etmeye çalışır.
              </p>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="text-left px-4 py-2 text-xs font-semibold text-gray-500">Alan</th>
                      <th className="text-left px-4 py-2 text-xs font-semibold text-gray-500">Açıklama</th>
                      <th className="text-left px-4 py-2 text-xs font-semibold text-gray-500">Örnek Değer</th>
                      <th className="text-left px-4 py-2 text-xs font-semibold text-gray-500">Durum</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {FILE_FIELDS.map(f => (
                      <tr key={f.field} className="hover:bg-gray-50">
                        <td className="px-4 py-3 font-mono text-brand text-xs font-semibold">{f.field}</td>
                        <td className="px-4 py-3 text-gray-600">{f.desc}</td>
                        <td className="px-4 py-3 font-mono text-gray-500 text-xs">{f.example}</td>
                        <td className="px-4 py-3">
                          <span className="badge-safe text-xs">Zorunlu</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="flex items-start gap-3 p-4 bg-green-50 rounded-xl border border-green-200">
                <span className="text-green-500 text-lg mt-0.5">✅</span>
                <div>
                  <p className="font-semibold text-green-800 text-sm mb-1">Desteklenen Formatlar</p>
                  <p className="text-xs text-green-700">.csv, .xlsx, .xls</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-4 bg-red-50 rounded-xl border border-red-200">
                <span className="text-red-400 text-lg mt-0.5">⛔</span>
                <div>
                  <p className="font-semibold text-red-800 text-sm mb-1">Desteklenmeyen</p>
                  <p className="text-xs text-red-700">PDF ekstre, görüntü dosyası, şifreli Excel</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ── 4. Sonuçlar Ne Anlama Geliyor? ─────────────────────── */}
      <section>
        <SectionTitle number="4" title="Sonuçlar Ne Anlama Geliyor?"
          desc={query ? `"${query}" ile eşleşen terimler` : 'Ekrandaki terimlerin ne anlama geldiğini öğrenin.'} />

        {visibleTerms.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {visibleTerms.map(t => (
              <div key={t.term} className="card flex items-start gap-3 py-4">
                <span className="text-2xl flex-shrink-0">{t.icon}</span>
                <div>
                  <p className="font-semibold text-brand text-sm mb-1">{highlight(t.term, query)}</p>
                  <p className="text-xs text-gray-500 leading-relaxed">{highlight(t.def, query)}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-400 text-sm">"{query}" için terim bulunamadı.</div>
        )}
      </section>

      {/* ── 5. Güvenlik, Sınırlar ve Sık Sorular ──────────────── */}
      <section>
        <SectionTitle number="5" title="Güvenlik, Sınırlar ve Sık Sorular" />

        {/* Model uyarısı */}
        <div className="card border-amber-200 bg-amber-50 mb-4">
          <div className="flex items-start gap-3">
            <span className="text-2xl">⚠️</span>
            <div>
              <h3 className="font-bold text-amber-900 mb-2">Model Yanılabilir Mi?</h3>
              <p className="text-sm text-amber-800 leading-relaxed mb-3">
                Evet. FinWise bir karar destek sistemidir; sonuçları kesin finansal tavsiye olarak değerlendirilmemelidir.
                Model, düşük güvenli işlemleri yanlış sınıflandırmak yerine <strong>Güvenli Bekletme</strong> sınıfına alır.
                Bu nedenle özellikle düşük güvenli işlemler, yüksek riskli teşhisler ve sıra dışı senaryolar
                kullanıcı tarafından ayrıca kontrol edilmelidir.
              </p>
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-amber-100 border border-amber-300 rounded-lg">
                <span className="text-amber-700 text-sm font-semibold">💬 FinWise karar vermez; karar vermenize yardımcı olur.</span>
              </div>
            </div>
          </div>
        </div>

        {/* SSS */}
        <div className="space-y-2">
          {visibleFaqs.length > 0 ? (
            visibleFaqs.map((f, i) => <FaqRow key={i} q={f.q} a={f.a} query={query} />)
          ) : (
            <div className="text-center py-8 text-gray-400 text-sm">"{query}" için soru bulunamadı.</div>
          )}
        </div>
      </section>

    </div>
  )
}
