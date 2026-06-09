# Google Colab — ML Pipeline Eğitimi

Bu klasörü Google Drive'a yükleyin ve aşağıdaki sırayla çalıştırın.

## Yükleme Adımları

1. Bu `colab_training/` klasörünü Google Drive'a yükleyin
2. Aşağıdaki veri dosyalarını da `colab_training/data/` altına kopyalayın:
   - `enhanced_synthetic_bank_data.csv`
   - `synthetic_budget_data.csv`
   - `bankaverison.xlsx` (gerçek test verisi)
   - `stage2_user_monthly_features.csv` (varsa, Stage 2'den gelir)

## Notebook Çalıştırma Sırası

| Sıra | Notebook | İçerik | GPU Gereksinim |
|------|----------|---------|---------------|
| 1 | `01_stage1_bert_classifier.ipynb` | Turkish ELECTRA fine-tuning, Confusion Matrix, ROC-AUC, Error Analysis | **Evet (T4)** |
| 2 | `02_stage2_unsupervised_ml.ipynb` | Isolation Forest + K-Means Clustering | Hayır (CPU OK) |
| 3 | `03_stage3_forecasting_shap.ipynb` | LightGBM + SMAPE/WAPE + SHAP + TimeSeriesSplit | Hayır (CPU OK) |
| 4 | `04_stage4_xgboost_coach.ipynb` | XGBoost Coaching Classifier + CV + Confusion Matrix | Hayır (CPU OK) |

## Colab GPU Aktif Etme

Her notebook'ta üst menüden:
**Çalışma Zamanı → Çalışma Zamanı Türünü Değiştir → T4 GPU** seçin.

## Çıktılar

Her notebook'un çalıştırılması sonucunda `colab_training/outputs/` klasörüne:
- Eğitilmiş model dosyaları (`.pkl`, `.pt`)
- Metrik JSON dosyaları
- Grafik PNG dosyaları

kaydedilecektir. Bu dosyaları indirip projenizin `models/` ve `reports/` klasörlerine aktarın.
