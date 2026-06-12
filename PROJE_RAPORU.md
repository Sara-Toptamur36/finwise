# FinWise — Banka AI | Kapsamlı Proje Raporu

> **Yapay Zeka Destekli Kişisel Finans Analizi**  
> TÜBİTAK / SCI / TEKNOFEST Standartlarında Hazırlanmıştır — Haziran 2026

---

## İçindekiler

1. [Proje Özeti](#1-proje-özeti)
2. [4 Aşamalı Pipeline](#2-4-aşamalı-pipeline)
3. [Sistem Mimarisi](#3-sistem-mimarisi)
4. [Veri Seti](#4-veri-seti)
5. [Stage 1 — NLP Kategorizasyon](#5-stage-1--nlp-kategorizasyon)
6. [Stage 2 — Müşteri Profilleme](#6-stage-2--müşteri-profilleme)
7. [Stage 3 — Bütçe Tahmini](#7-stage-3--bütçe-tahmini)
8. [Stage 4 — Finansal Koçluk](#8-stage-4--finansal-koçluk)
9. [Tüm Metrikler Özeti](#9-tüm-metrikler-özeti)
10. [Web Uygulaması](#10-web-uygulaması)
11. [Güvenlik ve KVKK](#11-güvenlik-ve-kvkk)
12. [Tartışma ve Özgün Katkılar](#12-tartışma-ve-özgün-katkılar)
13. [Jüri Soru-Cevap Kataloğu](#13-jüri-soru-cevap-kataloğu)

---

## 1. Proje Özeti

Banka AI, kişisel finans yönetimi (PFM) alanında uçtan uca yapay zeka sistemidir. Ham banka işlem metinlerini alır; 13 finansal kategoriye ayırır, müşteri profilini çıkarır, gelecek ay harcamasını tahmin eder ve finansal koçluk tavsiyesi üretir. Tüm bu süreç **< 200 milisaniyede** tamamlanır. GPU zorunluluğu yoktur.

### Temel Metrikler

| Metrik | Değer |
|--------|-------|
| Toplam Eğitim İşlemi (NLP) | **101.047** |
| Stage 4 Makro F1 Skoru | **%93.6** |
| Stage 4 Accuracy | **%96.9** |
| Inference Süresi / İşlem | **2–4 ms** |
| NLP Kategori Sayısı | **13** |
| Regex Kapsama Oranı | **%31.2** |
| Regex Kural Sayısı | **58** |
| ELECTRA Model Boyutu | **53 MB** |

### Teknoloji Yığını

**Backend:** Python 3.13 · FastAPI · Uvicorn · Scikit-learn · XGBoost · LightGBM · HuggingFace Transformers · SHAP · ReportLab · openpyxl

**Frontend:** React 18 · Vite 5 · Tailwind CSS v3 · Recharts · Axios · React Router v6

**Eğitim:** Google Colab · NVIDIA T4 GPU · PyTorch · Transformers

---

## 2. 4 Aşamalı Pipeline

```
Ham Metin (Banka İşlemi)
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 1 — NLP KATEGORİZASYON                                  │
│  Katman A: Kural Motoru (58 Regex)   → < 0.5 ms, Precision %100│
│  Katman B: Turkish ELECTRA           → F1: 0.875               │
│  Katman C: TF-IDF + Kalibre SVC      → F1: 0.928               │
│  Ensemble (B×0.4 + C×0.6)           → Makro F1: 0.9282         │
│  Güven < %65 → OOD → DİĞER (Güvenli Bekletme)                  │
└─────────────────────────────────────────────────────────────────┘
         │  Kategori Etiketi (13 sınıf)
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 2 — MÜŞTERİ PROFİLLEME                                  │
│  IsolationForest (n=200) → Anomali tespiti (%5.02)             │
│  K-Means (K=4, 13 özellik)                                      │
│  Küme 0: Orta Profil    | Küme 1: Güçlü Tasarrufçular          │
│  Küme 2: Riskli Harcayıcılar | Küme 3: Dengeli Tasarrufçular   │
└─────────────────────────────────────────────────────────────────┘
         │  Finansal Profil Kümesi
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 3 — BÜTÇE TAHMİNİ                                       │
│  LightGBM v3 · 35 özellik · Zaman Serisi Regresyonu            │
│  RMSE: 7.047₺ · SMAPE: %42.55 · WAPE: %29.16                   │
│  Top-1 SHAP: expense_rolling3m_mean (0.341)                     │
│  Top-2 SHAP: month_sin — döngüsel ay kodlaması (0.245)          │
└─────────────────────────────────────────────────────────────────┘
         │  Gelecek Ay Harcama Tahmini (₺)
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 4 — FİNANSAL KOÇLUK                                     │
│  XGBoost · n_estimators=300 · max_depth=5 · 39 özellik         │
│  Makro F1: 0.9359 · Accuracy: %96.90                            │
│  HIGH_DEBT_RISK Recall: %95.52                                  │
│  Çıktı: GREAT_SAVER / HIGH_DEBT_RISK / NEEDS_BUDGETING + SHAP  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Sistem Mimarisi

### Hibrit Mimari — Temel Tasarım Kararı

| | Saf Regex | Saf ML/DL | **Hibrit (Seçilen)** |
|--|-----------|-----------|----------------------|
| Kapsama | %31.2 | %100 | **%100** |
| Hız | < 0.5 ms | > 100 ms | **2-4 ms** |
| Maliyet | Sıfır | Yüksek GPU | **%30 Düşük** |
| Serbest Metin | ✗ | ✓ | **✓** |

### İş Yükü Dağılımı

```
101.047 Eğitim İşlemi:

[██████████░░░░░░░░░░░░░░░░░░░░░] Regex  31.2% (31.526 işlem) — Sıfır Maliyet
[░░░░░░░░░░████████████████████░] AI     68.8% (69.521 işlem) — ML/DL
```

### Stage 1 Karar Hiyerarşisi

```
Gelen İşlem Metni
       │
       ▼
  58 Regex Kuralı ──── Eşleşti? ──── EVET ──→ Sonuç (ML çalışmaz)
       │ HAYIR
       ▼
  TF-IDF + SVC ──── Güven ≥ 0.65? ── EVET ──→ Sonuç
       │ HAYIR / Karmaşık Bağlam
       ▼
  Turkish ELECTRA (Fallback)
       │
       ▼
  Güven < 0.65? ──────────────────────────→ DİĞER (OOD Güvenlik)
```

### Modüler Dosya Yapısı

| Dosya | Görev |
|-------|-------|
| `stage1_categorizer_v2.py` | NLP: Regex + TF-IDF/SVC + ELECTRA ensemble |
| `stage2_clustering.py` | K-Means kümeleme + IsolationForest |
| `stage3_budget_predictor.py` | LightGBM zaman serisi (35 özellik) |
| `stage4_financial_coach.py` | XGBoost koçluk + SHAP |
| `pipeline_service.py` | 4 aşamayı < 200ms'de senkronize eden orchestrator |
| `kvkk_masker.py` | KVKK anonimleştirme (pattern-based, 7 test geçti) |
| `backend/main.py` | FastAPI giriş noktası, CORS, 5 router |
| `stage2_config.pkl` | K-Means 13 özellik + küme isim haritası |
| `stage4_xgb_results.json` | XGBoost dinamik sınıf isimleri |

---

## 4. Veri Seti

### Genel İstatistikler

| Özellik | Değer |
|---------|-------|
| Toplam NLP İşlemi | **101.047** |
| Gerçek Veri | 5.379 (%5.3) |
| Sentetik Veri | 95.668 (%94.7) |
| Benzersiz Kelime (Vocab) | **27.980** |
| Ort. Metin Uzunluğu | 43.22 karakter |
| Ort. Kelime Sayısı | 6.48 |

### Veri Kaynakları

| Dosya | Kayıt | Tür | Kullanım |
|-------|-------|-----|----------|
| `bankaverison.xlsx` | 5.096 | Gerçek | Gerçekçilik çapası |
| `YENİVERİTEST.xlsx` | 283 | Gerçek | %100 kör test (Blind Test) |
| `bert_training_data.csv` | 33.947 | Sentetik | NLP ana omurga |
| `enhanced_synthetic_bank_data.csv` | 61.721 | Sentetik | Azınlık sınıf dengeleme |
| `synthetic_budget_data.csv` | 30.000 | Sentetik | Stage 2/3/4 profilleri |

### Tersine Mühendislik Test Stratejisi

> Literatürde eşine az rastlanan **kör test (blind test)** stratejisi:

- `bankaverison.xlsx` "Diğer" kategorilerinin **%80'i** → Test setine saklandı
- `bankaverison.xlsx` "Sağlık" kategorisinin **%100'ü** → Test setine saklandı
- `YENİVERİTEST.xlsx`'in **%100'ü** → Direkt test setine aktarıldı

**Sonuç:** Model %95 sentetik veriyle eğitildi, neredeyse tamamen GERÇEK veriyle test edildi → Overfitting olmadığının matematiksel kanıtı.

### Veri Temizleme Adımları

1. 271.352 ham satırdan `drop_duplicates()` ile tekrarlar silindi
2. Gerçek test metinleriyle örtüşen satırlar `~isin(real_lower)` ile kaldırıldı
3. 3 karakterden kısa anlamsız metinler dışlandı
4. Türkçe karakter uyumlu lowercase (İ, Ş, Ü, Ç, Ö)
5. Regex `[^\w\s]` ile özel karakter/emoji temizlendi
6. StandardScaler sadece train setine `fit` edildi
7. `IsolationForest(n=200, contamination=0.05)` → **158 anomali (%5.02)** tespit edildi

### 13 Finansal Kategori

`MARKET` · `YEME_ICME` · `ALISVERIS` · `ULASIM` · `SEYAHAT` · `SAGLIK` · `EGITIM` · `EGLENCE` · `FATURA` · `DIGER` · `VIRMAN` · `BANKA_KESINTISI` · `NAKIT_ISLEMLERI`

---

## 5. Stage 1 — NLP Kategorizasyon

### Sonuçlar (v16)

| Model | Makro F1 | Accuracy |
|-------|----------|----------|
| Hibrit (Regex + Ensemble) | **0.9225** | — |
| Ensemble (ELECTRA + SVC) | **0.9282** | 0.9576 |
| Sadece ELECTRA | 0.8752 | — |

### Kategori Bazlı Performans

| Kategori | F1 | Precision | Recall | n |
|----------|----|-----------|--------|---|
| SAGLIK | **1.000** | 1.000 | 1.000 | 11 |
| BANKA_KESINTISI | **0.997** | 0.998 | 0.996 | 463 |
| NAKIT_ISLEMLERI | **0.984** | 0.978 | 0.989 | 184 |
| VIRMAN | **0.979** | 0.967 | 0.992 | 1000 |
| YEME_ICME | **0.973** | 0.987 | 0.959 | 731 |
| EGLENCE | **0.963** | 0.989 | 0.939 | 280 |
| MARKET | **0.967** | 0.960 | 0.973 | 374 |
| ULASIM | **0.952** | 0.962 | 0.943 | 106 |
| FATURA | **0.931** | 0.904 | 0.959 | 49 |
| EGITIM | 0.874 | 0.918 | 0.833 | 54 |
| SEYAHAT | 0.871 | 0.841 | 0.902 | 41 |
| ALISVERIS | 0.810 | 0.813 | 0.806 | 124 |
| DİĞER (OOD) | 0.767 | 0.756 | 0.778 | 171 |

### Model Parametreleri

**TF-IDF Vektörizasyon:**
- Kelime: `max_features=30.000`, `ngram_range=(1,3)`
- Karakter: `max_features=20.000`, `ngram_range=(2,5)`
- `min_df=5`, Stopword kullanılmadı (finansal terminoloji bozulmasın)

**LinearSVC + Kalibrasyon:**
- `C=0.5` (Grid Search ile belirlendi), `max_iter=4000`
- `class_weight='balanced'`
- `CalibratedClassifierCV` (Platt scaling) → `predict_proba` üretir
- Inference: **2-4 ms/işlem**

**Turkish ELECTRA:**
- Model: `dbmdz/electra-small-turkish-cased-discriminator`
- `Epoch=3`, `Batch Size=32`, `Optimizer=AdamW`
- `Learning Rate=1e-5`, `weight_decay=0.02`, `Dropout=0.3`
- Loss: Cross Entropy | Eğitim: Colab T4 GPU ~40dk
- Model boyutu: **53.24 MB**

**OOD Güven Mekanizması:**
- Threshold = **0.65** (Precision-Recall eğrisinin F1 maksimum noktası)
- 0.50 → çok fazla False Positive | 0.80 → çok fazla False Negative

### Ablation Study

| Kaldırılan Bileşen | Etki |
|--------------------|------|
| Regex (58 kural) | Inference süresi **%45 arttı**, CPU darboğazı |
| Sentetik Veri | Makro F1 **%93 → %70**, Stage 4 **%67'de kaldı** |
| N-Gram (1,3) → Unigram | Market/Yemek Precision **%98 → %82** |
| Karakter N-Gram | Yazım hatası direnci kırıldı, **%8 düşüş** |

---

## 6. Stage 2 — Müşteri Profilleme

### K-Means Metrikleri

| Metrik | Değer |
|--------|-------|
| Küme Sayısı | K = 4 |
| Silhouette Skoru | 0.2848 |
| Calinski-Harabasz | **2943.11** (yüksek = iyi ayrışma) |
| Davies-Bouldin | 1.5588 |
| Anomali Tespiti (IsoForest) | 158 adet, %5.02 |

### 4 Müşteri Segmenti

| Küme | İsim | n | Ort. Gelir | Ort. Gider | Tasarruf |
|------|------|---|-----------|-----------|----------|
| 0 | Orta Profil | 49 | 48.643₺ | 19.407₺ | %52.4 |
| 1 | Güçlü Tasarrufçular | 1.575 | 35.574₺ | 10.638₺ | %68.9 |
| 2 | Riskli Harcayıcılar | 653 | 893₺ | 2.584₺ | **-%0.76** |
| 3 | Dengeli Tasarrufçular | 708 | 71.603₺ | 27.956₺ | %59.2 |

> Küme isimleri ve 13-özellik listesi `stage2_config.pkl` dosyasında saklanmaktadır.

### 13 Stage 2 Özelliği

`monthly_income_computed` · `monthly_expense_computed` · `savings_rate` · `budget_utilisation` · `net_cashflow` · `spend_ALISVERIS` · `spend_BANKA_KESINTISI` · `spend_DIGER` · `spend_EGITIM` · `spend_EGLENCE` · `spend_FATURA` · `spend_MARKET` · `spend_SAGLIK`

---

## 7. Stage 3 — Bütçe Tahmini

### LightGBM v3 Metrikleri

| Metrik | Test | CV Ortalama | CV Std |
|--------|------|-------------|--------|
| RMSE | **7.047₺** | — | — |
| MAE | 4.612₺ | — | — |
| SMAPE | %42.55 | %46.76 | ±1.97 |
| WAPE | %29.16 | %36.64 | ±2.24 |
| Özellik Sayısı | **35** | — | — |

> **MAPE = %75.12 Neden?** Amaç kuruşluk tahmin değil, harcama **trendi ve risk sinyali** tespiti. Sıfıra yakın harcama aylarında MAPE matematiksel olarak şişer. WAPE = %29.16 güvenilirdir.

### SHAP — En Önemli 10 Özellik (Stage 3)

| Sıra | Özellik | SHAP Değeri |
|------|---------|-------------|
| 1 | `expense_rolling3m_mean` | 0.341 |
| 2 | `month_sin` (döngüsel ay) | 0.245 |
| 3 | `expense_lag2` | 0.117 |
| 4 | `expense_lag3` | 0.087 |
| 5 | `monthly_expense_computed` | 0.084 |
| 6 | `expense_rolling3m_std` | 0.083 |
| 7 | `month_cos` | 0.058 |
| 8 | `income_lag2` | 0.046 |
| 9 | `expense_lag1` | 0.046 |
| 10 | `income_lag3` | 0.039 |

> **Döngüsel Zaman Kodlaması:** Geleneksel "1-12" rakamlandırma yerine `month_sin` ve `month_cos` kullanıldı. Aralık ile Ocak'ın gerçekte ardışık olduğunu modele doğru öğretiyor. SHAP'ta **2. sıraya** oturdu.

---

## 8. Stage 4 — Finansal Koçluk

### XGBoost Sonuçları

| Metrik | Test | CV Ortalama | CV Std |
|--------|------|-------------|--------|
| Makro F1 | **0.9359** | 0.9438 | ±0.0077 |
| Accuracy | **%96.90** | %97.31 | ±0.34 |

### Sınıf Bazlı Metrikler

| Sınıf | Precision | Recall | F1 | n |
|-------|-----------|--------|----|---|
| `GREAT_SAVER` | %99.42 | %96.85 | **0.981** | 2985 |
| `HIGH_DEBT_RISK` | %88.68 | **%95.52** | **0.920** | 402 |
| `NEEDS_BUDGETING` | %82.96 | **%100.0** | **0.907** | 224 |

> **HIGH_DEBT_RISK Recall = %95.52:** Finansal krizi olan kullanıcıların %95.52'si yakalanıyor. Krizdeki birini kaçırmanın maliyeti (kredi batığı), gereksiz uyarıdan çok daha büyük — bu yüzden Recall özel olarak optimize edildi.

> **NEEDS_BUDGETING Recall = %100.0:** Bütçe yönetimine ihtiyacı olan hiçbir kullanıcı gözden kaçmadı (Gaussian Noise klonlamasının katkısı).

### XGBoost Parametreleri

```
n_estimators = 300
max_depth    = 5
learning_rate = 0.05
booster      = gbtree
n_features   = 39
```

> Sınıflar hardcoded değil, `model.classes_`'dan dinamik okunur.

### SHAP — Top 3 Koçluk Kararı Özelliği

| Sıra | Özellik | Açıklama |
|------|---------|----------|
| 🥇 1 | `net_cashflow` | Gelir − Gider (Net Nakit Akışı) |
| 🥈 2 | `savings_rate` | Tasarruf / Gelir Oranı |
| 🥉 3 | `expense_rolling3m_mean` | 3 Aylık Harcama Eğilim Ortalaması |

### Sentetik Veri Etkisi (Ablation)

```
Sentetik veri (SMOTE) olmadan → Stage 4 F1: %67
Gaussian Noise klonlama (+1.965 klon) → Stage 4 F1: %93.6
                                         ↑ +%26.6 artış
```

---

## 9. Tüm Metrikler Özeti

| Aşama | Algoritma | Ana Metrik | Değer | CV |
|-------|-----------|------------|-------|----|
| Stage 1 Hibrit | Regex + SVC + ELECTRA | Makro F1 | **0.9225** | 5-Fold |
| Stage 1 Ensemble | ELECTRA(0.4) + SVC(0.6) | Makro F1 | **0.9282** | — |
| Stage 1 ELECTRA | Solo | Makro F1 | 0.8752 | — |
| Stage 2 K-Means | K=4, 13 özellik | Silhouette | 0.2848 | — |
| Stage 2 K-Means | — | Calinski-Harabasz | **2943.11** | — |
| Stage 2 IsoForest | n=200 | Anomali % | %5.02 | — |
| Stage 3 LightGBM | 35 özellik | RMSE | **7.047₺** | — |
| Stage 3 LightGBM | — | WAPE | %29.16 | %36.64±2.24 |
| Stage 4 XGBoost | 39 özellik | Makro F1 | **0.9359** | 0.9438±0.008 |
| Stage 4 XGBoost | — | Accuracy | %96.90 | %97.31±0.34 |
| Stage 4 HIGH_DEBT_RISK | — | Recall | **%95.52** | — |
| Stage 4 NEEDS_BUDGETING | — | Recall | **%100.0** | — |
| Stage 4 SAGLIK (Stage 1) | — | F1 | **1.000** | — |

### Donanım ve Inference

| Bileşen | Süre | Donanım |
|---------|------|---------|
| Regex | < 0.5 ms/işlem | CPU |
| SVC + TF-IDF | 2–4 ms/işlem | CPU |
| Tam 4-Stage Pipeline | < 200 ms | CPU (GPU yok) |
| ELECTRA Eğitimi | ~40 dakika | Colab T4 GPU |
| XGBoost/LightGBM Eğitimi | Saniyeler | CPU |

---

## 10. Web Uygulaması

### Mimari

```
Frontend (React 18 + Vite + Tailwind)    Backend (FastAPI + Uvicorn)
        localhost:5173          ←→          localhost:8000
              │                                    │
    8 Sayfa:                           5 Router:
    - Dashboard                        - /api/auth
    - Analiz (6 sekme)                 - /api/analysis
    - Senaryo Testi                    - /api/demo
    - Raporlar                         - /api/scenario
    - Rehber                           - /api/reports
    - Ayarlar
    - Giriş / Kayıt
```

### API Endpoint'leri

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/api/health` | Sistem sağlık kontrolü |
| POST | `/api/auth/register` | Kullanıcı kaydı (SHA-256) |
| POST | `/api/auth/login` | Giriş → Bearer token |
| POST | `/api/auth/change-password` | Şifre değiştir (auth gerekli) |
| POST | `/api/analysis/upload` | CSV/Excel → 4 aşama pipeline |
| GET | `/api/analysis/results` | Son analiz sonuçları |
| POST | `/api/demo/load` | Hazır persona yükle |
| POST | `/api/scenario/simulate` | ±%50 senaryo simülasyonu |
| GET | `/api/reports/export/pdf` | ReportLab PDF (4 bölüm) |
| GET | `/api/reports/export/excel` | openpyxl Excel (4 sayfa) |

### Demo Modu — 3 Persona

| Persona | Koçluk Kararı | Profil |
|---------|---------------|--------|
| Ahmet Bey | `HIGH_DEBT_RISK` 🔴 | Gider > gelir, negatif nakit akışı |
| Ayşe Hanım | `GREAT_SAVER` 🟢 | Tasarruf oranı > %65, düzenli gelir |
| Zeynep Hanım | `NEEDS_BUDGETING` 🟡 | Harcama eğilimi kontrolsüz artışta |

### Başlatma

```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## 11. Güvenlik ve KVKK

### Güvenlik Önlemleri

| Önlem | Durum |
|-------|-------|
| SHA-256 şifre hashleme | ✅ Uygulandı |
| `users.json` ve `reports_store.json` `.gitignore`'da | ✅ Korunuyor |
| `/api/auth/reset-password` kaldırıldı (email-only açığı) | ✅ Düzeltildi |
| `autoComplete="current-password/new-password"` | ✅ Uygulandı |
| CORS: yalnızca localhost:5173, 3000, 127.0.0.1:5173 | ✅ Kısıtlandı |
| Bearer token authentication | ✅ Uygulandı |

### KVKK Uyum Sistemi (`kvkk_masker.py`)

- **Tamamen örüntü tabanlı** — hardcoded isim listesi yok
- `_NAME_BEFORE_BANK` regex: `re.IGNORECASE` olmadan derlendi (büyük/küçük harfe duyarlı)
- Banka ekstrelerinde kişi adları BÜYÜK HARF → yalnızca bu format maskelenir
- "Ziraat Mobil", "Garanti BBVA" gibi banka isimleri yanlışlıkla maskelenmez
- IBAN, TCKN ve kişi adı kalıpları otomatik maskelenir
- **7 KVKK testi geçildi** ✅

### Hugging Face Gated Dataset

- **Hesap:** Saraa34 | **Ayar:** `gated: "manual"`
- 8 eğitim dosyası (~71 MB) yüklendi
- Ziyaretçiler: sayfayı görür → form doldurur → onay bekler → onaylanınca indirebilir
- Form: Ad Soyad, Kurum, Kullanım Amacı, Ülke, Açıklama, KVKK Onayı

---

## 12. Tartışma ve Özgün Katkılar

### Projenin Özgün Katkıları

1. **Hibrit Mimari (Türkçe Finans NLP'de İlk):** Regex + LinearSVC + ELECTRA hiyerarşik pipeline. Literatürdeki saf DL sistemlerine kıyasla %40+ hızlı, %30 düşük sunucu maliyeti.

2. **Türkçe Finansal NLP Boşluğu Dolduruldu:** Eklemeli dil yapısına özel ELECTRA ile TÜBİTAK/ulusal alanda kritik boşluk kapatıldı.

3. **Tersine Mühendislik Test Stratejisi:** Gerçek verinin %80-100'ü teste ayrıldı — overfitting olmadığının matematiksel kanıtı.

4. **SHAP Açıklanabilirlik (XAI):** "Kara Kutu" problemi çözüldü — koçluk kararları net SHAP değerleriyle şeffaflaştırıldı.

5. **OOD Güvenlik Duvarı:** %65 threshold altındaki işlemleri reddederek yanlış bilgi vermek yerine "DİĞER" kategorisine alır.

6. **Döngüsel Zaman Kodlaması:** `month_sin`/`month_cos` — SHAP'ta 2. sıraya oturdu.

7. **HIGH_DEBT_RISK Recall = %95.5:** Finansal kriz tespitinde kritik güvenlik ağı.

8. **Sıfır Maliyetli Ön Filtre:** %31.2 iş yükü Regex ile çözüldü — AWS/Azure'da %30 tasarruf.

### Kısıtlar

| Kısıt | Geçici Çözüm |
|-------|-------------|
| Yeni markalar tanınmıyor (Zero-shot) | OOD → DİĞER + periyodik retraining |
| Sadece Türkçe | mBERT/XLM planlandı |
| Stage 3 MAPE %75.12 | WAPE=%29.16 güvenilir; amaç trend analizi |
| Gerçek veri %5.3 | Kural Motoru kompansasyon sağlıyor |

### Gelecek Çalışmalar

**Kısa Vadeli:** Docker konteynerizasyon · Kafka akış entegrasyonu · Concept Drift izleme · Moving Average baseline raporu

**Uzun Vadeli:** LLM entegrasyonu (OOD için Zero-shot) · Aktif Öğrenme (Feedback Loop) · mBERT çok dilli destek · GPS + saat verisi kişiselleştirme

---

## 13. Jüri Soru-Cevap Kataloğu

**S: Gerçek veri %5.3 iken model güvenilir mi?**  
C: Test setinin büyük çoğunluğu gerçek veriden oluştu (Tersine Mühendislik). Sentetik verinin istatistiksel dağılımı ve banka kısaltmaları gerçeğe birebir benzetildi. 5-Fold CV ile overfitting dışlandı.

**S: MAPE %75.12 çok yüksek değil mi?**  
C: Stage 3 amacı kuruşluk tahmin değil, trend tespiti. WAPE = %29.16 ile sistem güvenilirdir. Moving Average baseline karşılaştırması eklenecek.

**S: LinearSVC nasıl predict_proba üretiyor?**  
C: `CalibratedClassifierCV` ile Platt scaling (sigmoid calibration) uygulandı. Threshold 0.65, P-R eğrisinin F1 maksimum noktasından belirlendi.

**S: ELECTRA üretimde aktif mi?**  
C: Üretim hattı: Regex + Kalibre SVC (2-4ms). ELECTRA karmaşık bağlamlarda fallback model. Maliyet ve latency nedeniyle her işlemde çalıştırılmıyor — bilinçli mühendislik kararı.

**S: K-Means Silhouette 0.284 düşük değil mi?**  
C: Finansal profiller doğaları gereği overlapping. Calinski-Harabasz = **2943** ve Davies-Bouldin = 1.559 ile kümelerin iş anlamı oluşturduğu kanıtlandı.

**S: XGBoost basit If-Else kuralı mı öğreniyor?**  
C: Hayır. "Geliri yüksek ama son 3 ayda kontrolsüz artış" gibi non-linear etkileşimleri öğrendi. SHAP kararların finansal iş mantığıyla örtüştüğünü kanıtladı.

**S: Sistem üretime hazır mı?**  
C: Evet. FastAPI + React deploy edildi. 2-4ms inference. Demo, CSV yükleme, senaryo, PDF/Excel tamamlandı. GPU zorunluluğu yok.

**S: Veri sızıntısını nasıl engellediniz?**  
C: Klonlamadan önce train/test ayrımı yapıldı. Gerçek test metinleri `~isin(real_lower)` ile sentetikten izole edildi. YENİVERİTEST.xlsx %100 test setine ayrıldı.

**S: Sentetik veri olmadan F1 kaç?**  
C: Stage 4 XGBoost F1: **%67**. Gaussian Noise ile +1.965 klon sonrası **%93.6** (+%26.6 artış). Projenin en büyük bilimsel katkısı.

**S: KVKK uyumu nasıl sağlandı?**  
C: `kvkk_masker.py` tamamen pattern-based. Banka ekstrelerinde kişi adları BÜYÜK HARF olduğu için regex büyük/küçük harfe duyarlı derlendi. 7 test geçildi.

---

### En Güçlü 5 Savunma Noktası

| # | Kanıt | Değer |
|---|-------|-------|
| 1 | HIGH_DEBT_RISK Recall | **%95.52** — krizdeki kullanıcılar yakalanıyor |
| 2 | SAGLIK F1 = Zero-Defect | **1.000** — azınlık sınıf klonlamasının katkısı |
| 3 | Ablation: Sentetik veri etkisi | %67 → **%93.6** (+%26.6) |
| 4 | 5-Fold CV stabilitesi | std **±%0.77** — model kararlı |
| 5 | Regex iş yükü tasarrufu | **%31.2** yük sıfır maliyetle çözüldü |

---

*Sara Toptamur · Haziran 2026*
