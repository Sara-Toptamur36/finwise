# Katkıda Bulunma Rehberi

FinWise'a katkıda bulunmak istediğiniz için teşekkürler! 🎉

Bu rehber, projeye katkı sürecini açıklar.

---

## 📋 İçindekiler

- [Davranış Kuralları](#davranış-kuralları)
- [Nasıl Katkıda Bulunabilirim?](#nasıl-katkıda-bulunabilirim)
- [Geliştirme Ortamı Kurulumu](#geliştirme-ortamı-kurulumu)
- [Commit Mesajı Formatı](#commit-mesajı-formatı)
- [Pull Request Süreci](#pull-request-süreci)
- [Kod Standartları](#kod-standartları)

---

## Davranış Kuralları

- Saygılı ve yapıcı bir iletişim dili kullanın
- Farklı görüşlere açık olun
- Topluluğun büyümesine katkı sağlayın

---

## Nasıl Katkıda Bulunabilirim?

### 🐛 Hata Bildirimi

1. [Issues](https://github.com/Sara-Toptamur36/finwise/issues) sayfasını kontrol edin — hata daha önce bildirilmiş olabilir
2. Yeni issue açın ve **Bug Report** şablonunu kullanın
3. Hatayı yeniden oluşturmak için adımları detaylı yazın

### 💡 Özellik Önerisi

1. [Issues](https://github.com/Sara-Toptamur36/finwise/issues) sayfasında **Feature Request** şablonunu kullanın
2. Özelliğin ne sorunu çözdüğünü açıklayın
3. Varsa örnek kullanım senaryosu ekleyin

### 🔧 Kod Katkısı

Aşağıdaki alanlarda katkı memnuniyetle karşılanır:

- Hata düzeltmeleri
- Yeni özellikler
- Performans iyileştirmeleri
- Dokümantasyon güncellemeleri
- Test yazımı
- Türkçe çeviri / metin düzeltmeleri

---

## Geliştirme Ortamı Kurulumu

```bash
# 1. Depoyu fork edin (GitHub'da "Fork" butonuna basın)

# 2. Fork'unuzu klonlayın
git clone https://github.com/KULLANICI_ADINIZ/finwise.git
cd finwise

# 3. Upstream remote'u ekleyin
git remote add upstream https://github.com/Sara-Toptamur36/finwise.git

# 4. Backend ortamını kurun
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

# 5. Frontend ortamını kurun
cd frontend && npm install && cd ..

# 6. Geliştirme sunucularını başlatın
# Terminal 1:
python -m uvicorn backend.main:app --reload --port 8000
# Terminal 2:
cd frontend && npm run dev
```

---

## Commit Mesajı Formatı

[Conventional Commits](https://www.conventionalcommits.org/) standardını kullanıyoruz:

```
<tür>(<kapsam>): <kısa açıklama>

[isteğe bağlı gövde]

[isteğe bağlı notlar]
```

### Tür Etiketleri

| Etiket | Kullanım |
|--------|---------|
| `feat` | Yeni özellik |
| `fix` | Hata düzeltmesi |
| `docs` | Dokümantasyon değişikliği |
| `style` | Kod biçimlendirme (mantık değişmez) |
| `refactor` | Yeniden yapılandırma |
| `perf` | Performans iyileştirmesi |
| `test` | Test ekleme/güncelleme |
| `chore` | Build, araç, yapılandırma |

### Örnekler

```bash
git commit -m "feat(analysis): kategori dağılımına pasta grafik eklendi"
git commit -m "fix(auth): şifre değiştirmede token doğrulaması düzeltildi"
git commit -m "docs(readme): kurulum adımları güncellendi"
git commit -m "style(frontend): SettingsPage düzen iyileştirmeleri"
```

---

## Pull Request Süreci

1. **Dal oluşturun**
   ```bash
   git checkout -b feat/ozellik-adi
   # veya
   git checkout -b fix/hata-ozeti
   ```

2. **Değişikliklerinizi yapın ve test edin**
   - Backend değişiklikler için: API'nin doğru çalıştığını `http://localhost:8000/docs` üzerinden doğrulayın
   - Frontend değişiklikler için: Tüm ilgili sayfaları tarayıcıda test edin

3. **Commit atın** (yukarıdaki format ile)

4. **Push edin**
   ```bash
   git push origin feat/ozellik-adi
   ```

5. **PR açın**
   - Başlık net ve kısa olsun
   - Neyi değiştirdiğinizi açıklayın
   - Varsa ekran görüntüsü ekleyin
   - İlgili issue'yu bağlayın: `Closes #42`

6. **İnceleme sürecini takip edin**
   - Yorumlara yanıt verin
   - İstenen değişiklikleri yapın

---

## Kod Standartları

### Python (Backend)

```python
# ✅ Doğru: Türkçe yorum, anlamlı değişken adı
def kullanici_sil(email: str) -> bool:
    """Kullanıcı kaydını kalıcı olarak siler."""
    users = _load_users()
    if email not in users:
        return False
    del users[email]
    _save_users(users)
    return True

# ❌ Yanlış: Tek harfli değişken, açıklama yok
def f(e):
    u = _load_users()
    del u[e]
    _save_users(u)
```

### React / JavaScript (Frontend)

```jsx
// ✅ Doğru: Bileşeni dosyanın üst düzeyinde tanımla
function KategoriKarti({ baslik, tutar, renk }) {
  return (
    <div className={`card ${renk}`}>
      <h3>{baslik}</h3>
      <p>{tutar}</p>
    </div>
  )
}

export default function AnalizSayfasi() {
  return <KategoriKarti baslik="Market" tutar="₺450" renk="bg-green-50" />
}

// ❌ Yanlış: Bileşeni fonksiyon içinde tanımlama (her render'da yeniden oluşur!)
export default function AnalizSayfasi() {
  const KategoriKarti = ({ baslik }) => <div>{baslik}</div>  // HATALI
  return <KategoriKarti baslik="Market" />
}
```

### Genel Kurallar

- **Yorum dili:** Türkçe veya İngilizce (tutarlı olun)
- **Değişken adları:** Anlamlı, `camelCase` (JS) / `snake_case` (Python)
- **Fonksiyon uzunluğu:** Tek sorumluluk ilkesi — bir fonksiyon bir iş yapar
- **Hata yönetimi:** try/catch kullanın, hataları yutmayın

---

Herhangi bir sorunuz olursa [Issues](https://github.com/Sara-Toptamur36/finwise/issues) üzerinden sormaktan çekinmeyin!

**Katkılarınız için şimdiden teşekkürler 💚**
