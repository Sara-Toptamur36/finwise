import { useState, useEffect } from 'react'
import axios from 'axios'
import { useAuth } from '../context/AuthContext'

export default function ReportsPage() {
  const { result, setResult } = useAuth()
  const [reports,    setReports]    = useState([])
  const [loading,    setLoading]    = useState(true)
  const [error,      setError]      = useState(null)
  const [filter,     setFilter]     = useState('Tümü')
  const [pdfLoading, setPdfLoading] = useState(null)

  useEffect(() => {
    axios.get('/api/analysis/history')
      .then(r => setReports(r.data))
      .catch(() => setError('Raporlar yüklenemedi.'))
      .finally(() => setLoading(false))
  }, [])

  const diagBadge = d =>
    d === 'Riskli' ? 'badge-risk' :
    d === 'Tasarrufçu' ? 'badge-safe' : 'badge-warning'

  const filtered = reports.filter(r => filter === 'Tümü' || r.mode === filter)

  const handlePdf = async (reportId, filename) => {
    setPdfLoading(reportId)
    try {
      const { data: fullResult } = await axios.get(`/api/analysis/result/${reportId}`)
      const resp = await axios.post('/api/reports/pdf',
        { result: fullResult, mode: 'real' },
        { responseType: 'blob' }
      )
      const url  = URL.createObjectURL(resp.data)
      const link = document.createElement('a')
      link.href  = url
      link.download = `BankaAI_${filename.replace(/\.[^.]+$/, '')}_Rapor.pdf`
      link.click()
      URL.revokeObjectURL(url)
    } catch {
      alert('PDF oluşturulurken hata oluştu.')
    } finally {
      setPdfLoading(null)
    }
  }

  const handleView = async (reportId) => {
    try {
      const { data: fullResult } = await axios.get(`/api/analysis/result/${reportId}`)
      setResult(fullResult)
      window.location.href = '/analyze'
    } catch {
      alert('Rapor yüklenemedi.')
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-brand">Raporlarım</h1>
        <p className="text-gray-500 text-sm mt-1">Geçmiş analiz sonuçlarınız ve indirilebilir raporlar.</p>
      </div>

      {/* Filtre */}
      <div className="flex gap-2">
        {['Tümü', 'Kişisel', 'Demo'].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${filter === f ? 'bg-brand text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'}`}>
            {f}
          </button>
        ))}
      </div>

      {/* İçerik */}
      {loading ? (
        <div className="text-center py-20 text-gray-400">
          <div className="text-4xl mb-3 animate-pulse">📊</div>
          <p className="text-sm">Raporlar yükleniyor...</p>
        </div>
      ) : error ? (
        <div className="text-center py-20 text-red-400">
          <div className="text-4xl mb-3">⚠️</div>
          <p className="font-medium">{error}</p>
        </div>
      ) : filtered.length > 0 ? (
        <div className="card overflow-hidden p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="bg-gray-50">
                {['Tarih', 'Dosya', 'Mod', 'Kayıt Sayısı', 'AI Teşhis', 'İşlemler'].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-gray-500">{h}</th>
                ))}
              </tr></thead>
              <tbody className="divide-y divide-gray-100">
                {filtered.map(r => (
                  <tr key={r.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-500 text-xs whitespace-nowrap">{r.date}</td>
                    <td className="px-4 py-3 font-medium text-brand max-w-[160px] truncate" title={r.filename}>{r.filename}</td>
                    <td className="px-4 py-3">
                      <span className={r.mode === 'Demo' ? 'badge-demo' : 'inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-green-100 text-green-700'}>
                        {r.mode}
                      </span>
                    </td>
                    <td className="px-4 py-3">{r.txnCount}</td>
                    <td className="px-4 py-3"><span className={diagBadge(r.diagnosis)}>{r.diagnosis}</span></td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button onClick={() => handleView(r.id)}
                          className="text-xs text-brand font-medium hover:underline">
                          👁 Görüntüle
                        </button>
                        <button onClick={() => handlePdf(r.id, r.filename)}
                          disabled={pdfLoading === r.id}
                          className="text-xs text-gray-500 font-medium hover:text-brand hover:underline disabled:opacity-40">
                          {pdfLoading === r.id ? '...' : '📥 PDF'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="text-center py-20 text-gray-400">
          <div className="text-4xl mb-3">📂</div>
          <p className="font-medium text-gray-500">Henüz rapor oluşturmadınız.</p>
          <p className="text-sm mt-1">İlk finansal analizinizi başlatmak için "Analiz Et" sayfasına gidin.</p>
          <a href="/analyze" className="btn-primary mt-4 inline-block">Analiz Et</a>
        </div>
      )}

      {/* Mevcut sonuç varsa ama raporlar boşsa */}
      {result && reports.length === 0 && !loading && (
        <div className="card border-dashed border-2 border-brand-200">
          <h4 className="font-semibold text-brand mb-2">✅ Mevcut Analizinizden Rapor Oluştur</h4>
          <p className="text-sm text-gray-500 mb-3">Son yükleme/demo sonucundan direkt rapor alabilirsiniz.</p>
          <a href="/analyze" className="btn-secondary text-sm">Analiz sayfasına git → Rapor sekmesi</a>
        </div>
      )}
    </div>
  )
}
