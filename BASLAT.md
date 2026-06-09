# Banka AI Web Uygulamasi — Baslangic Kilavuzu

## Proje Yapisi
```
veri_seti/
├── backend/           # FastAPI Python backend
│   ├── main.py
│   ├── routers/       # auth, analysis, demo, scenario, reports
│   ├── services/      # pipeline_service, report_service
│   └── requirements.txt
├── frontend/          # React + Vite + Tailwind
│   ├── src/
│   │   ├── pages/     # LandingPage, Dashboard, AnalyzePage, ...
│   │   ├── components/# Layout, Sidebar, Header
│   │   └── context/   # AuthContext
│   └── package.json
├── bank_ai_pipeline.py
├── kvkk_masker.py
└── rules_engine.py
```

---

## 1. Backend Kurulumu

```bash
cd veri_seti/backend

# Bagimlilikları kur
pip install -r requirements.txt

# Calistir (veri_seti klasoründen)
cd ..
python -m uvicorn backend.main:app --reload --port 8000
```

Backend API: http://localhost:8000
API Docs:    http://localhost:8000/docs

---

## 2. Frontend Kurulumu

```bash
cd veri_seti/frontend

# Bagimlilikları kur (ilk seferinde)
npm install

# Gelistirme sunucusunu calistir
npm run dev
```

Frontend: http://localhost:5173

---

## 3. Her Iki Servisi Ayni Anda Calistir

**Terminal 1 (Backend):**
```bash
cd C:\Users\...\veri_seti
python -m uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd C:\Users\...\veri_seti\frontend
npm run dev
```

Tarayıcida http://localhost:5173 ac.

---

## 4. Demo Modu

Backend calismasa da demo modu temel gorunum icin calisir.
Ancak AI analizi icin backend gereklidir.

Demo persona'lari:
- **Ahmet Bey** — Yuksek Butce Riski (HIGH_DEBT_RISK)
- **Ayse Hanim** — Tasarrufcu Profil (GREAT_SAVER)
- **Zeynep Hanim** — Butceleme Yapmali (NEEDS_BUDGETING)

---

## 5. Gercek Kullanici Modu

1. Kayit Ol sayfasindan hesap olustur
2. Analiz Et → Veri Yukle sekmesine git
3. CSV veya Excel ekstre yukle
4. Pipeline otomatik calisir, sonuclar gosterilir
5. Rapor sekmesinden PDF/Excel indir

Minimum CSV formati:
```csv
tarih,aciklama,tutar
2026-06-01,MIGROS AS,-450.00
2026-06-05,MAAS ODEMESI,35000.00
```

---

## 6. API Endpoint'leri

| Endpoint                    | Method | Aciklama                    |
|-----------------------------|--------|-----------------------------|
| /api/auth/register          | POST   | Kayit ol                    |
| /api/auth/login             | POST   | Giris yap                   |
| /api/demo/personas          | GET    | Demo persona listesi        |
| /api/demo/analyze/{id}      | GET    | Demo analiz sonucu          |
| /api/analysis/upload        | POST   | CSV/Excel yukle + analiz et |
| /api/analysis/result        | GET    | Son analiz sonucunu al      |
| /api/scenario/test          | POST   | Senaryo simulasyonu         |
| /api/reports/pdf            | POST   | PDF rapor indir             |
| /api/reports/excel          | POST   | Excel indir                 |

---

## 7. Notlar

- Backend mock auth kullanir (in-memory). Sunucu kapaninca kullanicilar silinir.
- Prototip surumde yuklunen dosyalar bellekte tutulur, disk'e yazilmaz.
- ML modelleri (sklearn, lightgbm, xgboost) Windows ortaminizda yuklu olmalidir.
- Demo modu ML kutuphanesi gerektirmez — onceden hesaplanmis sonuclari dondurur.
