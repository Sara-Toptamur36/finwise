<div align="center">

<img src="frontend/public/favicon.svg" width="80" alt="FinWise Logo" />

# FinWise

### Yapay Zeka Destekli Kişisel Finans Analizi

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=flat-square&logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind-3-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)
![LightGBM](https://img.shields.io/badge/LightGBM-ML-brightgreen?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-FFD21E?style=flat-square)](https://huggingface.co/datasets/Saraa34/finwise-egitim-verisi)

**Banka ekstrelerinizi yükleyin — yapay zeka harcamalarınızı anlasın, geleceğinizi tahmin etsin.**

[🚀 Hızlı Başlangıç](#-hızlı-başlangıç) · [✨ Özellikler](#-özellikler) · [🤖 ML Pipeline](#-ml-pipeline) · [📡 API](#-api-endpointleri) · [🤝 Katkı](#-katkıda-bulunma)

</div>

---

## 📖 Proje Nedir?

FinWise, CSV veya Excel formatındaki **banka ekstrelerinizi** analiz ederek size kapsamlı bir finansal tablo sunan kişisel finans asistanıdır. Makine öğrenmesi modellerini birbirine bağlayan 4 aşamalı bir AI pipeline'ı sayesinde:

- İşlemlerinizi **otomatik olarak kategorize eder** ("MIGROS" → Market & Gıda)
- Harcama alışkanlıklarınızdan **kişisel profilinizi** çıkarır
- **Gelecek ay tahmini** yapar ve tahmin nedenini açıklar
- "Tasarruf Et / Yatırım Yap / Beklet" şeklinde **eylem önerisi** sunar
- Tüm bunları **PDF rapora** dönüştürür

> Kayıt olmadan da 3 hazır demo profil ile uygulamayı keşfedebilirsiniz.

---

## ✨ Özellikler

| # | Özellik | Açıklama |
|---|---------|----------|
| 🏷️ | **Otomatik Kategorizasyon** | Turkish ELECTRA + TF-IDF/SVC ensemble ile 13 farklı harcama kategorisi |
| 👤 | **Harcama Profili** | K-Means kümeleme ile kişisel finansal profil |
| 📈 | **Gelecek Ay Tahmini** | LightGBM + SHAP ile tahmin ve açıklama |
| 🤖 | **AI Finansal Teşhis** | XGBoost ile Tasarruf Et / Yatırım Yap / Beklet |
| 💡 | **Açıklanabilir Karar** | "Neden bu sonuç?" sorusuna sade yanıt (SHAP) |
| 🔮 | **Senaryo Testi** | "X kadar daha harcasam ne olur?" simülasyonu |
| 📄 | **PDF Rapor** | Grafikli, görsel analiz raporu (kategori, trend, AI) |
| 📜 | **Rapor Geçmişi** | Önceki analizlere istediğiniz zaman erişin |
| 🎭 | **Demo Modu** | Kayıt gerekmez — 3 hazır profille hemen deneyin |
| 🔐 | **Güvenli Hesap** | SHA-256 şifre, Bearer token, güvenli şifre değiştirme |

---

## 🛠️ Teknoloji Yığını

### Backend (Çalışma Zamanı)
| Paket | Versiyon | Kullanım |
|-------|----------|---------|
| **FastAPI** | 0.111 | REST API çerçevesi |
| **Uvicorn** | 0.29 | ASGI web sunucusu |
| **Pandas** | 2.2 | Veri işleme |
| **OpenPyXL** | 3.1 | Excel okuma/yazma |
| **ReportLab** | 4.2 | PDF oluşturma |
| **Matplotlib** | — | PDF içi grafikler |
| **scikit-learn** | — | TF-IDF, Kalibre SVC, K-Means, Isolation Forest |
| **LightGBM** | — | Harcama tahmini (Stage 3) |
| **XGBoost** | — | Karar destek modeli (Stage 4) |
| **SHAP** | — | Model açıklanabilirliği |

### Model Eğitimi (Google Colab — GPU)
| Paket | Kullanım |
|-------|---------|
| **PyTorch** | ELECTRA model eğitimi |
| **Transformers (HuggingFace)** | `dbmdz/electra-small-turkish-cased-discriminator` |
| **Focal Loss** | Sınıf dengesizliği giderme (γ=2.0–3.0) |
| **scikit-learn** | TF-IDF + SVC, ensemble değerlendirme |

---

## 📦 Eğitim Veri Seti

Modellerin eğitildiği veri seti Hugging Face üzerinde **Gated Dataset** olarak yayınlanmıştır.
Sayfayı herkes görebilir, ancak dosyaları indirmek için erişim talep etmeniz gerekir.

[![Hugging Face Dataset](https://img.shields.io/badge/%F0%9F%A4%97%20Dataset-finwise--egitim--verisi-FFD21E?style=flat-square)](https://huggingface.co/datasets/Saraa34/finwise-egitim-verisi)

**İçerik:**
| Dosya | Açıklama | Kullanım |
|-------|----------|---------|
| `bankaverison.xlsx` | Etiketli gerçek banka işlemleri | Stage 1 eğitim |
| `YENİVERİTEST.xlsx` | Gerçek işlem test seti | Stage 1 test |
| `bert_training_data.csv` | ELECTRA eğitim verisi | Stage 1 eğitim |
| `enhanced_synthetic_bank_data.csv` | Zengin sentetik işlemler (29 MB) | Stage 1 eğitim |
| `synthetic_budget_data.csv` | Sentetik bütçe verisi | Stage 1 eğitim |
| `ultimate_synthetic_bank_data.csv` | Nihai sentetik işlemler | Stage 2 eğitim |
| `stage2_user_monthly_features.csv` | Kullanıcı aylık özellik matrisi | Stage 2 eğitim |
| `stage4_coached_users.csv` | Karar etiketi verisi | Stage 4 eğitim |

> Erişim için: [Request Access](https://huggingface.co/datasets/Saraa34/finwise-egitim-verisi)

### Frontend
| Paket | Versiyon | Kullanım |
|-------|----------|---------|
| **React** | 18 | UI kütüphanesi |
| **Vite** | 5 | Build aracı |
| **Tailwind CSS** | 3 | Stil çerçevesi |
| **Recharts** | 2.12 | Grafikler |
| **React Router** | 6 | Sayfa yönlendirme |
| **Axios** | 1.6 | HTTP istemcisi |

---

## 🏗️ Proje Yapısı

```
finwise/
│
├── 📂 backend/                        # FastAPI backend
│   ├── main.py                        # Uygulama giriş noktası & CORS
│   ├── requirements.txt               # Python bağımlılıkları
│   │
│   ├── 📂 routers/
│   │   ├── auth.py                    # Kayıt · Giriş · Şifre değiştirme
│   │   ├── analysis.py                # Dosya yükleme · Analiz · Geçmiş
│   │   ├── reports.py                 # PDF & Excel rapor oluşturma
│   │   ├── scenario.py                # Senaryo simülasyonu
│   │   └── demo.py                    # Demo profil verileri
│   │
│   └── 📂 services/
│       └── pipeline_service.py        # ML pipeline → API köprüsü
│
├── 📂 frontend/                       # React + Vite frontend
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   │
│   └── 📂 src/
│       ├── 📂 pages/
│       │   ├── LandingPage.jsx        # Ana / karşılama sayfası
│       │   ├── Dashboard.jsx          # Gösterge paneli
│       │   ├── AnalyzePage.jsx        # Analiz sonuçları & sekmeler
│       │   ├── ScenarioPage.jsx       # "Ya şöyle olsaydı?" testi
│       │   ├── ReportsPage.jsx        # Rapor geçmişi
│       │   ├── SettingsPage.jsx       # Hesap & model ayarları
│       │   ├── LoginPage.jsx          # Giriş
│       │   └── RegisterPage.jsx       # Kayıt
│       │
│       ├── 📂 components/
│       │   ├── Layout.jsx             # Sayfa iskeleti (sidebar + header)
│       │   ├── Sidebar.jsx            # Navigasyon menüsü
│       │   ├── Header.jsx             # Üst bar
│       │   ├── Logo.jsx               # FinWise SVG logosu
│       │   └── PasswordInput.jsx      # Şifre göster/gizle bileşeni
│       │
│       ├── 📂 context/
│       │   └── AuthContext.jsx        # Global auth & analiz state
│       │
│       └── 📂 hooks/
│           └── useSettings.js         # localStorage model ayarları
│
├── 🤖 bank_ai_pipeline.py             # 4 aşamalı ana ML pipeline
├── ⚙️  rules_engine.py                # Kural tabanlı karar motoru
├── 🔒 kvkk_masker.py                  # Kişisel veri maskeleme (KVKK)
├── 👥 demo_profiles.json              # 3 demo kullanıcı profili
│
└── 📂 colab_training/                 # Model eğitim kaynakları
    ├── 01_stage1_bert_classifier.ipynb   # Kategori sınıflandırma eğitimi
    ├── 02_stage2_unsupervised_ml.ipynb   # Kümeleme & anomali eğitimi
    ├── 03_stage3_forecasting_shap.ipynb  # LightGBM tahmin eğitimi
    ├── 04_stage4_xgboost_coach.ipynb     # XGBoost karar eğitimi
    └── 📂 data/                          # Eğitim veri setleri
```

---

## 🤖 ML Pipeline

FinWise, yüklenen her ekstreyi 4 aşamalı bir AI zincirinden geçirir:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Kullanıcı Ekstresi                          │
│                  (CSV / Excel dosyası)                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  AŞAMA 1 — Kategori Sınıflandırması  (Ensemble v16)            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Katman A — Kural Motoru (rules_engine.py)              │   │
│  │  50+ regex kural → kesin eşleşme → doğrudan kategori   │   │
│  │  "ATM" → NAKİT, "NETFLIX" → EGLENCE, "EFT" → VİRMAN   │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         │  Kural eşleşmezse ↓                  │
│  ┌──────────────────────┴──────────────────────────────────┐   │
│  │  Katman B — Turkish ELECTRA (Colab GPU eğitimi)         │   │
│  │  dbmdz/electra-small-turkish-cased-discriminator        │   │
│  │  Faz 1: Sentetik veri (60K örnek, Focal Loss γ=2)       │   │
│  │  Faz 2: Gerçek banka verisi (layer-wise LR, early stop) │   │
│  │  Test F1: 0.9121                                        │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         │  ↕ α-ağırlıklı birleşim              │
│  ┌──────────────────────┴──────────────────────────────────┐   │
│  │  Katman C — TF-IDF + Kalibre SVC (Çalışma Zamanı)      │   │
│  │  Word n-gram (80K özellik) + Char n-gram (40K özellik)  │   │
│  │  Tiered oversampling + Confidence threshold             │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         │                                       │
│  Ensemble (B×(1-α) + C×α) → Makro F1 = 0.9369                 │
│                                                                 │
│  "MIGROS AŞ"        →  🛒 Market & Gıda                        │
│  "NETFLIX"          →  🎬 Eğlence                              │
│  "TRENDYOLYEM"      →  🍔 Yeme & İçme                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  AŞAMA 2 — Kullanıcı Profili & Anomali Tespiti                  │
│                                                                 │
│  K-Means Kümeleme  →  Harcama tipi profili                      │
│  Isolation Forest  →  Anormal işlem tespiti                     │
│                                                                 │
│  Çıktı: Tasarrufçu / Bütçeci / Risk Altında / Dengeli          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  AŞAMA 3 — Gelecek Ay Tahmini                                   │
│                                                                 │
│  LightGBM regresyon  →  Tahmini aylık gider                     │
│  SHAP değerleri      →  "Neden bu tahmin?" açıklaması           │
│                                                                 │
│  Çıktı: ₺X,XXX  —  "Fatura harcamanız artış gösterdi..."       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  AŞAMA 4 — Finansal Karar Desteği                               │
│                                                                 │
│  XGBoost sınıflandırıcı  →  Eylem önerisi                       │
│                                                                 │
│  🟢 Tasarruf Et   —  Birikim için uygun ortam                   │
│  🔵 Yatırım Yap   —  Sermaye büyütme fırsatı                    │
│  🟡 Beklet        —  Dengeli yaklaş, beklet                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
                 Dashboard + PDF Rapor
```

### Desteklenen Kategoriler (13 adet)

`ALISVERIS` · `BANKA_KESINTISI` · `DIGER` · `EGITIM` · `EGLENCE` · `FATURA` · `MARKET` · `NAKIT_ISLEMLERI` · `SAGLIK` · `SEYAHAT` · `ULASIM` · `VIRMAN` · `YEME_ICME`

---

## 🚀 Hızlı Başlangıç

### Ön Koşullar

Kurulu olması gereken araçlar:

| Araç | Minimum Versiyon | Kontrol |
|------|-----------------|---------|
| Python | 3.10 | `python --version` |
| pip | 23+ | `pip --version` |
| Node.js | 18 | `node --version` |
| npm | 9+ | `npm --version` |

### 1. Depoyu İndir

```bash
git clone https://github.com/Sara-Toptamur36/finwise.git
cd finwise
```

### 2. Backend Kurulumu

```bash
# Sanal ortam oluştur (önerilir)
python -m venv .venv

# Etkinleştir
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# Bağımlılıkları kur
pip install -r backend/requirements.txt
```

#### Eğitilmiş Modelleri Kur

Pipeline'ın çalışması için `colab_training/outputs/` klasöründe eğitilmiş modeller (`.pkl` dosyaları) olmalıdır. İki seçeneğiniz var:

**A) Google Colab'da Eğit** — `colab_training/` klasöründeki notebook'ları sırasıyla çalıştırın:
```
01 → 02 → 03 → 04
```

**B) Demo Modunu Kullan** — Model olmadan da uygulama çalışır; sadece demo analizi yapar.

### 3. Backend'i Başlat

```bash
# Proje kök dizininden çalıştırın
python -m uvicorn backend.main:app --reload --port 8000
```

✅ API: `http://localhost:8000`
📚 Swagger Docs: `http://localhost:8000/docs`

### 4. Frontend Kurulumu

```bash
cd frontend
npm install
npm run dev
```

✅ Uygulama: `http://localhost:5173`

### 5. Yapılandırma

İlk çalıştırmada `backend/users.json` otomatik oluşturulur. Örnek yapı için:
```bash
cp backend/users.json.example backend/users.json
```

---

## 📋 Desteklenen Veri Formatı

### Minimum CSV Yapısı

```csv
tarih,aciklama,tutar
2026-06-01,MIGROS AS,-450.00
2026-06-05,MAAS ODEMESI,35000.00
2026-06-08,NETFLIX ABONELIK,-149.00
2026-06-10,BIM MARKET,-380.50
2026-06-15,AKARYAKIT,-650.00
```

### Sütun Açıklamaları

| Sütun | Açıklama | Format | Zorunlu |
|-------|----------|--------|---------|
| `tarih` | İşlem tarihi | `YYYY-MM-DD` veya `GG.AA.YYYY` | ✅ |
| `aciklama` | İşlem açıklaması (banka metni) | Serbest metin | ✅ |
| `tutar` | Tutar (gider için negatif, gelir için pozitif) | Ondalıklı sayı | ✅ |

> **İpucu:** Çoğu Türk bankasının internet şubesinden CSV veya Excel formatında ekstre indirilebilir. Sütun adları Türkçe veya İngilizce olabilir; sistem otomatik tanır.

---

## 📡 API Endpointleri

Tam API dokümantasyonu için: `http://localhost:8000/docs`

### Kimlik Doğrulama

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `POST /api/auth/register` | — | Yeni hesap oluştur |
| `POST /api/auth/login` | — | Giriş yap, token al |
| `POST /api/auth/change-password` | 🔒 Auth | Şifre değiştir |
| `GET  /api/auth/me` | 🔒 Auth | Oturum bilgisi |

### Analiz

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `POST /api/analysis/upload` | 🔒 Auth | Ekstreyi yükle ve analiz et |
| `GET  /api/analysis/result` | 🔒 Auth | Son analiz sonucunu getir |
| `GET  /api/analysis/history` | 🔒 Auth | Rapor geçmişini listele |
| `GET  /api/analysis/result/{id}` | 🔒 Auth | Belirli raporu getir |
| `DELETE /api/analysis/data` | 🔒 Auth | Analiz verisi sil |
| `DELETE /api/analysis/reports` | 🔒 Auth | Rapor geçmişi temizle |

### Raporlar

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `POST /api/reports/pdf` | 🔒 Auth | PDF rapor oluştur ve indir |
| `POST /api/reports/excel` | 🔒 Auth | Excel raporu indir |

### Senaryo & Demo

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `POST /api/scenario/test` | — | Senaryo simülasyonu çalıştır |
| `GET  /api/demo/personas` | — | Demo persona listesi |
| `GET  /api/demo/analyze/{id}` | — | Demo analiz sonucu |

> 🔒 **Auth:** İstek header'ında `Authorization: Bearer <token>` gerektirir.

---

## 🎭 Demo Modu

Kayıt olmadan 3 farklı kullanıcı profiliyle uygulamayı test edin:

| Persona | Finansal Profil | Özellik |
|---------|----------------|---------|
| 👨 **Ahmet Bey** | Yüksek Borç Riski | Giderleri gelirini aşıyor, acil önlem önerileri |
| 👩 **Ayşe Hanım** | Mükemmel Tasarrufçu | Düzenli birikim, yatırım fırsatları |
| 👩 **Zeynep Hanım** | Bütçeleme Gerekli | Dengesiz harcama dağılımı, kategori uyarıları |

---

## 🔒 Güvenlik

- Şifreler **SHA-256** ile hashlenerek saklanır, düz metin hiçbir zaman tutulmaz
- API istekleri **UUID Bearer token** ile korunur
- Şifre sıfırlama **e-posta doğrulaması** gerektirir (e-posta altyapısı olmadan devre dışı)
- Şifre değiştirme **mevcut şifre doğrulaması** yapılarak gerçekleştirilir
- Kullanıcı verileri yalnızca **yerel sunucuda** tutulur, üçüncü taraflarla paylaşılmaz
- **KVKK** uyumlu kişisel veri maskeleme (`kvkk_masker.py`)
- `users.json` ve `reports_store.json` `.gitignore` ile versiyon kontrolü dışında

---

## 🧪 Geliştirme

### Kod Yapısı Kuralları

```
backend/routers/   → Her kaynak için ayrı router dosyası
backend/services/  → İş mantığı, ML bağlantısı
frontend/pages/    → Her sayfa bir dosya, bileşen dışarıda tanımlanır*
frontend/components/ → Paylaşılan UI bileşenleri
```

> \* **Önemli React Kuralı:** Bileşenleri her zaman parent bileşenin **dışında** tanımlayın. Bileşeni içeride tanımlamak her render'da yeniden oluşturulmasına, focus kaybına ve gereksiz unmount/remount'a neden olur.

### Ortam Değişkenleri

Şu an uygulama yapılandırması için ortam değişkeni kullanılmamaktadır. İleride eklemek için `backend/.env.example` dosyasını referans alın:

```env
# Backend yapılandırma (örnek)
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./finwise.db
CORS_ORIGINS=http://localhost:5173
```

### Sık Kullanılan Komutlar

```bash
# Backend — geliştirme modunda başlat
python -m uvicorn backend.main:app --reload --port 8000

# Frontend — geliştirme sunucusu
cd frontend && npm run dev

# Frontend — prodüksiyon build
cd frontend && npm run build

# API dokümantasyonu
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Detaylar için [CONTRIBUTING.md](CONTRIBUTING.md) dosyasına bakın.

**Kısaca:**

1. Depoyu fork edin
2. Özellik dalı oluşturun: `git checkout -b ozellik/yeni-ozellik`
3. Değişikliklerinizi commit edin: `git commit -m 'feat: yeni özellik ekle'`
4. Dalı push edin: `git push origin ozellik/yeni-ozellik`
5. Pull Request açın

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında dağıtılmaktadır. Detaylar için `LICENSE` dosyasına bakın.

---

## 👤 Geliştirici

**Sara Toptamur**

- GitHub: [@Sara-Toptamur36](https://github.com/Sara-Toptamur36)

---

<div align="center">

**⭐ Beğendiyseniz yıldız vermeyi unutmayın!**

*FinWise — Paranızı daha iyi anlayın* 💚

</div>
