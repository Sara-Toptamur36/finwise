import { useState } from 'react'
import axios from 'axios'
import { useAuth } from '../context/AuthContext'
import { getSettings, saveSettings } from '../hooks/useSettings'
import PasswordInput from '../components/PasswordInput'

// ── Bileşen DIŞINDA tanımlı → her render'da yeniden oluşturulmaz,
//    React aynı tip olarak görür → children unmount olmaz → focus korunur ──
function Section({ title, children }) {
  return (
    <div className="card space-y-4">
      <h3 className="font-bold text-brand text-base border-b border-gray-100 pb-2">{title}</h3>
      {children}
    </div>
  )
}

const EXPL_DESC = {
  Basit:   'En önemli 2 faktör, sade dil — teknik terim yok.',
  Orta:    'Tüm faktörler, kısa açıklamalar ile.',
  Teknik:  'Tüm faktörler + özellik adları + önem skorları.',
}

export default function SettingsPage() {
  const { user, isDemo, setResult } = useAuth()
  const [name,      setName]      = useState(user?.name || '')
  const [email,     setEmail]     = useState(user?.email || '')
  const [saved,     setSaved]     = useState(false)
  const [modelSaved, setModelSaved] = useState(false)
  const [deleting,  setDeleting]  = useState(null)
  const [delMsg,    setDelMsg]    = useState('')

  // Şifre değiştirme
  const [currentPw,  setCurrentPw]  = useState('')
  const [newPw,      setNewPw]      = useState('')
  const [confirmPw,  setConfirmPw]  = useState('')
  const [pwSaving,   setPwSaving]   = useState(false)
  const [pwMsg,      setPwMsg]      = useState('')

  // localStorage'dan mevcut ayarları yükle
  const initial = getSettings()
  const [holdThres, setHoldThres] = useState(initial.holdThres)
  const [holdExpl,  setHoldExpl]  = useState(initial.holdExpl)

  const saveProfile = () => { setSaved(true); setTimeout(() => setSaved(false), 2500) }

  const changePassword = async () => {
    setPwMsg('')
    if (!currentPw) { setPwMsg('⚠️ Mevcut şifrenizi girin.'); return }
    if (newPw.length < 6) { setPwMsg('⚠️ Yeni şifre en az 6 karakter olmalı.'); return }
    if (newPw !== confirmPw) { setPwMsg('⚠️ Yeni şifreler eşleşmiyor.'); return }
    setPwSaving(true)
    try {
      await axios.post('/api/auth/change-password', {
        current_password: currentPw,
        new_password: newPw,
      })
      setPwMsg('✅ Şifreniz başarıyla güncellendi.')
      setCurrentPw(''); setNewPw(''); setConfirmPw('')
      setTimeout(() => setPwMsg(''), 3500)
    } catch (e) {
      setPwMsg('⚠️ ' + (e.response?.data?.detail || 'Şifre değiştirilemedi.'))
    } finally {
      setPwSaving(false)
    }
  }

  const saveModelPrefs = () => {
    saveSettings({ holdThres, holdExpl })
    setModelSaved(true)
    setTimeout(() => setModelSaved(false), 2500)
  }

  const handleDelete = async (type) => {
    const messages = {
      data:    'Mevcut analiz verisi bellekten silinsin mi? (Raporlar korunur)',
      reports: 'Tüm rapor geçmişi kalıcı olarak silinsin mi? Bu işlem geri alınamaz.',
    }
    if (!window.confirm(messages[type])) return
    setDeleting(type); setDelMsg('')
    try {
      await axios.delete(`/api/analysis/${type}`)
      if (type === 'data' || type === 'reports') setResult(null)
      setDelMsg(type === 'data' ? '✅ Analiz verisi silindi.' : '✅ Rapor geçmişi temizlendi.')
      setTimeout(() => setDelMsg(''), 3000)
    } catch (e) {
      setDelMsg('⚠️ Silme işlemi başarısız: ' + (e.response?.data?.detail || e.message))
    } finally {
      setDeleting(null)
    }
  }

  if (isDemo) return (
    <div className="max-w-lg mx-auto text-center py-20">
      <div className="text-4xl mb-4">🔒</div>
      <h2 className="text-xl font-bold text-brand mb-2">Ayarlar Demo Modunda Kullanılamaz</h2>
      <p className="text-gray-500 text-sm">Ayarlara erişim için kayıt olup giriş yapın.</p>
      <div className="flex gap-3 justify-center mt-6">
        <a href="/register" className="btn-primary">Kayıt Ol</a>
        <a href="/login" className="btn-secondary">Giriş Yap</a>
      </div>
    </div>
  )

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-brand">Ayarlar</h1>

      {saved      && <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700">✅ Profil değişiklikleri kaydedildi.</div>}
      {modelSaved && <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700">✅ Model tercihleri kaydedildi. Karar Açıklaması sekmesine yansıyacak.</div>}
      {delMsg     && <div className={`p-3 rounded-lg text-sm border ${delMsg.startsWith('✅') ? 'bg-green-50 border-green-200 text-green-700' : 'bg-red-50 border-red-200 text-red-600'}`}>{delMsg}</div>}

      {/* Profil */}
      <Section title="Profil Ayarları">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Ad Soyad</label>
          <input value={name} onChange={e => setName(e.target.value)} className="input-field" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">E-posta</label>
          <input value={email} onChange={e => setEmail(e.target.value)} type="email" className="input-field" />
        </div>
        <button onClick={saveProfile} className="btn-primary">Kaydet</button>
      </Section>

      {/* Şifre Değiştir */}
      <Section title="Şifre Değiştir">
        {pwMsg && (
          <div className={`p-3 rounded-lg text-sm border ${pwMsg.startsWith('✅') ? 'bg-green-50 border-green-200 text-green-700' : 'bg-red-50 border-red-200 text-red-600'}`}>
            {pwMsg}
          </div>
        )}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Mevcut Şifre</label>
          <PasswordInput value={currentPw} onChange={e => setCurrentPw(e.target.value)} placeholder="Mevcut şifreniz" autoComplete="current-password" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Yeni Şifre</label>
          <PasswordInput value={newPw} onChange={e => setNewPw(e.target.value)} placeholder="En az 6 karakter" autoComplete="new-password" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Yeni Şifre (Tekrar)</label>
          <PasswordInput value={confirmPw} onChange={e => setConfirmPw(e.target.value)} placeholder="Yeni şifrenizi tekrar girin" autoComplete="new-password" />
        </div>
        <button onClick={changePassword} disabled={pwSaving} className="btn-primary disabled:opacity-50">
          {pwSaving ? 'Kaydediliyor...' : 'Şifreyi Güncelle'}
        </button>
      </Section>

      {/* Veri Temizleme */}
      <Section title="Veri Temizleme">
        <div className="space-y-2">
          {[
            ['Yüklenen verileri sil',  'Analiz verileri ve geçici dosyalar', 'data'],
            ['Rapor geçmişini temizle','Kayıtlı rapor listesi',              'reports'],
          ].map(([label, sub, type]) => (
            <button key={type} onClick={() => handleDelete(type)} disabled={deleting === type}
              className="w-full text-left px-4 py-2.5 border border-gray-200 rounded-lg text-sm hover:bg-red-50 hover:border-red-200 hover:text-red-600 transition-colors disabled:opacity-50">
              <p className="font-medium">{deleting === type ? 'Siliniyor...' : label}</p>
              <p className="text-xs text-gray-400">{sub}</p>
            </button>
          ))}
        </div>
      </Section>

      {/* Model Tercihleri */}
      <Section title="Model Tercihleri (Gelişmiş)">
        {/* Güven eşiği */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <label className="text-sm font-medium text-gray-700">Düşük Güven Eşiği</label>
            <span className="text-sm font-bold text-brand">{holdThres.toFixed(2)}</span>
          </div>
          <input type="range" min={0.5} max={0.9} step={0.05} value={holdThres}
            onChange={e => setHoldThres(Number(e.target.value))} className="w-full accent-brand" />
          <div className="flex justify-between text-xs text-gray-400 mt-0.5">
            <span>0.50 — Az seçici</span><span>0.90 — Çok seçici</span>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Eşik yükseldikçe sistem daha fazla işlemi <em>Güvenli Bekletme</em> sınıfına alır.
            Şu an: işlemlerin yaklaşık <strong>%{Math.round((holdThres - 0.5) / 0.4 * 30 + 5)}</strong>'i bekletmeye alınıyor.
          </p>
        </div>

        {/* Güvenli Bekletme Sınıfı */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Güvenli Bekletme Sınıfı</label>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-sm text-green-600 font-medium">Aktif</span>
            <span className="text-xs text-gray-400 ml-1">— Güven &lt; {holdThres.toFixed(2)} olan işlemler bekletiliyor</span>
          </div>
        </div>

        {/* Açıklama Detay Seviyesi */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Açıklama Detay Seviyesi</label>
          <div className="flex gap-2 mb-2">
            {['Basit','Orta','Teknik'].map(o => (
              <button key={o} onClick={() => setHoldExpl(o)}
                className={`px-4 py-1.5 rounded-lg text-sm border transition-colors ${holdExpl===o ? 'bg-brand text-white border-brand' : 'bg-white text-gray-600 border-gray-200 hover:border-brand'}`}>
                {o}
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-500 bg-gray-50 rounded-lg px-3 py-2 border border-gray-100">
            <strong>{holdExpl}:</strong> {EXPL_DESC[holdExpl]}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            💡 Bu ayar "Analiz Et → Karar Açıklaması" sekmesini etkiler.
          </p>
        </div>

        <button onClick={saveModelPrefs} className="btn-primary w-full">
          Tercihleri Kaydet
        </button>
      </Section>
    </div>
  )
}
