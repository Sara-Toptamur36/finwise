import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import axios from 'axios'

const fmt = n => n != null ? Math.round(n).toLocaleString('tr-TR') : '-'

function Slider({ label, value, min, max, step = 5, onChange }) {
  return (
    <div>
      <div className="flex justify-between items-center mb-1">
        <label className="text-sm text-gray-700">{label}</label>
        <span className={`text-sm font-bold ${value > 0 ? 'text-green-600' : value < 0 ? 'text-red-500' : 'text-gray-500'}`}>
          {value > 0 ? '+' : ''}{value}%
        </span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(Number(e.target.value))}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-brand"
      />
      <div className="flex justify-between text-xs text-gray-400 mt-0.5">
        <span>{min}%</span><span>0</span><span>+{max}%</span>
      </div>
    </div>
  )
}

function DiffCell({ current, scenario, unit = 'TL', better = 'high' }) {
  const diff      = scenario - current
  const better_if = better === 'high' ? diff > 0 : diff < 0
  const color     = diff === 0 ? 'text-gray-600' : better_if ? 'text-green-600' : 'text-red-500'
  return (
    <td className="px-4 py-3 text-right">
      <div className="font-semibold">{fmt(scenario)} {unit}</div>
      {diff !== 0 && <div className={`text-xs ${color}`}>{diff > 0 ? '+' : ''}{fmt(diff)}</div>}
    </td>
  )
}

export default function ScenarioPage() {
  const { result, isDemo, demoPersona, setResult } = useAuth()
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(false)
  const [testRes, setTestRes] = useState(null)
  const [error,   setError]   = useState('')

  const [incCh, setIncCh] = useState(0)
  const [expCh, setExpCh] = useState(0)
  const [mktCh, setMktCh] = useState(0)
  const [yemCh, setYemCh] = useState(0)
  const [savCh, setSavCh] = useState(0)

  useEffect(() => {
    const load = async () => {
      if (result) { setData(result); return }
      if (isDemo) {
        setLoading(true)
        try {
          const { data: d } = await axios.get(`/api/demo/analyze/${demoPersona}`)
          setResult(d); setData(d)
        } catch {} finally { setLoading(false) }
        return
      }
      // Giriş yapmış gerçek kullanıcı: son analiz sonucunu API'dan yükle
      setLoading(true)
      try {
        const { data: d } = await axios.get('/api/analysis/result')
        setResult(d); setData(d)
      } catch {
        // 404 = henüz analiz yok, hata gösterme
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [result, isDemo, demoPersona])

  const runScenario = async () => {
    if (!data) return
    setError(''); setLoading(true); setTestRes(null)
    try {
      const s = data.summary || {}
      const c = data.ai_coach || {}
      const { data: res } = await axios.post('/api/scenario/test', {
        income:             s.total_income,
        expense:            s.total_expense,
        savings_rate:       (s.savings_rate_pct || 0) / 100,
        net_cashflow:       s.net_cashflow,
        action_label:       c.action_label,
        class_probs:        c.class_probabilities || {},
        income_change_pct:  incCh,
        expense_change_pct: expCh,
        market_change_pct:  mktCh,
        yemek_change_pct:   yemCh,
        savings_change_pct: savCh,
      })
      setTestRes(res)
    } catch (e) {
      setError(e.response?.data?.detail || 'Senaryo hesaplanamadı.')
    } finally {
      setLoading(false)
    }
  }

  const reset = () => { setIncCh(0); setExpCh(0); setMktCh(0); setYemCh(0); setSavCh(0); setTestRes(null) }

  if (!data && !loading) return (
    <div className="flex flex-col items-center justify-center h-64 text-center">
      <div className="text-5xl mb-4">🔮</div>
      <p className="font-medium text-gray-700 mb-2">Senaryo testi için önce analiz yapılmalı</p>
      <a href="/analyze" className="btn-primary mt-2">Analiz Et</a>
    </div>
  )

  const s = data?.summary || {}
  const c = data?.ai_coach || {}

  const coachBadge = (label) => label === 'HIGH_DEBT_RISK' ? 'badge-risk' : label === 'GREAT_SAVER' ? 'badge-safe' : 'badge-warning'
  const PROBS_TR   = { 'HIGH_DEBT_RISK':'Riskli', 'GREAT_SAVER':'Tasarrufçu', 'NEEDS_BUDGETING':'Bütçeleme Yapmalı' }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-brand">Senaryo Testi</h1>
        <p className="text-gray-500 text-sm mt-1">Gelir veya gider değişirse AI teşhisinizin nasıl değişeceğini simüle edin.</p>
      </div>

      {error && <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">⚠️ {error}</div>}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Slider paneli */}
        <div className="card space-y-5">
          <h3 className="font-semibold text-brand">Senaryoyu Ayarla</h3>
          <Slider label="Gelir Değişimi"          value={incCh} min={-50} max={50} onChange={setIncCh} />
          <Slider label="Gider Değişimi"          value={expCh} min={-50} max={50} onChange={setExpCh} />
          <Slider label="Market Harcaması"        value={mktCh} min={-50} max={50} onChange={setMktCh} />
          <Slider label="Yeme-İçme Harcaması"     value={yemCh} min={-50} max={50} onChange={setYemCh} />
          <Slider label="Tasarruf Oranı"          value={savCh} min={-30} max={30} onChange={setSavCh} />

          {(Math.abs(incCh) + Math.abs(expCh) > 70) && (
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 text-xs text-orange-700">
              ⚠️ <strong>Model güvenlik uyarısı:</strong> Bu senaryo mevcut finansal profilinize çok uzak olduğu
              için tahmin tutarlılığı düşebilir. Daha gerçekçi bir aralık seçmeniz önerilir.
            </div>
          )}

          <div className="flex gap-3">
            <button onClick={runScenario} disabled={loading} className="btn-primary flex-1">
              {loading ? 'Hesaplanıyor...' : '🔮 Senaryoyu Hesapla'}
            </button>
            <button onClick={reset} className="btn-ghost">Sıfırla</button>
          </div>
        </div>

        {/* Mevcut durum */}
        <div className="card">
          <h3 className="font-semibold text-brand mb-4">Mevcut Durum</h3>
          <div className="space-y-3">
            {[
              ['AI Teşhis',       c.label_display || '-'],
              ['Gelir',           `${fmt(s.total_income)} TL`],
              ['Gider',           `${fmt(s.total_expense)} TL`],
              ['Net Nakit Akışı', `${s.net_cashflow > 0 ? '+' : ''}${fmt(s.net_cashflow)} TL`],
              ['Tasarruf Oranı',  `%${s.savings_rate_pct?.toFixed(1) || 0}`],
            ].map(([k, v]) => (
              <div key={k} className="flex justify-between items-center py-1.5 border-b border-gray-100 last:border-0">
                <span className="text-sm text-gray-500">{k}</span>
                <span className="text-sm font-semibold text-brand">{v}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Sonuç */}
      {testRes && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500">Senaryo Güven Seviyesi:</span>
            <span className={`font-semibold text-sm ${testRes.confidence_level === 'Yüksek' ? 'text-green-600' : testRes.confidence_level === 'Orta' ? 'text-yellow-600' : 'text-red-500'}`}>
              {testRes.confidence_level}
              {testRes.ood_warning && ' — Dağılım dışı senaryo'}
            </span>
          </div>

          {/* Önce / Sonra */}
          <div className="card overflow-hidden p-0">
            <div className="px-5 py-3 bg-brand text-white">
              <h4 className="font-semibold">Senaryo Sonuçları — Önce / Sonra</h4>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead><tr className="bg-gray-50">
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500">Metrik</th>
                  <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500">Mevcut</th>
                  <th className="text-right px-4 py-3 text-xs font-semibold text-gray-500">Senaryo</th>
                </tr></thead>
                <tbody className="divide-y divide-gray-100">
                  <tr className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">AI Teşhis</td>
                    <td className="px-4 py-3 text-right"><span className={coachBadge(testRes.current.action_label)}>{testRes.current.label_display}</span></td>
                    <td className="px-4 py-3 text-right"><span className={coachBadge(testRes.scenario.action_label)}>{testRes.scenario.label_display}</span></td>
                  </tr>
                  {[
                    ['Gelir',              testRes.current.income,           testRes.scenario.income,           'TL', 'high'],
                    ['Gider',              testRes.current.expense,          testRes.scenario.expense,          'TL', 'low'],
                    ['Net Nakit Akışı',    testRes.current.net_cashflow,     testRes.scenario.net_cashflow,     'TL', 'high'],
                    ['Tasarruf Oranı',     testRes.current.savings_rate_pct, testRes.scenario.savings_rate_pct, '%',  'high'],
                    ['Gelecek Ay Tahmini', null,                             testRes.scenario.forecast,         'TL', 'low'],
                  ].map(([label, cur, scen, unit, better]) => (
                    <tr key={label} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium">{label}</td>
                      <td className="px-4 py-3 text-right text-gray-500">{cur != null ? `${fmt(cur)} ${unit}` : '—'}</td>
                      <DiffCell current={cur||0} scenario={scen} unit={unit} better={better} />
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Olasılık karşılaştırma */}
          <div className="card">
            <h4 className="font-semibold text-brand mb-4">Model Karar Dağılımı — Önce / Sonra</h4>
            <div className="space-y-3">
              {Object.entries(testRes.current.class_probs).map(([k, curV]) => {
                const scnV = testRes.scenario.class_probs[k] || 0
                return (
                  <div key={k}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-gray-600">{PROBS_TR[k] || k}</span>
                      <span>%{Math.round(curV*100)} → <strong className={scnV > curV ? 'text-green-600' : scnV < curV ? 'text-red-500' : 'text-gray-600'}>%{Math.round(scnV*100)}</strong></span>
                    </div>
                    <div className="flex gap-1 h-2">
                      <div className="flex-1 bg-gray-100 rounded-l-full overflow-hidden">
                        <div className="h-full bg-brand/40 rounded-l-full" style={{ width: `${curV*100}%` }} />
                      </div>
                      <div className="flex-1 bg-gray-100 rounded-r-full overflow-hidden">
                        <div className="h-full bg-brand rounded-r-full" style={{ width: `${scnV*100}%` }} />
                      </div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-400 mt-0.5"><span>Mevcut</span><span>Senaryo</span></div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Metinsel öneri */}
          <div className="card border-l-4 border-l-green-400 bg-green-50">
            <p className="text-sm text-gray-700 leading-relaxed">{testRes.narrative}</p>
          </div>

          <p className="text-xs text-gray-400 italic">⚠️ Senaryo sonuçları tahmini simülasyondur. Gerçek finansal sonuç garantisi vermez.</p>
        </div>
      )}
    </div>
  )
}
