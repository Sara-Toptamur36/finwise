# -*- coding: utf-8 -*-
"""
Uctan Uca Yapay Zeka Finansal Analiz Hatti (API Sinifi)
Stage 1 -> Stage 2 -> Stage 3 -> Stage 4

FIX 1: Stage 2 K-Means pipeline entegre edildi
FIX 2: Stage 3 LightGBM feature mismatch cozuldu
FIX 3: KVKK masker hardcoded isim listesi kaldirildi (kvkk_masker.py'da)
FIX 4: XGBoost sinif isimleri model'den dinamik okunuyor
"""
import os, sys, pickle, json, warnings
import numpy as np
import pandas as pd

try:
    from kvkk_masker import mask_kvkk
except ImportError:
    mask_kvkk = lambda x: x

warnings.filterwarnings('ignore')

try:
    import xgboost as xgb
    import lightgbm as lgb
except ImportError:
    print("UYARI: xgboost veya lightgbm kutuphaneleri eksik!")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from rules_engine import preprocess_text, rule_based_classify

ALL_CATEGORIES = [
    'ALISVERIS', 'BANKA_KESINTISI', 'DIGER', 'EGITIM', 'EGLENCE',
    'FATURA', 'MARKET', 'NAKIT_ISLEMLERI', 'SAGLIK', 'SEYAHAT',
    'ULASIM', 'VIRMAN', 'YEME_ICME'
]


class BankAIPipeline:
    def __init__(self, base_models_dir="models", colab_outputs_dir="colab_training/outputs"):
        self.base_models_dir    = os.path.join(BASE_DIR, base_models_dir)
        self.colab_outputs_dir  = os.path.join(BASE_DIR, colab_outputs_dir)
        self.stage1_svc         = None
        self.stage1_word        = None
        self.stage1_char        = None
        self.stage1_lenc        = None
        self.stage2_kmeans      = None
        self.stage2_scaler      = None
        self.stage2_config      = None   # FIX 1
        self.stage3_lgbm        = None
        self.stage3_features    = None   # FIX 2
        self.stage4_xgb         = None
        self.stage4_classes     = None   # FIX 4
        self._load_models()

    def _load_models(self):
        out = self.colab_outputs_dir

        # Stage 1
        try:
            with open(os.path.join(out, "stage1 svc_v16.pkl"),          "rb") as f: self.stage1_svc  = pickle.load(f)
            with open(os.path.join(out, "stage1  word_tfidf_v16.pkl"),   "rb") as f: self.stage1_word = pickle.load(f)
            with open(os.path.join(out, "stage1  char_16 tfidf_v16.pkl"),"rb") as f: self.stage1_char = pickle.load(f)
            with open(os.path.join(out, "stage1 .pkl"),                  "rb") as f: self.stage1_lenc = pickle.load(f)
            print(" [OK] Stage 1 (Kategorizasyon - SVC v16) Yuklendi")
        except Exception as e:
            print(f" [HATA] Stage 1 yuklenemedi: {e}")

        # Stage 2 -- FIX 1: stage2_config.pkl ile feature_cols ve cluster_name_map
        try:
            with open(os.path.join(out, "kmeans_model.pkl"),   "rb") as f: self.stage2_kmeans = pickle.load(f)
            with open(os.path.join(out, "stage2_scaler.pkl"),  "rb") as f: self.stage2_scaler = pickle.load(f)
            with open(os.path.join(out, "stage2_config.pkl"),  "rb") as f: self.stage2_config = pickle.load(f)
            print(" [OK] Stage 2 (Profilleme) Yuklendi")
            print(f"      Kume isimleri: {self.stage2_config.get('cluster_name_map', {})}")
        except Exception as e:
            print(f" [HATA] Stage 2 yuklenemedi: {e}")

        # Stage 3 -- FIX 2: feature listesi model'den dinamik aliniyor
        try:
            with open(os.path.join(out, "lgbm_v3_model.pkl"), "rb") as f: self.stage3_lgbm = pickle.load(f)
            if hasattr(self.stage3_lgbm, 'feature_name_') and self.stage3_lgbm.feature_name_:
                self.stage3_features = list(self.stage3_lgbm.feature_name_)
            elif hasattr(self.stage3_lgbm, 'feature_names_in_'):
                self.stage3_features = list(self.stage3_lgbm.feature_names_in_)
            elif hasattr(self.stage3_lgbm, 'booster_'):
                self.stage3_features = self.stage3_lgbm.booster_.feature_name()
            else:
                self.stage3_features = []
            print(f" [OK] Stage 3 (Harcama Tahmini - LGBM) Yuklendi [{len(self.stage3_features)} feature]")
        except Exception as e:
            print(f" [HATA] Stage 3 yuklenemedi: {e}")

        # Stage 4 -- FIX 4: sinif isimleri results JSON'dan (LabelEncoder siralama=alfabetik)
        try:
            with open(os.path.join(out, "xgboost_coach_model.pkl"), "rb") as f: self.stage4_xgb = pickle.load(f)
            results_path = os.path.join(out, "stage4_xgb_results.json")
            if os.path.exists(results_path):
                with open(results_path, encoding="utf-8") as f:
                    rj = json.load(f)
                self.stage4_classes = sorted(rj["per_class"].keys())  # alfabetik = LabelEncoder sirasi
            elif hasattr(self.stage4_xgb, 'classes_'):
                self.stage4_classes = [str(c) for c in self.stage4_xgb.classes_]
            else:
                self.stage4_classes = ["GREAT_SAVER", "HIGH_DEBT_RISK", "NEEDS_BUDGETING"]
            print(f" [OK] Stage 4 (Finansal Kocluk - XGBoost) Yuklendi -- siniflar: {self.stage4_classes}")
        except Exception as e:
            print(f" [HATA] Stage 4 yuklenemedi: {e}")

        print("Sistem Kullanima Hazir!\n" + "-" * 40)

    def process_transactions(self, transactions):
        """
        Ham islem listesini alir, 4 asamali pipeline'dan gecirir.
        Format: [{'tarih': '2026-06-01', 'aciklama': 'MIGROS', 'tutar': 250.0, 'is_income': False}, ...]
        """
        if not transactions:
            return {"error": "Bos islem listesi"}

        # KVKK maskeleme
        df = pd.DataFrame([
            {'tarih': t.get('tarih'), 'aciklama': mask_kvkk(t.get('aciklama', '')),
             'tutar': t.get('tutar'), 'is_income': t.get('is_income')}
            for t in transactions
        ])

        # Stage 1: Kategorizasyon
        categories = []
        for _, row in df.iterrows():
            desc = str(row.get('aciklama', ''))
            cat  = rule_based_classify(desc)
            if not cat:
                clean = preprocess_text(desc)
                X_w   = self.stage1_word.transform([clean])
                X_c   = self.stage1_char.transform([clean])
                from scipy.sparse import hstack
                X     = hstack([X_w, X_c])
                idx   = self.stage1_svc.predict(X)[0]
                cat   = self.stage1_lenc.inverse_transform([idx])[0]
            categories.append(cat)
        df['predicted_category'] = categories

        # Feature engineering
        # Türk tarih formatı desteği: GG.AA.YYYY, YYYY-MM-DD vb.
        try:
            df['tarih'] = pd.to_datetime(df['tarih'], dayfirst=True, format='mixed')
        except Exception:
            df['tarih'] = pd.to_datetime(df['tarih'], infer_datetime_format=True, dayfirst=True)
        current_month   = df['tarih'].max().replace(day=1)
        df_cur          = df[df['tarih'] >= current_month]
        income          = float(df_cur[df_cur['is_income'] == True]['tutar'].sum())
        expense         = float(df_cur[df_cur['is_income'] == False]['tutar'].sum())
        savings         = income - expense
        savings_rate    = savings / income  if income  > 0 else 0.0
        budget_util     = expense / income  if income  > 0 else 0.0
        txn_count       = len(df_cur)
        total_expense   = expense if expense > 0 else 1.0

        cat_exp = df_cur[df_cur['is_income'] == False].groupby('predicted_category')['tutar'].sum()

        spend_vals = {f'spend_{c}': 0.0 for c in ALL_CATEGORIES}
        share_vals = {f'share_{c}': 0.0 for c in ALL_CATEGORIES}
        for cat, amt in cat_exp.items():
            spend_vals[f'spend_{cat}'] = float(amt)
            share_vals[f'share_{cat}'] = float(amt) / total_expense

        base = {
            'monthly_income_computed':  income,
            'monthly_expense_computed': expense,
            'savings_rate':             savings_rate,
            'budget_utilisation':       budget_util,
            'txn_count':                txn_count,
            'net_cashflow':             savings,
        }
        month_val = current_month.month
        time_f = {
            'month_sin': float(np.sin(2 * np.pi * month_val / 12)),
            'month_cos': float(np.cos(2 * np.pi * month_val / 12)),
        }

        # FIX 1: Stage 2 -- K-Means ile gercek kume tahmini
        cluster_id   = 0
        cluster_name = "Bilinmiyor"
        if self.stage2_kmeans and self.stage2_scaler and self.stage2_config:
            try:
                cols   = self.stage2_config['feature_cols']
                c_map  = self.stage2_config.get('cluster_name_map', {})
                src    = {**base, **spend_vals}
                vec    = np.array([[src.get(c, 0.0) for c in cols]])
                scaled = self.stage2_scaler.transform(vec)
                cluster_id   = int(self.stage2_kmeans.predict(scaled)[0])
                cluster_name = c_map.get(cluster_id, f"Kume-{cluster_id}")
            except Exception as e:
                print(f" [UYARI] Stage 2 kumeleme basarisiz, cluster=0 kullaniliyor: {e}")

        inference_row = {
            **base, **spend_vals, **share_vals, **time_f,
            'cluster': cluster_id, 'cluster_enc': cluster_id,
            'expense_lag1': 0.0, 'expense_lag2': 0.0, 'expense_lag3': 0.0,
            'income_lag1':  0.0, 'income_lag2':  0.0, 'income_lag3':  0.0,
            'savings_lag1': 0.0, 'savings_lag2': 0.0, 'savings_lag3': 0.0,
            'expense_rolling3m_mean': expense, 'expense_rolling3m_std': 0.0,
            'income_rolling3m_mean':  income,
            'anomaly_score': 0.0, 'is_anomaly': 0.0, 'expense_anomaly_flag': 0,
            'expense_peer_pct': 0.0, 'income_peer_pct': 0.0, 'savings_peer_pct': 0.0,
        }

        # FIX 2: Stage 3 -- LightGBM feature mismatch olmadan guvenli tahmin
        forecast_expense = expense
        if self.stage3_lgbm and self.stage3_features:
            try:
                lgb_row      = pd.DataFrame([[inference_row.get(f, 0.0) for f in self.stage3_features]], columns=self.stage3_features)
                forecast_expense = float(self.stage3_lgbm.predict(lgb_row)[0])
            except Exception as e:
                print(f" [UYARI] Stage 3 tahmin basarisiz, bu ayin degeri kullaniliyor: {e}")

        # FIX 4: Stage 4 -- XGBoost sinif isimleri model'den
        coach_action = "ON_TRACK"
        if self.stage4_xgb and self.stage4_classes:
            try:
                feats     = self.stage4_xgb.feature_names_in_
                xgb_row   = pd.DataFrame([[inference_row.get(f, 0.0) for f in feats]], columns=feats)
                raw_pred  = self.stage4_xgb.predict(xgb_row)[0]
                pred_str  = str(raw_pred)
                # Eger tahmin dogrudan sinif etiketi ise kullan, yoksa index olarak yorumla
                if pred_str in self.stage4_classes:
                    coach_action = pred_str
                else:
                    coach_action = self.stage4_classes[int(raw_pred)]
            except Exception as e:
                print(f" [UYARI] Stage 4 kocluk basarisiz, ON_TRACK donduruluyor: {e}")

        # Kocluk mesaji
        MESSAGES = {
            "NEEDS_BUDGETING":  "Butcenizi kontrol etmeniz gerekiyor. Degisken harcamalariniz (alisveris/eglence/yemek) yukseliyor.",
            "HIGH_DEBT_RISK":   "KIRMIZI ALARM: Gelirinizden fazlasini harcayip borc sarmalina giriyorsunuz!",
            "GREAT_SAVER":      "Harika! Butcenizi cok iyi yonetiyor ve tasarruf ediyorsunuz.",
            "EMERGENCY_WARNING":"ACIL: Finansal durumunuz kritik esige ulasti. Derhal harekete gecin.",
            "SAVE_MORE":        "Iyi gidiyorsunuz -- kucuk kisintilerla tasarruf oraninizi daha da artirabilirsiniz.",
            "ON_TRACK":         "Finansal sagliginiz standart seviyede. Butcenize sadik kalmaya devam edin.",
        }

        if coach_action == "NEEDS_BUDGETING":
            var_cats = ['share_ALISVERIS', 'share_EGLENCE', 'share_YEME_ICME']
            highest  = max(var_cats, key=lambda x: inference_row.get(x, 0))
            cat_msg  = {"share_ALISVERIS": "alisveris", "share_EGLENCE": "eglence"}.get(highest, "yeme-icme")
            coach_message = (f"Butcenizi kontrol etmeniz gerekiyor. "
                             f"Bu ay en buyuk degisken harcamaniz {cat_msg} kategorisinde. Kisintiya gidin.")
        else:
            coach_message = MESSAGES.get(coach_action, "Finansal sagliginiz standart seviyede.")

        df_sample = df[['tarih', 'aciklama', 'tutar', 'predicted_category']].head(5).copy()
        df_sample['tarih'] = df_sample['tarih'].dt.strftime('%Y-%m-%d')

        # Kategori bazlı harcama dağılımı (tüm veri, gelir hariç)
        cat_breakdown = {c: 0.0 for c in ALL_CATEGORIES}
        for cat, amt in cat_exp.items():
            if cat in cat_breakdown:
                cat_breakdown[cat] = float(amt)

        return {
            "summary": {
                "total_income":      income,
                "total_expense":     expense,
                "net_cashflow":      savings,
                "savings_rate_pct":  round(savings_rate * 100, 2),
            },
            "user_profile": {
                "cluster_id":   cluster_id,
                "cluster_name": cluster_name,
            },
            "categorized_transactions_sample": df_sample.to_dict('records'),
            "category_breakdown": cat_breakdown,
            "ai_forecast": {
                "next_month_expected_expense": round(forecast_expense, 2),
            },
            "ai_coach": {
                "action_label":        coach_action,
                "personalized_message": coach_message,
            },
        }


if __name__ == "__main__":
    pipeline  = BankAIPipeline()
    test_data = [
        {"tarih": "2026-06-01", "aciklama": "MIGROS AS",      "tutar": 450.0,   "is_income": False},
        {"tarih": "2026-06-03", "aciklama": "TRENDYOL",        "tutar": 2150.0,  "is_income": False},
        {"tarih": "2026-06-05", "aciklama": "MAAS ODEMESI",    "tutar": 35000.0, "is_income": True},
        {"tarih": "2026-06-10", "aciklama": "ZARA GIYIM",      "tutar": 4200.0,  "is_income": False},
        {"tarih": "2026-06-15", "aciklama": "STARBUCKS",       "tutar": 250.0,   "is_income": False},
        {"tarih": "2026-06-20", "aciklama": "KIRA ODEMESI",    "tutar": 15000.0, "is_income": False},
        {"tarih": "2026-06-25", "aciklama": "NETFLIX",         "tutar": 150.0,   "is_income": False},
    ]
    print("\n[TEST] Pipeline test ediliyor...\n")
    res = pipeline.process_transactions(test_data)
    print(json.dumps(res, indent=4, ensure_ascii=False))
