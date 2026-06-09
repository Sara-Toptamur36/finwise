import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { LogoIcon, LogoText } from '../components/Logo'
import PasswordInput from '../components/PasswordInput'

// ── KVKK metni ──────────────────────────────────────────────────────────────
const KVKK_TEXT = `KİŞİSEL VERİLERİN KORUNMASI KANUNU AYDINLATMA METNİ

Veri Sorumlusu: FinWise (Prototip Uygulama)

1. İŞLENEN KİŞİSEL VERİLER
Uygulamamız aracılığıyla yalnızca aşağıdaki finansal işlem verileri işlenmektedir:
• İşlem tarihi, açıklaması ve tutarı
• Gelir/gider sınıflandırma bilgisi
• Hesap bakiyesi (opsiyonel)

Kimlik tespitine yarayan IBAN, T.C. Kimlik Numarası, kart numarası gibi hassas kişisel veriler otomatik maskeleme sistemi tarafından tespit edilerek işlenmez ve saklanmaz.

2. VERİLERİN İŞLENME AMAÇLARI
Kişisel verileriniz aşağıdaki amaçlarla işlenmektedir:
• Banka ekstre işlemlerinin otomatik olarak kategorilendirilmesi
• Harcama profili ve finansal segment analizi oluşturulması
• Gelecek dönem harcama tahmini yapılması
• Yapay zeka destekli finansal teşhis ve öneri üretilmesi
• Kişiselleştirilmiş raporların hazırlanması

3. VERİLERİN İŞLENME HUKUKİ DAYANAĞI
Verileriniz, 6698 sayılı KVKK'nın 5. maddesi kapsamında açık rızanıza dayalı olarak işlenmektedir.

4. VERİLERİN SAKLANMASI VE AKTARILMASI
• Yüklenen ekstreler yalnızca aktif oturum süresince bellekte tutulur; sunucu kapatıldığında veya oturum sonlandırıldığında kalıcı olarak silinir.
• Verileriniz hiçbir üçüncü kişi, kurum veya kuruluşla paylaşılmaz.
• Yurt dışı veri aktarımı yapılmamaktadır.

5. VERİLERİN KORUNMASI
• Tüm veri iletimi HTTPS şifrelemesi ile güvence altına alınmaktadır.
• Uygulama, PCI DSS kapsamında hassas finansal veri içermeyecek şekilde tasarlanmıştır.
• Yapay zeka modelleri yalnızca lokal sunucuda çalışmakta, dış servise veri gönderilmemektedir.

6. HAKLARINIZ
KVKK'nın 11. maddesi kapsamında aşağıdaki haklara sahipsiniz:
• Kişisel verilerinizin işlenip işlenmediğini öğrenme
• İşlenen verilerinize ilişkin bilgi talep etme
• Verilerinizin silinmesini veya yok edilmesini talep etme
• İşlemenin kısıtlanmasını talep etme
• Kişisel verilerinizin aktarıldığı üçüncü kişileri öğrenme
• Otomatik sistemler aracılığıyla aleyhinize sonuç doğuran kararlara itiraz etme

Bu aydınlatma metni, 6698 sayılı Kişisel Verilerin Korunması Kanunu ve Aydınlatma Yükümlülüğünün Yerine Getirilmesinde Uyulacak Usul ve Esaslar Hakkında Tebliğ çerçevesinde hazırlanmıştır.`

// ── Kullanım Koşulları metni ────────────────────────────────────────────────
const TERMS_TEXT = `KULLANIM KOŞULLARI VE HİZMET SÖZLEŞMESİ

Son Güncelleme: Ocak 2026

Bu uygulamayı kullanarak aşağıdaki koşulları kabul etmiş sayılırsınız. Lütfen dikkatlice okuyunuz.

1. HİZMETİN KAPSAMI
FinWise, banka ekstrelerinizi yapay zekâ yardımıyla analiz eden; harcama kategorilendirmesi, finansal profil çıkarımı, gider tahmini ve finansal teşhis yapan açıklanabilir bir karar destek aracıdır.

2. FİNANSAL TAVSİYE DEĞİLDİR
• Uygulamamız tarafından üretilen analizler, tahminler ve öneriler yalnızca bilgilendirme ve karar destek amacı taşımaktadır.
• Hiçbir içerik, 6362 sayılı Sermaye Piyasası Kanunu veya 5411 sayılı Bankacılık Kanunu kapsamında yatırım tavsiyesi, kredi önerisi veya finansal danışmanlık hizmeti niteliği taşımaz.
• Finansal kararlarınızı vermeden önce yetkili bir finansal danışmana başvurmanızı tavsiye ederiz.

3. KULLANICI YÜKÜMLÜLÜKLERİ
Kullanıcı olarak aşağıdakileri kabul edersiniz:
• Uygulamayı yalnızca yasal amaçlarla kullanmayı
• Başkasına ait hesap verilerini izinsiz yüklememeyı
• Sisteme zarar verecek yazılım veya kod göndermemeyi
• Elde ettiğiniz analiz sonuçlarını üçüncü kişilere yanıltıcı şekilde sunmamayı

4. SORUMLULUK SINIRLAMASI
• Uygulama "olduğu gibi" sunulmaktadır; herhangi bir kesintisiz çalışma garantisi verilmemektedir.
• Yapay zeka modelleri olasılıksal çalışır; çıktılar kesin doğruluk garantisi taşımaz.
• Analiz sonuçlarına dayanılarak alınan kararlardan doğan zararlar için sorumluluk kabul edilmez.
• Bu uygulama bir prototiptir; ticari veya kurumsal finans süreçlerinde kullanılması önerilmez.

5. FİKRİ MÜLKİYET
Uygulamada kullanılan yapay zeka modelleri, algoritmalar, tasarım ve yazılım bileşenlerinin tüm hakları saklıdır. İzinsiz kopyalama, dağıtım veya ticari kullanım yasaktır.

6. GİZLİLİK
Kişisel verilerinizin işlenmesine ilişkin ayrıntılı bilgi için KVKK Aydınlatma Metnini inceleyiniz.

7. KOŞULLARDA DEĞİŞİKLİK
Kullanım koşulları önceden bildirim yapılmaksızın güncellenebilir. Uygulamayı kullanmaya devam etmeniz güncel koşulları kabul ettiğiniz anlamına gelir.

8. UYGULANACAK HUKUK
Bu sözleşme Türkiye Cumhuriyeti hukuku kapsamında yorumlanır ve uygulanır. Uyuşmazlıklarda Türk mahkemeleri yetkilidir.`

// ── Modal bileşeni ───────────────────────────────────────────────────────────
function LegalModal({ title, text, onClose }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[80vh] flex flex-col">
        {/* Başlık */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200">
          <h2 className="font-bold text-gray-900 text-sm">{title}</h2>
          <button onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-700 transition text-lg leading-none">
            ×
          </button>
        </div>
        {/* İçerik */}
        <div className="overflow-y-auto p-5 flex-1">
          <pre className="text-xs text-gray-600 whitespace-pre-wrap leading-relaxed font-sans">{text}</pre>
        </div>
        {/* Kapat */}
        <div className="px-5 py-3 border-t border-gray-100 flex justify-end">
          <button onClick={onClose} className="btn-primary text-sm px-6 py-2">
            Okudum, Anladım
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Ana bileşen ──────────────────────────────────────────────────────────────
export default function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form,    setForm]    = useState({ name:'', email:'', password:'', password2:'', kvkk:false, terms:false })
  const [error,   setError]   = useState('')
  const [loading, setLoading] = useState(false)
  const [modal,   setModal]   = useState(null) // 'kvkk' | 'terms' | null

  const update = e => {
    const { name, value, type, checked } = e.target
    setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }))
  }

  const handleSubmit = async e => {
    e.preventDefault(); setError('')
    if (form.password !== form.password2) return setError('Şifreler eşleşmiyor.')
    if (form.password.length < 6)         return setError('Şifre en az 6 karakter olmalıdır.')
    if (!form.kvkk || !form.terms)        return setError('KVKK ve Kullanım Koşulları onaylanmalıdır.')
    setLoading(true)
    try {
      await register(form.name, form.email, form.password, form.kvkk, form.terms)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Kayıt başarısız. Lütfen tekrar deneyin.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-10">

      {/* Modal */}
      {modal === 'kvkk'  && <LegalModal title="KVKK Aydınlatma Metni"   text={KVKK_TEXT}  onClose={() => setModal(null)} />}
      {modal === 'terms' && <LegalModal title="Kullanım Koşulları"       text={TERMS_TEXT} onClose={() => setModal(null)} />}

      <div className="w-full max-w-sm">

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-3">
            <LogoIcon size={48} />
          </div>
          <LogoText className="text-2xl font-black tracking-tight" />
          <p className="text-sm text-gray-400 mt-1">Ücretsiz hesap oluşturun</p>
        </div>

        <div className="card">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-600">
              ⚠️ {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3.5">
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1.5">Ad Soyad</label>
              <input name="name" required value={form.name} onChange={update}
                className="input-field" placeholder="Ayşe Yılmaz" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1.5">E-posta</label>
              <input name="email" type="email" required value={form.email} onChange={update}
                className="input-field" placeholder="ayse@ornek.com" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1.5">Şifre</label>
              <PasswordInput name="password" required value={form.password} onChange={update} placeholder="En az 6 karakter" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1.5">Şifre Tekrar</label>
              <PasswordInput name="password2" required value={form.password2} onChange={update} placeholder="Şifrenizi tekrar girin" />
            </div>

            {/* Onay kutuları */}
            <div className="space-y-2.5 pt-1">
              <label className="flex items-start gap-2 cursor-pointer">
                <input type="checkbox" name="kvkk" checked={form.kvkk} onChange={update}
                  className="mt-0.5 accent-brand shrink-0" />
                <span className="text-xs text-gray-500 leading-relaxed">
                  <button type="button"
                    onClick={() => setModal('kvkk')}
                    className="font-bold text-brand hover:underline">
                    KVKK Aydınlatma Metni
                  </button>
                  'ni okudum ve kişisel verilerimin işlenmesine onay veriyorum.
                </span>
              </label>
              <label className="flex items-start gap-2 cursor-pointer">
                <input type="checkbox" name="terms" checked={form.terms} onChange={update}
                  className="mt-0.5 accent-brand shrink-0" />
                <span className="text-xs text-gray-500 leading-relaxed">
                  <button type="button"
                    onClick={() => setModal('terms')}
                    className="font-bold text-brand hover:underline">
                    Kullanım Koşulları
                  </button>
                  'nı okudum ve kabul ediyorum.
                </span>
              </label>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-xs text-green-700">
              🛡️ Verileriniz yalnızca analiz amacıyla işlenir. Kalıcı olarak saklanmaz.
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? 'Oluşturuluyor...' : 'Hesap Oluştur'}
            </button>
          </form>

          <p className="mt-4 text-center text-xs text-gray-400">
            Hesabın var mı?{' '}
            <Link to="/login" className="text-brand font-semibold hover:underline">Giriş Yap</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
