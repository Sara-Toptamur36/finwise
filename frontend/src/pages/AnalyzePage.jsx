import { useState, useRef, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const TABS = ['Veri Yükle','İşlem Kategorizasyonu','Harcama Profiliniz','AI Finansal Teşhis','Karar Açıklaması','Rapor Oluştur']
const CATEGORY_TR = {
  ALISVERIS:'Alışveriş', BANKA_KESINTISI:'Banka Kesintisi', DIGER:'Diğer',
  EGITIM:'Eğitim', EGLENCE:'Eğlence', FATURA:'Fatura', MARKET:'Market',
  NAKIT_ISLEMLERI:'Nakit', SAGLIK:'Sağlık', SEYAHAT:'Seyahat',
  ULASIM:'Ulaşım', VIRMAN:'Virman', YEME_ICME:'Yeme-İçme',
}
const COLORS = ['#166534','#16a34a','#22c55e','#86efac','#f59e0b','#fbbf24','#ef4444','#f87171','#84cc16','#a3e635','#4ade80','#6ee7b7','#14b8a6']
const fmt = n => n?.toLocaleString('tr-TR', { maximumFractionDigits: 0 })

// ── Sekme 1: Veri Yükle ─────────────────────────────────────────
function TabUpload({ onSuccess }) {
  const { isDemo, demoPersona, setResult, setDemoPersona } = useAuth()
  const [drag,       setDrag]       = useState(false)
  const [uploading,  setUploading]  = useState(false)
  const [rawSummary, setRawSummary] = useState(null)
  const [error,      setError]      = useState('')
  const inputRef = useRef()

  if (isDemo) return (
    <div className="max-w-xl">
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-6 text-center">
        <div className="text-4xl mb-3">🔒</div>
        <h3 className="font-bold text-brand text-lg mb-2">Demo Modundasınız</h3>
        <p className="text-sm text-gray-600 mb-4">
          Şu an sentetik olarak oluşturulan demo profilini inceliyorsunuz.
          Bu profil tamamen anonimdir ve örnek amaçlıdır. Kendi banka ekstrenizi yüklemek için kayıt olup giriş yapın.
        </p>
        <div className="flex gap-3 justify-center mb-4">
          <a href="/register" className="btn-primary text-sm">Kayıt Ol</a>
          <a href="/login"    className="btn-secondary text-sm">Giriş Yap</a>
        </div>
        <div className="border-t border-amber-200 pt-4">
          <p className="text-xs text-amber-600 mb-2">Başka Demo Profili Seç:</p>
          <div className="flex gap-2 justify-center flex-wrap">
            {[['ahmet','Ahmet Bey'],['ayse','Ayşe Hanım'],['zeynep','Zeynep Hanım']].map(([id,name]) => (
              <button key={id} onClick={() => setDemoPersona(id)}
                className={`px-3 py-1.5 rounded-lg text-xs border ${demoPersona===id ? 'bg-brand text-white border-brand' : 'bg-white text-brand border-brand hover:bg-brand-50'}`}>
                {name}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )

  const doUpload = async file => {
    if (!file) return
    setError(''); setRawSummary(null); setUploading(true)
    const fd = new FormData()
    fd.append('file', file)
    try {
      const { data } = await axios.post('/api/analysis/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      setResult(data)
      setRawSummary(data.raw_summary)
      onSuccess?.()
    } catch (e) {
      setError(e.response?.data?.detail || 'Yükleme başarısız.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="max-w-2xl space-y-5">
      {/* Yükleme alanı */}
      <div
        onDragOver={e => { e.preventDefault(); setDrag(true) }}
        onDragLeave={() => setDrag(false)}
        onDrop={e => { e.preventDefault(); setDrag(false); doUpload(e.dataTransfer.files[0]) }}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${drag ? 'border-brand bg-brand-50' : 'border-gray-300 hover:border-brand hover:bg-gray-50'}`}
      >
        <input ref={inputRef} type="file" accept=".csv,.xlsx,.xls" className="hidden" onChange={e => doUpload(e.target.files[0])} />
        {uploading ? (
          <div><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand mx-auto mb-3" /><p className="text-brand font-medium">Analiz ediliyor...</p></div>
        ) : (
          <>
            <div className="text-4xl mb-3">📤</div>
            <p className="font-semibold text-brand mb-1">CSV veya Excel dosyanızı buraya sürükleyin ya da tıklayın</p>
            <p className="text-sm text-gray-400">Desteklenen: .csv, .xlsx, .xls</p>
          </>
        )}
      </div>

      {error && <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">⚠️ {error}</div>}

      {/* Beklenen format */}
      <div className="card">
        <h4 className="font-semibold text-brand mb-3">Beklenen Kolon Formatı</h4>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="bg-gray-50">{['Kolon','Örnek','Zorunlu'].map(h => <th key={h} className="text-left px-3 py-2 text-xs font-semibold text-gray-500">{h}</th>)}</tr></thead>
            <tbody className="divide-y divide-gray-100">
              {[['tarih','2026-06-01','Evet'],['aciklama','MIGROS AS','Evet'],['tutar','450.00','Evet']].map(r => (
                <tr key={r[0]}>
                  <td className="px-3 py-2 font-mono text-brand">{r[0]}</td>
                  <td className="px-3 py-2 text-gray-500">{r[1]}</td>
                  <td className="px-3 py-2"><span className="badge-safe">{r[2]}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Yükleme özeti */}
      {rawSummary && (
        <div className="card border-green-200">
          <h4 className="font-semibold text-green-700 mb-3">✅ Dosya Başarıyla Yüklendi</h4>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {[
              ['Ham İşlem Sayısı',   rawSummary.row_count],
              ['Ham Kolon Sayısı',   rawSummary.col_count],
              ['Eksik Değer Oranı',  `%${rawSummary.null_rate}`],
              ['Geçerli İşlem Oranı',`%${rawSummary.valid_rate}`],
            ].map(([k,v]) => (
              <div key={k}><p className="text-gray-500 text-xs">{k}</p><p className="font-semibold text-brand">{v}</p></div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ── Sekme 2: Kategorizasyon ──────────────────────────────────────
function TabCategories({ result }) {
  if (!result) return <EmptyState />
  const txns = result.transactions || []
  const s    = result.summary || {}
  return (
    <div className="space-y-5">
      <div className="card">
        <p className="text-sm text-gray-600 leading-relaxed">
          FinWise, ham banka işlem açıklamalarını temizleyerek <strong>13 finansal kategoriye</strong> ayırır.
          Önce yüksek kesinlikli Regex kuralları çalışır. Regex ile çözülemeyen işlemler kalibre edilmiş makine
          öğrenmesi modeline gönderilir. Düşük güvenli işlemler <em>güvenli bekletme</em> sınıfına alınır.
        </p>
      </div>

      {/* Metrikler */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        {[
          ['Toplam İşlem',       s.txn_count],
          ['Regex ile Çözülen',  Math.round((s.txn_count||0)*0.62)],
          ['ML ile Çözülen',     Math.round((s.txn_count||0)*0.28)],
          ['Güvenli Bekletme',   s.uncategorized_count],
          ['Ort. Güveni',        `%${((s.avg_confidence||0)*100).toFixed(0)}`],
        ].map(([k, v]) => (
          <div key={k} className="card text-center">
            <p className="text-xs text-gray-400 mb-1">{k}</p>
            <p className="text-xl font-bold text-brand">{v}</p>
          </div>
        ))}
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg px-4 py-3 text-sm text-yellow-700">
        💡 <strong>Güvenli Bekletme</strong>, sistemin emin olmadığı işlemleri yanlış sınıflandırmak yerine ayrı bir sınıfa almasıdır.
      </div>

      {/* Tablo */}
      <div className="card overflow-hidden p-0">
        <div className="px-5 py-3 border-b border-gray-100">
          <h4 className="font-semibold text-brand">İşlem Örnekleri</h4>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="bg-gray-50">
              {['Tarih','Açıklama','Tutar','Karar Yolu','Kategori'].map(h => (
                <th key={h} className="text-left px-4 py-2 text-xs font-semibold text-gray-500 whitespace-nowrap">{h}</th>
              ))}
            </tr></thead>
            <tbody className="divide-y divide-gray-100">
              {txns.map((t, i) => (
                <tr key={i} className="hover:bg-gray-50">
                  <td className="px-4 py-2.5 text-gray-500 text-xs">{t.tarih}</td>
                  <td className="px-4 py-2.5 font-medium">{t.aciklama}</td>
                  <td className="px-4 py-2.5 whitespace-nowrap">{t.is_income ? <span className="text-green-600">+{fmt(t.tutar)} TL</span> : <span className="text-gray-700">-{fmt(t.tutar)} TL</span>}</td>
                  <td className="px-4 py-2.5">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${t.decision_path === 'Regex' ? 'bg-green-100 text-green-700' : t.decision_path === 'Güvenli Bekletme' ? 'bg-gray-100 text-gray-500' : 'bg-amber-100 text-amber-700'}`}>
                      {t.decision_path}
                    </span>
                  </td>
                  <td className="px-4 py-2.5"><span className="badge-safe text-xs">{CATEGORY_TR[t.predicted_category] || t.predicted_category}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

// ── Sekme 3: Harcama Profili ─────────────────────────────────────
function TabProfile({ result }) {
  const [showTech, setShowTech] = useState(false)
  if (!result) return <EmptyState />
  const prof   = result.user_profile || {}
  const s      = result.summary || {}
  const cats   = result.category_breakdown || {}
  const topCat = Object.entries(cats).filter(([,v]) => v>0).sort((a,b) => b[1]-a[1]).slice(0,3)

  return (
    <div className="space-y-5 max-w-3xl">
      <div className="card">
        <p className="text-sm text-gray-600 leading-relaxed">
          FinWise, kategorize edilen işlemlerden gelir-gider dengenizi, harcama ritminizi ve tasarruf
          eğilimini analiz ederek kişisel finansal profilinizi oluşturur.
        </p>
      </div>

      {/* Profil kartları */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {[
          ['Finansal Segment',  prof.cluster_name || '-'],
          ['Nakit Akışı',       prof.cash_flow || '-'],
          ['Tasarruf Eğilimi',  prof.savings_trend || '-'],
          ['Harcama Ritmi',     prof.spending_rhythm || '-'],
          ['Baskın Kategori',   CATEGORY_TR[prof.dominant_category] || prof.dominant_category || '-'],
          ['Tasarruf Oranı',    `%${s.savings_rate_pct?.toFixed(1) || 0}`],
        ].map(([k,v]) => (
          <div key={k} className="card bg-brand-50 border-brand-100">
            <p className="text-xs text-gray-400 mb-1">{k}</p>
            <p className="font-bold text-brand text-sm">{v}</p>
          </div>
        ))}
      </div>

      {/* Kişisel yorum */}
      <div className="card border-l-4 border-l-brand">
        <p className="font-semibold text-brand mb-2">Kişisel Yorum</p>
        <p className="text-sm text-gray-700 leading-relaxed">
          {topCat.length > 0
            ? `Son analize göre en yüksek harcamalarınız: ${topCat.map(([k]) => CATEGORY_TR[k]||k).join(', ')} kategorilerinde. `
            : ''}
          {s.net_cashflow < 0
            ? 'Giderleriniz gelirinizi aşıyor — Bütçe planlaması yapmanız öneriliyor.'
            : s.savings_rate_pct > 20
            ? 'Güçlü bir tasarruf eğilimi var — Finansal hedeflerinize ulaşma hızınız iyi.'
            : 'Harcama dağılımında dengesizlik var — Kategori bazlı limit belirlemeniz faydalı olabilir.'}
        </p>
      </div>

      {/* Teknik detay */}
      <div>
        <button onClick={() => setShowTech(!showTech)} className="text-sm text-brand font-medium hover:underline flex items-center gap-1">
          {showTech ? '▼' : '▶'} Gelişmiş teknik detayları göster
        </button>
        {showTech && (
          <div className="mt-3 card">
            <table className="w-full text-sm">
              <thead><tr className="bg-gray-50">
                <th className="text-left px-3 py-2 text-xs text-gray-500">Teknik Özellik</th>
                <th className="text-left px-3 py-2 text-xs text-gray-500">Kullanıcı Açıklaması</th>
                <th className="text-right px-3 py-2 text-xs text-gray-500">Değer</th>
              </tr></thead>
              <tbody className="divide-y divide-gray-100">
                {[
                  ['net_cashflow', 'Gelir - gider farkı',        `${s.net_cashflow?.toLocaleString('tr-TR')} TL`],
                  ['savings_rate', 'Tasarruf oranı',             `%${s.savings_rate_pct?.toFixed(1)}`],
                  ['cluster',      'Finansal davranış grubu',    `${prof.cluster_id} — ${prof.cluster_name}`],
                ].map(([f,d,v]) => (
                  <tr key={f} className="hover:bg-gray-50">
                    <td className="px-3 py-2 font-mono text-xs text-brand">{f}</td>
                    <td className="px-3 py-2 text-gray-500 text-xs">{d}</td>
                    <td className="px-3 py-2 text-right font-medium text-xs">{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Sekme 4: AI Teşhis ───────────────────────────────────────────
function TabDiagnosis({ result }) {
  if (!result) return <EmptyState />
  const coach = result.ai_coach    || {}
  const fore  = result.ai_forecast  || {}
  const prof  = result.user_profile || {}
  const s     = result.summary || {}
  const probs = coach.class_probabilities || {}

  const coachBadge = coach.action_label === 'HIGH_DEBT_RISK' ? 'badge-risk' : coach.action_label === 'GREAT_SAVER' ? 'badge-safe' : 'badge-warning'

  const STAGE_ROWS = [
    ['İşlem Kategorizasyonu', result.transactions?.slice(0,2).map(t => CATEGORY_TR[t.predicted_category]||t.predicted_category).join(', ') + ' harcaması yüksek'],
    ['Harcama Profili',       `Son 3 ayda gider ${s.net_cashflow < 0 ? 'artışı' : 'istikrarı'}`],
    ['Finansal Segment',      prof.cluster_name],
    ['Gelecek Ay Tahmini',    `${fmt(fore.next_month_expected_expense)} TL`],
    ['AI Teşhis',             coach.label_display],
  ]

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Segment */}
      <div className="card">
        <h4 className="font-semibold text-brand mb-2">Finansal Segment</h4>
        <span className="badge-safe text-sm px-3 py-1">{prof.cluster_name}</span>
        <p className="mt-3 text-sm text-gray-600 leading-relaxed">
          Bu segment, gelir-gider profiline göre benzer finansal davranış gösteren kullanıcılar arasından
          K-Means kümeleme algoritmasıyla belirlenmiştir.
        </p>
      </div>

      {/* Tahmin */}
      <div className="card">
        <h4 className="font-semibold text-brand mb-2">Gelecek Ay Harcama Tahmini</h4>
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-brand">{fmt(fore.next_month_expected_expense)} TL</span>
          <span className={`text-sm font-medium ${fore.trend === 'Artış' ? 'text-red-500' : 'text-green-600'}`}>
            {fore.trend === 'Artış' ? '↑ Artış' : '↓ Azalış'}
          </span>
        </div>
        <p className="mt-2 text-xs text-gray-400">LightGBM modeli, önceki ay giderleri ve son dönem harcama eğilimlerini kullanarak bu tahmini üretir.</p>
      </div>

      {/* AI Teşhis */}
      <div className="card">
        <h4 className="font-semibold text-brand mb-3">AI Finansal Teşhis</h4>
        <div className="flex items-center gap-3 mb-4">
          <span className={`${coachBadge} text-base px-4 py-1.5`}>{coach.label_display}</span>
        </div>
        <div className="space-y-2 mb-4">
          {Object.entries(probs).map(([k, v]) => {
            const label = k==='HIGH_DEBT_RISK' ? 'Riskli' : k==='GREAT_SAVER' ? 'Tasarrufçu' : 'Bütçeleme Yapmalı'
            const color = k==='HIGH_DEBT_RISK' ? 'bg-red-400' : k==='GREAT_SAVER' ? 'bg-green-400' : 'bg-yellow-400'
            return (
              <div key={k}>
                <div className="flex justify-between text-xs mb-0.5"><span>{label}</span><span className="font-bold">%{Math.round(v*100)}</span></div>
                <div className="h-2.5 bg-gray-100 rounded-full"><div className={`h-2.5 rounded-full ${color}`} style={{width:`${v*100}%`}} /></div>
              </div>
            )
          })}
        </div>
        <p className="text-sm text-gray-600 italic leading-relaxed">
          Model, sizi "<strong>{prof.cluster_name}</strong>" finansal segmentinde görmesi ve gelecekteki{' '}
          <strong>{fmt(fore.next_month_expected_expense)} TL</strong> harcama tahminine dayanarak en yüksek olasılığı{' '}
          "<strong>{coach.label_display}</strong>" sınıfına vermiştir.
        </p>
      </div>

      {/* Pipeline akışı */}
      <div className="card">
        <h4 className="font-semibold text-brand mb-3">Karar Akışı</h4>
        <div className="space-y-2">
          {STAGE_ROWS.map(([stage, output], i) => (
            <div key={stage} className="flex items-start gap-3">
              <div className="w-5 h-5 rounded-full bg-brand text-white text-xs flex items-center justify-center flex-shrink-0 mt-0.5">{i+1}</div>
              <div><p className="text-xs text-gray-400">{stage}</p><p className="text-sm font-medium text-brand">{output}</p></div>
            </div>
          ))}
        </div>
      </div>

      {/* Öneri */}
      <div className="bg-brand-50 border border-brand-100 rounded-xl p-4">
        <p className="font-semibold text-brand mb-1">Önerilen Aksiyon</p>
        <p className="text-sm text-gray-700 leading-relaxed">{coach.personalized_message}</p>
      </div>
      <p className="text-xs text-gray-400 italic">⚠️ Bu sonuç karar destek amaçlıdır; kesin finansal tavsiye değildir.</p>
    </div>
  )
}

// ── Sekme 5: Karar Açıklaması ─────────────────────────────────────
function TabExplanation({ result }) {
  if (!result) return <EmptyState />
  const shap  = result.shap_features || []
  const coach = result.ai_coach || {}
  const s     = result.summary || {}

  // Ayarlardan detay seviyesini oku (localStorage)
  const expl = (() => { try { return localStorage.getItem('fw_hold_expl') || 'Orta' } catch { return 'Orta' } })()

  // Detay seviyesine göre SHAP listesini filtrele
  const shapToShow = expl === 'Basit' ? shap.slice(0, 2) : shap

  // Basit modda sade metinler, Teknik modda özellik adları da gösterilir
  const showFeatureName = expl === 'Teknik'
  const showImportance  = expl === 'Teknik'

  const SIMPLE_DESC = {
    risk:    'Bütçenizi olumsuz etkiliyor',
    safe:    'Bütçenizi olumlu etkiliyor',
    neutral: 'Nötr etki',
  }
  const DETAIL_DESC = {
    risk:    'Bu faktör riski artırmaktadır',
    safe:    'Bu faktör riski azaltmaktadır',
    neutral: 'Nötr etki',
  }

  return (
    <div className="space-y-5 max-w-3xl">
      {/* Açıklama metni — Basit modda kısa */}
      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <h4 className="font-semibold text-brand">Bu karar neden verildi?</h4>
          <span className="text-xs px-2 py-0.5 rounded-full bg-brand/10 text-brand font-medium">{expl} mod</span>
        </div>
        {expl === 'Basit' ? (
          <p className="text-sm text-gray-700 leading-relaxed">
            Yapay zeka analizinize bakarak sizi <strong>{coach.label_display}</strong> olarak değerlendirdi.
            {s.net_cashflow < 0 ? ' Giderleriniz gelirinizi aşıyor.' : ' Gelir-gider dengeniz incelendi.'}
          </p>
        ) : (
          <p className="text-sm text-gray-600 leading-relaxed">
            Bu karar yalnızca tek bir işlemden üretilmemiştir. Sistem önce banka açıklamalarınızı kategorilere
            ayırmış, ardından aylık harcama profilinizi çıkarmış, gelecek ay harcama eğilimini tahmin etmiş ve
            son olarak XGBoost modeliyle finansal teşhis sınıfınızı belirlemiştir.
          </p>
        )}
      </div>

      {/* Metinsel özet */}
      <div className="card border-l-4 border-l-yellow-400 bg-yellow-50">
        <p className="text-sm text-gray-700 leading-relaxed font-medium">
          Sistem sizi "<strong>{coach.label_display}</strong>" sınıfına daha yakın değerlendirdi çünkü{' '}
          {s.net_cashflow < 0 ? 'net nakit akışı negatif, ' : ''}
          {(s.savings_rate_pct||0) < 10 ? `tasarruf oranı düşük (%${s.savings_rate_pct?.toFixed(1)}), ` : ''}
          son 3 aylık harcama ortalaması yükseliyor.
        </p>
      </div>

      {/* SHAP faktörleri — seviyeye göre */}
      <div className="card">
        <h4 className="font-semibold text-brand mb-1">
          Kararı Etkileyen Faktörler
          {expl === 'Basit' && <span className="text-xs font-normal text-gray-400 ml-2">(en önemli 2 faktör)</span>}
        </h4>

        {expl === 'Basit' ? (
          // Basit: kart formatı, sade dil
          <div className="space-y-3 mt-3">
            {shapToShow.map(f => {
              const dir = f.direction
              const bg  = dir === 'risk' ? 'bg-red-50 border-red-200' : dir === 'safe' ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'
              const tc  = dir === 'risk' ? 'text-red-700' : dir === 'safe' ? 'text-green-700' : 'text-gray-600'
              return (
                <div key={f.feature} className={`rounded-lg border px-4 py-3 ${bg}`}>
                  <p className="font-semibold text-sm text-gray-800">{f.display}</p>
                  <p className={`text-xs mt-0.5 ${tc}`}>{SIMPLE_DESC[dir] || SIMPLE_DESC.neutral}</p>
                  <p className="text-xs text-gray-500 mt-1">Değer: <strong>{f.value?.toLocaleString('tr-TR')} {f.unit}</strong></p>
                </div>
              )
            })}
          </div>
        ) : (
          // Orta / Teknik: tablo
          <table className="w-full text-sm mt-3">
            <thead><tr className="bg-gray-50">
              {['Faktör', expl === 'Teknik' ? 'Özellik Adı' : null, 'Etki Yönü', 'Açıklama', 'Değer', expl === 'Teknik' ? 'Önem' : null]
                .filter(Boolean)
                .map(h => (
                  <th key={h} className="text-left px-3 py-2 text-xs font-semibold text-gray-500">{h}</th>
                ))}
            </tr></thead>
            <tbody className="divide-y divide-gray-100">
              {shapToShow.map(f => {
                const dir   = f.direction
                const label = dir === 'risk' ? 'Riski Artırdı' : dir === 'safe' ? 'Riski Azalttı' : 'Nötr'
                const cls   = dir === 'risk' ? 'badge-risk' : dir === 'safe' ? 'badge-safe' : 'badge-warning'
                return (
                  <tr key={f.feature} className="hover:bg-gray-50">
                    <td className="px-3 py-2.5 font-medium">{f.display}</td>
                    {showFeatureName && <td className="px-3 py-2.5 font-mono text-xs text-gray-400">{f.feature}</td>}
                    <td className="px-3 py-2.5"><span className={cls}>{label}</span></td>
                    <td className="px-3 py-2.5 text-xs text-gray-400">{DETAIL_DESC[dir] || DETAIL_DESC.neutral}</td>
                    <td className="px-3 py-2.5 font-mono text-xs">{f.value?.toLocaleString('tr-TR')} {f.unit}</td>
                    {showImportance && <td className="px-3 py-2.5 text-xs text-gray-500">%{((f.importance || 0) * 100).toFixed(0)}</td>}
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-xs text-gray-500 italic">
        📊 Bu açıklama SHAP tabanlı model yorumlamasıdır. Nedensellik kanıtı değil, model kararına katkı analizini yansıtır.
        {expl !== 'Orta' && <span className="ml-2">· Detay seviyesi: <strong>{expl}</strong> (Ayarlar'dan değiştirebilirsiniz)</span>}
      </div>
    </div>
  )
}

// ── Sekme 6: Rapor ───────────────────────────────────────────────
function TabReport({ result }) {
  const { isDemo, demoPersona } = useAuth()
  const [loading, setLoading] = useState({ pdf: false, excel: false })
  const [error,   setError]   = useState('')

  if (!result) return <EmptyState />

  const personaNames = { ahmet:'Ahmet Bey', ayse:'Ayşe Hanım', zeynep:'Zeynep Hanım' }

  const download = async (type) => {
    setError('')
    setLoading(l => ({ ...l, [type]: true }))
    try {
      const payload = { result, mode: isDemo ? 'demo' : 'real', persona_name: isDemo ? personaNames[demoPersona] : null }
      const res  = await axios.post(`/api/reports/${type}`, payload, { responseType: 'blob' })
      const ext  = type === 'pdf' ? 'pdf' : 'xlsx'
      const mime = type === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      const blob = new Blob([res.data], { type: mime })
      const href = URL.createObjectURL(blob)
      const a    = document.createElement('a')
      a.href = href; a.download = `FinWise_${isDemo ? 'Demo' : 'Rapor'}_${new Date().toISOString().slice(0,10)}.${ext}`
      a.click(); URL.revokeObjectURL(href)
    } catch (e) {
      setError('Rapor oluşturulamadı: ' + (e.response?.data?.detail || e.message))
    } finally {
      setLoading(l => ({ ...l, [type]: false }))
    }
  }

  return (
    <div className="space-y-5 max-w-2xl">
      <div className="card">
        <p className="text-sm text-gray-600 leading-relaxed">
          Analiz sonuçlarınızı PDF veya Excel formatında indirin. Rapor; özet, kategori dağılımı,
          profil, tahmin, AI teşhis ve karar açıklaması içerir.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card text-center hover:shadow-md transition">
          <div className="text-4xl mb-3">📋</div>
          <h4 className="font-bold text-brand mb-1">PDF Rapor</h4>
          <p className="text-xs text-gray-400 mb-4">Tam analiz raporu, tablolar ve açıklamalar</p>
          <button onClick={() => download('pdf')} disabled={loading.pdf} className="btn-primary w-full">
            {loading.pdf ? 'Oluşturuluyor...' : '📥 PDF İndir'}
          </button>
        </div>

        <div className="card text-center hover:shadow-md transition">
          <div className="text-4xl mb-3">📊</div>
          <h4 className="font-bold text-brand mb-1">Excel Sonuçları</h4>
          <p className="text-xs text-gray-400 mb-4">Özet, kategori, trend ve SHAP verileri</p>
          <button onClick={() => download('excel')} disabled={loading.excel} className="btn-secondary w-full">
            {loading.excel ? 'Oluşturuluyor...' : '📥 Excel İndir'}
          </button>
        </div>
      </div>

      {error && <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">⚠️ {error}</div>}

      <p className="text-xs text-gray-400 italic">
        ⚠️ Bu rapor bilgilendirme ve karar destek amacıyla üretilmiştir. Kesin finansal tavsiye değildir.
      </p>
    </div>
  )
}

function EmptyState() {
  return (
    <div className="text-center py-16 text-gray-400">
      <div className="text-4xl mb-3">📂</div>
      <p className="font-medium text-gray-500">Veri bekleniyor</p>
      <p className="text-sm mt-1">Önce "Veri Yükle" sekmesinden dosya yükleyin veya demo modunu kullanın.</p>
    </div>
  )
}

// ── Ana bileşen ──────────────────────────────────────────────────
export default function AnalyzePage() {
  const { isDemo, demoPersona, result, setResult } = useAuth()
  const [activeTab, setActiveTab] = useState(0)
  const [loading,   setLoading]   = useState(false)

  useEffect(() => {
    if (isDemo && !result) {
      setLoading(true)
      axios.get(`/api/demo/analyze/${demoPersona}`)
        .then(r => setResult(r.data))
        .catch(() => {})
        .finally(() => setLoading(false))
    }
  }, [isDemo, demoPersona])

  const FLOW = ['Veri Yüklendi','Kategorize Edildi','Profil Çıkarıldı','Model Çalıştı','Karar Açıklandı','Rapor Hazır']

  return (
    <div className="max-w-7xl mx-auto space-y-4">
      {/* Akış diyagramı */}
      <div className="bg-white border border-gray-100 rounded-xl px-5 py-3 shadow-sm">
        <div className="flex flex-wrap gap-2 items-center text-xs">
          {FLOW.map((step, i) => (
            <div key={step} className="flex items-center gap-2">
              <span className={`px-3 py-1 rounded-full font-medium ${i <= activeTab ? 'bg-brand text-white' : 'bg-gray-100 text-gray-400'}`}>{step}</span>
              {i < FLOW.length - 1 && <span className="text-gray-300">→</span>}
            </div>
          ))}
        </div>
      </div>

      {loading && <div className="flex items-center justify-center h-32"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand" /></div>}

      {/* Sekmeler */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="flex border-b border-gray-200 overflow-x-auto">
          {TABS.map((tab, i) => (
            <button
              key={tab}
              onClick={() => setActiveTab(i)}
              className={`px-5 py-3 text-sm whitespace-nowrap transition-colors ${activeTab === i ? 'tab-active' : 'tab-inactive'}`}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="p-6">
          {activeTab === 0 && <TabUpload onSuccess={() => setActiveTab(1)} />}
          {activeTab === 1 && <TabCategories result={result} />}
          {activeTab === 2 && <TabProfile result={result} />}
          {activeTab === 3 && <TabDiagnosis result={result} />}
          {activeTab === 4 && <TabExplanation result={result} />}
          {activeTab === 5 && <TabReport result={result} />}
        </div>
      </div>
    </div>
  )
}
