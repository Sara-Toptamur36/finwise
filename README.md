# 💰 FinWise — Yapay Zeka Destekli Kişisel Finans Analizi

> Banka ekstrelerinizi yükleyin, yapay zeka harcamalarınızı analiz etsin.

FinWise, CSV veya Excel formatındaki banka ekstrelerinizi analiz eden, kategori sınıflandırması yapan, gelecek ay harcamanızı tahmin eden ve PDF rapor oluşturan kişisel finans asistanıdır.

---

## ✨ Özellikler

| Özellik | Açıklama |
|---|---|
| 📊 **Kategori Analizi** | TF-IDF + SVM ile işlem açıklamalarını otomatik sınıflandırır |
| 🔮 **Harcama Tahmini** | LightGBM + SHAP ile gelecek ay tahmini ve açıklama |
| 🎯 **Karar Desteği** | XGBoost ile Tasarruf Et / Yatırım Yap / Beklet önerisi |
| 🎭 **Senaryo Testi** | "X kadar daha harcasam ne olur?" sorusuna yanıt |
| 📄 **PDF Rapor** | Grafikli, görsel analiz raporu (kategori, trend, AI kararı) |
| 📜 **Rapor Geçmişi** | Geçmiş analizlere dilediğiniz zaman erişin |
| 🔐 **Güvenli Hesap** | SHA-256 şifreleme, JWT token, şifre değiştirme |
| 🎭 **Demo Modu** | Kayıt olmadan 3 hazır profille uygulamayı deneyin |

---

## 🛠️ Teknoloji Yığını

**Frontend**
- React 18 + Vite + Tailwind CSS
- Recharts (grafikler)
- React Router v6

**Backend**
- FastAPI (Python 3.13) + Uvicorn
- Pandas + OpenPyXL (veri işleme)
- ReportLab + Matplotlib (PDF oluşturma)

**Makine Öğrenmesi**
- Stage 1: TF-IDF + SVM — Kategori sınıflandırması
- Stage 2: K-Means + Isolation Forest — Kullanıcı profili & anomali
- Stage 3: LightGBM + SHAP — Harcama tahmini
- Stage 4: XGBoost — Eylem önerisi (Coach)

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.10 veya üzeri
- Node.js 18 veya üzeri

### 1. Projeyi İndir

```bash
git clone https://github.com/Sara-Toptamur36/finwise.git
cd finwise
```

### 2. Backend

```bash
# Bağımlılıkları kur
pip install -r backend/requirements.txt

# Sunucuyu başlat (proje kök dizininden)
python -m uvicorn backend.main:app --reload --port 8000
```

Backend çalışıyor: `http://localhost:8000`
API Dokümantasyonu: `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend

# Bağımlılıkları kur (ilk seferinde)
npm install

# Geliştirme sunucusunu başlat
npm run dev
```

Uygulama açık: `http://localhost:5173`

> **Not:** Backend ve frontend'i aynı anda iki ayrı terminalde çalıştırın.

---

## 📁 Proje Yapısı

```
finwise/
│
├── backend/                        # FastAPI backend
│   ├── main.py                     # Uygulama giriş noktası
│   ├── requirements.txt            # Python bağımlılıkları
│   ├── routers/
│   │   ├── auth.py                 # Kayıt / Giriş / Şifre değiştirme
│   │   ├── analysis.py             # Dosya yükleme, analiz, geçmiş
│   │   ├── reports.py              # PDF rapor oluşturma
│   │   ├── scenario.py             # Senaryo simülasyonu
│   │   └── demo.py                 # Demo profil verileri
│   └── services/
│       └── pipeline_service.py     # ML pipeline entegrasyonu
│
├── frontend/                       # React + Vite frontend
│   └── src/
│       ├── pages/
│       │   ├── LandingPage.jsx     # Ana sayfa
│       │   ├── Dashboard.jsx       # Gösterge paneli
│       │   ├── AnalyzePage.jsx     # Analiz & sonuçlar
│       │   ├── ScenarioPage.jsx    # Senaryo testi
│       │   ├── ReportsPage.jsx     # Rapor geçmişi
│       │   ├── SettingsPage.jsx    # Ayarlar
│       │   ├── LoginPage.jsx       # Giriş
│       │   └── RegisterPage.jsx    # Kayıt
│       ├── components/
│       │   ├── Layout.jsx          # Sayfa iskeleti
│       │   ├── PasswordInput.jsx   # Şifre göster/gizle input
│       │   └── Logo.jsx            # FinWise logo
│       ├── context/
│       │   └── AuthContext.jsx     # Global auth & analiz state
│       └── hooks/
│           └── useSettings.js      # localStorage ayar yönetimi
│
├── bank_ai_pipeline.py             # 4 aşamalı ana ML pipeline
├── rules_engine.py                 # Kural tabanlı karar motoru
├── kvkk_masker.py                  # Kişisel veri maskeleme (KVKK)
├── demo_profiles.json              # Demo kullanıcı verileri
│
└── colab_training/                 # Model eğitim notebook'ları
    ├── 01_stage1_bert_classifier.ipynb
    ├── 02_stage2_unsupervised_ml.ipynb
    ├── 03_stage3_forecasting_shap.ipynb
    ├── 04_stage4_xgboost_coach.ipynb
    └── data/                       # Eğitim veri setleri
```

---

## 🤖 ML Pipeline Detayı

```
Excel/CSV Ekstresi
       │
       ▼
┌─────────────────────────────────┐
│  Stage 1 — Kategori Sınıflama   │  TF-IDF + SVM
│  "MIGROS" → Market & Gıda       │
└─────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  Stage 2 — Kullanıcı Profili    │  K-Means + Isolation Forest
│  Kümeleme + Anomali Tespiti     │
└─────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  Stage 3 — Harcama Tahmini      │  LightGBM + SHAP
│  Gelecek ay: ~₺X,XXX            │
└─────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  Stage 4 — Karar Desteği        │  XGBoost Coach
│  Öneri: Tasarruf Et / Yatırım   │
└─────────────────────────────────┘
       │
       ▼
  Dashboard + PDF Rapor
```

---

## 📊 API Endpoint'leri

| Endpoint | Method | Açıklama |
|---|---|---|
| `/api/auth/register` | POST | Yeni hesap oluştur |
| `/api/auth/login` | POST | Giriş yap |
| `/api/auth/change-password` | POST | Şifre değiştir (auth gerekli) |
| `/api/analysis/upload` | POST | Ekstreyi yükle ve analiz et |
| `/api/analysis/result` | GET | Son analiz sonucunu getir |
| `/api/analysis/history` | GET | Rapor geçmişini listele |
| `/api/analysis/result/{id}` | GET | Belirli raporu getir |
| `/api/scenario/test` | POST | Senaryo simülasyonu çalıştır |
| `/api/reports/pdf` | POST | PDF rapor oluştur ve indir |
| `/api/reports/excel` | POST | Excel raporu indir |
| `/api/demo/personas` | GET | Demo persona listesi |
| `/api/demo/analyze/{id}` | GET | Demo analiz sonucu |

---

## 🎭 Demo Modu

Kayıt olmadan 3 hazır profille uygulamayı test edin:

| Persona | Profil | Özellik |
|---|---|---|
| **Ahmet Bey** | Yüksek Borç Riski | HIGH_DEBT_RISK — tasarruf önerileri |
| **Ayşe Hanım** | Tasarrufçu | GREAT_SAVER — yatırım önerileri |
| **Zeynep Hanım** | Bütçeleme Gerekli | NEEDS_BUDGETING — harcama uyarıları |

---

## 📋 Desteklenen Veri Formatı

Minimum CSV/Excel yapısı:

```csv
tarih,aciklama,tutar
2026-06-01,MIGROS AS,-450.00
2026-06-05,MAAS ODEMESI,35000.00
2026-06-08,NETFLIX,-149.00
```

| Sütun | Açıklama | Format |
|---|---|---|
| `tarih` | İşlem tarihi | YYYY-MM-DD veya GG.AA.YYYY |
| `aciklama` | İşlem açıklaması | Serbest metin |
| `tutar` | Tutar (gider eksi, gelir artı) | Ondalıklı sayı |

---

## 🔒 Güvenlik

- Şifreler **SHA-256** ile hashlenerek saklanır
- API istekleri **Bearer Token** ile korunur
- Şifre sıfırlama e-posta doğrulaması gerektirir
- Kullanıcı verileri yerel sunucuda tutulur
- **KVKK** uyumlu veri maskeleme desteği (`kvkk_masker.py`)

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

---

<div align="center">
  <strong>FinWise</strong> — Paranızı daha iyi anlayın 💚
</div>
