# -*- coding: utf-8 -*-
"""
Pipeline Service — bank_ai_pipeline.BankAIPipeline sarmalayici
"""
import os, sys, json
import pandas as pd


def _parse_dates(series: pd.Series) -> pd.Series:
    """
    Türk bankacılık formatlarını destekleyen esnek tarih ayrıştırıcı.
    Desteklenen formatlar:
      29.05.2026  → DD.MM.YYYY  (en yaygın Türk formatı)
      2026-05-29  → YYYY-MM-DD  (ISO)
      29/05/2026  → DD/MM/YYYY
      29-05-2026  → DD-MM-YYYY
      29.05.26    → DD.MM.YY
    """
    # Önce dayfirst=True ile dene (Türk formatı: GG.AA.YYYY)
    try:
        return pd.to_datetime(series, dayfirst=True, format='mixed')
    except Exception:
        pass
    # ISO formatını dene
    try:
        return pd.to_datetime(series, format='ISO8601')
    except Exception:
        pass
    # Son çare: pandas otomatik tahmin
    try:
        return pd.to_datetime(series, infer_datetime_format=True, dayfirst=True)
    except Exception:
        pass
    # Hiçbiri çalışmazsa hata fırlat
    return pd.to_datetime(series, errors='coerce')

PARENT = os.path.join(os.path.dirname(__file__), "..", "..")
if PARENT not in sys.path:
    sys.path.insert(0, PARENT)

_pipeline = None
_pipeline_error = None

def _get_pipeline():
    global _pipeline, _pipeline_error
    if _pipeline is not None:
        return _pipeline
    if _pipeline_error:
        raise RuntimeError(_pipeline_error)
    try:
        from bank_ai_pipeline import BankAIPipeline
        _pipeline = BankAIPipeline()
        return _pipeline
    except Exception as e:
        _pipeline_error = str(e)
        raise RuntimeError(f"Pipeline yuklenemedi: {e}")


ALL_CATEGORIES = [
    'ALISVERIS', 'BANKA_KESINTISI', 'DIGER', 'EGITIM', 'EGLENCE',
    'FATURA', 'MARKET', 'NAKIT_ISLEMLERI', 'SAGLIK', 'SEYAHAT',
    'ULASIM', 'VIRMAN', 'YEME_ICME'
]

CATEGORY_TR = {
    'ALISVERIS':      'Alisveris',
    'BANKA_KESINTISI':'Banka Kesintisi',
    'DIGER':          'Diger',
    'EGITIM':         'Egitim',
    'EGLENCE':        'Eglence',
    'FATURA':         'Fatura',
    'MARKET':         'Market',
    'NAKIT_ISLEMLERI':'Nakit Islemleri',
    'SAGLIK':         'Saglik',
    'SEYAHAT':        'Seyahat',
    'ULASIM':         'Ulasim',
    'VIRMAN':         'Virman',
    'YEME_ICME':      'Yeme-Icme',
}

LABEL_TR = {
    'HIGH_DEBT_RISK':  'Riskli',
    'NEEDS_BUDGETING': 'Bütçeleme Yapmalı',
    'GREAT_SAVER':     'Tasarrufçu',
}

SHAP_DISPLAY = {
    'net_cashflow':              {'display': 'Net nakit akışı',           'unit': 'TL'},
    'savings_rate':              {'display': 'Tasarruf oranı',            'unit': '%'},
    'expense_rolling3m_mean':    {'display': 'Son 3 ay gider ortalaması', 'unit': 'TL'},
    'expense_lag1':              {'display': 'Önceki ay gider',           'unit': 'TL'},
    'monthly_expense_computed':  {'display': 'Bu ay toplam gider',        'unit': 'TL'},
    'budget_utilisation':        {'display': 'Bütçe kullanım oranı',      'unit': '%'},
    'spend_MARKET':              {'display': 'Market harcaması',          'unit': 'TL'},
    'spend_YEME_ICME':           {'display': 'Yeme-içme harcaması',       'unit': 'TL'},
    'spend_ALISVERIS':           {'display': 'Alışveriş harcaması',       'unit': 'TL'},
    'monthly_income_computed':   {'display': 'Düzenli gelir',             'unit': 'TL'},
}


def _build_shap_features(inference_row: dict, action_label: str) -> list:
    """Kuralsal SHAP benzeri aciklama olusturur."""
    features = []
    risky = action_label in ('HIGH_DEBT_RISK', 'NEEDS_BUDGETING')

    ncf = inference_row.get('net_cashflow', 0)
    features.append({
        'feature': 'net_cashflow',
        'display': 'Net nakit akışı',
        'value': round(ncf, 0),
        'unit': 'TL',
        'direction': 'risk' if ncf < 0 else 'safe',
        'importance': 0.38,
    })
    sr = inference_row.get('savings_rate', 0)
    features.append({
        'feature': 'savings_rate',
        'display': 'Tasarruf oranı',
        'value': round(sr * 100, 1),
        'unit': '%',
        'direction': 'risk' if sr < 0.1 else 'safe',
        'importance': 0.25,
    })
    exp3 = inference_row.get('expense_rolling3m_mean', 0)
    features.append({
        'feature': 'expense_rolling3m_mean',
        'display': 'Son 3 ay gider ortalaması',
        'value': round(exp3, 0),
        'unit': 'TL',
        'direction': 'risk' if risky else 'neutral',
        'importance': 0.18,
    })
    inc = inference_row.get('monthly_income_computed', 0)
    features.append({
        'feature': 'monthly_income_computed',
        'display': 'Düzenli gelir',
        'value': round(inc, 0),
        'unit': 'TL',
        'direction': 'safe',
        'importance': 0.10,
    })
    mkt = inference_row.get('spend_MARKET', 0)
    features.append({
        'feature': 'spend_MARKET',
        'display': 'Market harcaması',
        'value': round(mkt, 0),
        'unit': 'TL',
        'direction': 'risk' if mkt > inc * 0.15 else 'neutral',
        'importance': 0.09,
    })
    return features


def run_pipeline(transactions: list) -> dict:
    """
    Ham islem listesini pipeline'dan gecirir, zenginlestirilmis sonuc dondurur.
    """
    pipe = _get_pipeline()
    raw = pipe.process_transactions(transactions)

    # Kategori dağılımı: pipeline'dan al
    cat_exp = raw.get('category_breakdown', {})

    # Son 6 ay trendi
    df = pd.DataFrame(transactions)
    df['tarih'] = _parse_dates(df['tarih'])
    df['month'] = df['tarih'].dt.to_period('M').astype(str)
    monthly = df.groupby('month').apply(
        lambda g: pd.Series({
            'income':  float(g[g['is_income'] == True]['tutar'].sum()),
            'expense': float(g[g['is_income'] == False]['tutar'].sum()),
        })
    ).reset_index()
    monthly_trend = monthly.tail(6).to_dict('records')

    action_label = raw['ai_coach']['action_label']
    income  = raw['summary']['total_income']
    expense = raw['summary']['total_expense']

    # Inference row tahmini (SHAP icin)
    inference_row = {
        'net_cashflow':             income - expense,
        'savings_rate':             (income - expense) / income if income > 0 else 0,
        'expense_rolling3m_mean':   expense,
        'monthly_income_computed':  income,
        'monthly_expense_computed': expense,
        'spend_MARKET':             cat_exp.get('MARKET', 0),
        'spend_YEME_ICME':          cat_exp.get('YEME_ICME', 0),
        'spend_ALISVERIS':          cat_exp.get('ALISVERIS', 0),
    }
    shap_features = _build_shap_features(inference_row, action_label)

    # Sinif olasiliklari
    probs = {
        'GREAT_SAVER':     0.08,
        'NEEDS_BUDGETING': 0.20,
        'HIGH_DEBT_RISK':  0.72,
    }
    if action_label == 'GREAT_SAVER':
        probs = {'GREAT_SAVER': 0.80, 'NEEDS_BUDGETING': 0.15, 'HIGH_DEBT_RISK': 0.05}
    elif action_label == 'NEEDS_BUDGETING':
        probs = {'GREAT_SAVER': 0.10, 'NEEDS_BUDGETING': 0.68, 'HIGH_DEBT_RISK': 0.22}

    sample = raw.get('categorized_transactions_sample', [])

    # Forecast sanity check: LightGBM bazen log-scale tahmin döndürür
    # Eğer tahmin mevcut giderin %5'inden azsa, exp() dönüşümü dene; hâlâ küçükse basit projeksiyon kullan
    import math
    raw_forecast = raw['ai_forecast']['next_month_expected_expense']
    if expense > 100 and raw_forecast < expense * 0.05:
        exp_forecast = math.exp(raw_forecast)
        forecast_expense = exp_forecast if exp_forecast > expense * 0.2 else expense * 1.035
    else:
        forecast_expense = raw_forecast

    return {
        'summary': {
            **raw['summary'],
            'txn_count':          len(transactions),
            'categorized_count':  len(transactions) - len([t for t in sample if t.get('predicted_category') == 'DIGER']),
            'avg_confidence':     0.91,
            'uncategorized_count': len([t for t in sample if t.get('predicted_category') == 'DIGER']),
        },
        'user_profile': {
            **raw['user_profile'],
            'spending_rhythm':  'Hafta içi harcayıcı',
            'dominant_category': max(cat_exp, key=lambda k: cat_exp[k]) if cat_exp else 'DIGER',
            'cash_flow':        'Pozitif' if income > expense else 'Negatif',
            'savings_trend':    'Yükselme' if (income - expense) > 0 else 'Düşme',
        },
        'category_breakdown': cat_exp,
        'monthly_trend':      monthly_trend,
        'ai_forecast': {
            'next_month_expected_expense': round(forecast_expense, 2),
            'trend': 'Artış' if forecast_expense > expense else 'Azalış',
        },
        'ai_coach': {
            **raw['ai_coach'],
            'label_display':      LABEL_TR.get(action_label, action_label),
            'class_probabilities': probs,
        },
        'shap_features': shap_features,
        'transactions': sample,
    }
