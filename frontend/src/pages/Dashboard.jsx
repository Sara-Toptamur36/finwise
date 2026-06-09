import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import axios from 'axios'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, Cell, Legend
} from 'recharts'

const CATEGORY_TR = {
  ALISVERIS:'Alışveriş', BANKA_KESINTISI:'Banka Kes.', DIGER:'Diğer',
  EGITIM:'Eğitim', EGLENCE:'Eğlence', FATURA:'Fatura',
  MARKET:'Market', NAKIT_ISLEMLERI:'Nakit', SAGLIK:'Sağlık',
  SEYAHAT:'Seyahat', ULASIM:'Ulaşım', VIRMAN:'Virman', YEME_ICME:'Yeme-İçme',
}
const COLORS = ['#166534','#16a34a','#22c55e','#86efac','#f59e0b','#fbbf24','#ef4444','#f87171','#84cc16','#a3e635','#4ade80','#6ee7b7','#14b8a6']
const fmt = n => n?.toLocaleString('tr-TR', { maximumFractionDigits: 0 })

function StatCard({ label, value, sub, color = 'default' }) {
  const left = {
    default: 'border-l-gray-300',
    green:   'border-l-green-500',
    red:     'border-l-red-500',
    amber:   'border-l-amber-500',
  }[color] || 'border-l-gray-300'
  return (
    <div className={`card border-l-4 ${left}`}>
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <p className="text-xl font-bold text-gray-900">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
    </div>
  )
}

export default function Dashboard() {
  const { isDemo, demoPersona, user, result, setResult } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true); setError('')
      try {
        if (isDemo) {
          const { data } = await axios.get(`/api/demo/analyze/${demoPersona}`)
          setResult(data)
        } else if (!result) {
          const { data } = await axios.get('/api/analysis/result').catch(() => ({ data: null }))
          if (data) setResult(data)
        }
      } catch (e) {
        setError('Veri yüklenemedi: ' + (e.response?.data?.detail || e.message))
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [isDemo, demoPersona])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-brand border-t-transparent mx-auto mb-3" />
        <p className="text-gray-400 text-sm">Yükleniyor...</p>
      </div>
    </div>
  )

  if (!result && !isDemo) return (
    <div className="flex flex-col items-center justify-center h-64 text-center">
      <div className="text-5xl mb-4">📂</div>
      <h2 className="text-lg font-bold text-gray-800 mb-2">Henüz analiz yapılmadı</h2>
      <p className="text-gray-400 text-sm mb-5">Banka ekstrenizi yükleyerek başlayın.</p>
      <button onClick={() => navigate('/analyze')} className="btn-primary">Analiz Et</button>
    </div>
  )

  if (!result) return <div className="text-center text-gray-400 mt-20 text-sm">Veri bekleniyor...</div>

  const s     = result.summary     || {}
  const prof  = result.user_profile || {}
  const coach = result.ai_coach    || {}
  const fore  = result.ai_forecast  || {}
  const cats  = result.category_breakdown || {}
  const trend = result.monthly_trend     || []

  const coachColor = coach.action_label === 'HIGH_DEBT_RISK' ? 'red'
                   : coach.action_label === 'GREAT_SAVER'    ? 'green' : 'amber'
  const coachBadge = coach.action_label === 'HIGH_DEBT_RISK' ? 'badge-risk'
                   : coach.action_label === 'GREAT_SAVER'    ? 'badge-safe' : 'badge-warning'

  const catData = Object.entries(cats)
    .filter(([, v]) => v > 0)
    .map(([k, v]) => ({ name: CATEGORY_TR[k] || k, tutar: Math.round(v) }))
    .sort((a, b) => b.tutar - a.tutar).slice(0, 8)

  const trendData = [
    ...trend.map(t => ({ month: t.month?.slice(2), gelir: t.income, gider: t.expense })),
    { month: 'Tahmin', gelir: null, gider: null, tahmin: Math.round(fore.next_month_expected_expense || 0) },
  ]

  const probs     = coach.class_probabilities || {}
  const probData  = Object.entries(probs).map(([k, v]) => ({
    name: k === 'HIGH_DEBT_RISK' ? 'Riskli' : k === 'GREAT_SAVER' ? 'Tasarrufçu' : 'Bütçeleme Yapmalı',
    value: Math.round(v * 100),
    color: k === 'HIGH_DEBT_RISK' ? '#ef4444' : k === 'GREAT_SAVER' ? '#22c55e' : '#f59e0b',
  }))

  const greeting = isDemo
    ? `Demo: ${result.persona?.name} — ${result.persona?.subtitle}`
    : `Merhaba ${user?.name?.split(' ')[0]}, ${s.net_cashflow < 0 ? 'giderleriniz geliri aşıyor.' : 'bütçeniz dengede.'}`

  const coachBg = coach.action_label === 'HIGH_DEBT_RISK'
    ? 'bg-red-50 border-red-200'
    : coach.action_label === 'GREAT_SAVER'
    ? 'bg-green-50 border-green-200'
    : 'bg-amber-50 border-amber-200'

  return (
    <div className="space-y-5 max-w-7xl mx-auto">

      {/* Karşılama */}
      <div className={`rounded-xl px-5 py-3 border text-sm font-medium ${isDemo ? 'bg-amber-50 border-amber-200 text-amber-800' : 'bg-green-50 border-green-200 text-green-800'}`}>
        {greeting}
        {isDemo && <span className="ml-2 text-xs font-normal text-amber-600">— anonim örnek veri</span>}
      </div>

      {error && <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">{error}</div>}

      {/* Özet kartlar */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
        <StatCard label="Toplam İşlem"          value={fmt(s.txn_count)}            sub="adet" />
        <StatCard label="Kategorize Edilen"      value={fmt(s.categorized_count)}    sub={`%${((s.categorized_count/s.txn_count)*100||0).toFixed(0)}`} />
        <StatCard label="Kategori Güveni"        value={`%${((s.avg_confidence||0)*100).toFixed(0)}`} />
        <StatCard label="AI Finansal Teşhis"     value={coach.label_display || '-'}  color={coachColor} />
        <StatCard label="Gelecek Ay Tahmini"     value={`${fmt(fore.next_month_expected_expense)} TL`} sub={fore.trend} color="amber" />
        <StatCard label="Düşük Güvenli İşlem"    value={fmt(s.uncategorized_count)}  sub="incelenecek" color={s.uncategorized_count > 20 ? 'red' : 'default'} />
      </div>

      {/* Grafik satırı */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Kategori dağılımı */}
        <div className="card">
          <h3 className="font-semibold text-gray-800 text-sm mb-4">Kategori Bazlı Harcama</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={catData} layout="vertical" margin={{ left: 10, right: 10 }}>
              <XAxis type="number" tickFormatter={v => `${(v/1000).toFixed(0)}K`} tick={{ fontSize: 10 }} />
              <YAxis type="category" dataKey="name" width={75} tick={{ fontSize: 10 }} />
              <Tooltip formatter={v => [`${fmt(v)} TL`, '']} />
              <Bar dataKey="tutar" radius={[0, 4, 4, 0]}>
                {catData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Aylık trend */}
        <div className="card">
          <h3 className="font-semibold text-gray-800 text-sm mb-1">Aylık Trend + Gelecek Ay Tahmini</h3>
          <p className="text-xs text-gray-400 mb-3">Son kesik çubuk LightGBM tahminidir.</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" tick={{ fontSize: 10 }} />
              <YAxis tickFormatter={v => `${(v/1000).toFixed(0)}K`} tick={{ fontSize: 10 }} />
              <Tooltip formatter={v => v ? [`${fmt(v)} TL`] : ['-']} />
              <Bar dataKey="gelir"  name="Gelir"  fill="#22c55e" radius={[3,3,0,0]} />
              <Bar dataKey="gider"  name="Gider"  fill="#166534" radius={[3,3,0,0]} />
              <Bar dataKey="tahmin" name="Tahmin" fill="#f59e0b" radius={[3,3,0,0]} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Alt satır */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

        {/* AI Teşhis dağılımı */}
        <div className="card">
          <h3 className="font-semibold text-gray-800 text-sm mb-3">AI Teşhis Dağılımı</h3>
          <span className={coachBadge + ' mb-4 block w-fit'}>{coach.label_display}</span>
          <div className="space-y-3">
            {probData.map(p => (
              <div key={p.name}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-600">{p.name}</span>
                  <span className="font-semibold">%{p.value}</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full">
                  <div className="h-2 rounded-full transition-all" style={{ width: `${p.value}%`, backgroundColor: p.color }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Profil */}
        <div className="card">
          <h3 className="font-semibold text-gray-800 text-sm mb-4">Finansal Profil</h3>
          <div className="space-y-2.5">
            {[
              ['Segment',           prof.cluster_name],
              ['Nakit Akışı',       prof.cash_flow],
              ['Tasarruf Eğilimi',  prof.savings_trend],
              ['Harcama Ritmi',     prof.spending_rhythm],
              ['Baskın Kategori',   CATEGORY_TR[prof.dominant_category] || prof.dominant_category],
            ].map(([k, v]) => (
              <div key={k} className="flex justify-between items-center text-sm border-b border-gray-50 pb-1 last:border-0">
                <span className="text-gray-400">{k}</span>
                <span className="font-semibold text-gray-800">{v || '-'}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Koç mesajı */}
        <div className={`card border-2 ${coachBg}`}>
          <h3 className="font-semibold text-gray-800 text-sm mb-2">AI Finansal Koç</h3>
          <span className={coachBadge}>{coach.label_display}</span>
          <p className="text-sm text-gray-700 mt-3 leading-relaxed">{coach.personalized_message}</p>
          <button onClick={() => navigate('/analyze')} className="mt-4 text-xs text-brand font-semibold hover:underline">
            Detaylı analiz →
          </button>
        </div>
      </div>
    </div>
  )
}
