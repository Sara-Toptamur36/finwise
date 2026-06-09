# -*- coding: utf-8 -*-
"""
Demo endpoint'leri — önceden hesaplanmış persona sonuçları
"""
import os, json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

PARENT = os.path.join(os.path.dirname(__file__), "..", "..")

# Demo personaları (ön hesaplanmış sonuçlar)
DEMO_RESULTS = {
    "ahmet": {
        "persona": {
            "id": "ahmet",
            "name": "Ahmet Bey",
            "subtitle": "Yüksek Bütçe Riski",
            "description": "Geliri sabit, son aylarda giderleri artmış, yeme-içme ve market harcaması yükseldi.",
            "avatar": "A",
        },
        "summary": {
            "total_income":      35000.0,
            "total_expense":     37300.0,
            "net_cashflow":      -2300.0,
            "savings_rate_pct":  -6.6,
            "txn_count":         195,
            "categorized_count": 188,
            "avg_confidence":    0.91,
            "uncategorized_count": 7,
        },
        "user_profile": {
            "cluster_id":        2,
            "cluster_name":      "Riskli Harcayıcılar",
            "spending_rhythm":   "Hafta sonu harcayıcı",
            "dominant_category": "MARKET",
            "cash_flow":         "Negatif",
            "savings_trend":     "Düşme",
        },
        "category_breakdown": {
            "MARKET":         9200.0,
            "YEME_ICME":      6800.0,
            "ALISVERIS":      5400.0,
            "FATURA":         4200.0,
            "ULASIM":         3100.0,
            "EGLENCE":        2800.0,
            "BANKA_KESINTISI":2400.0,
            "SAGLIK":         1600.0,
            "NAKIT_ISLEMLERI":1200.0,
            "DIGER":           600.0,
        },
        "monthly_trend": [
            {"month": "2026-01", "income": 35000, "expense": 29800},
            {"month": "2026-02", "income": 35000, "expense": 32100},
            {"month": "2026-03", "income": 35000, "expense": 34600},
            {"month": "2026-04", "income": 35000, "expense": 35900},
            {"month": "2026-05", "income": 35000, "expense": 36400},
            {"month": "2026-06", "income": 35000, "expense": 37300},
        ],
        "ai_forecast": {
            "next_month_expected_expense": 38750.0,
            "trend": "Artış",
        },
        "ai_coach": {
            "action_label":        "HIGH_DEBT_RISK",
            "label_display":       "Riskli",
            "personalized_message":"KIRMIZI ALARM: Gelirinizden fazlasını harcayıp borç sarmalına giriyorsunuz! En büyük risk market ve yeme-içme kategorilerinde.",
            "class_probabilities": {"GREAT_SAVER": 0.05, "NEEDS_BUDGETING": 0.23, "HIGH_DEBT_RISK": 0.72},
        },
        "shap_features": [
            {"feature":"net_cashflow",           "display":"Net nakit akışı",           "value":-2300,"unit":"TL", "direction":"risk","importance":0.38},
            {"feature":"savings_rate",            "display":"Tasarruf oranı",            "value":-6.6, "unit":"%",  "direction":"risk","importance":0.25},
            {"feature":"expense_rolling3m_mean",  "display":"Son 3 ay gider ortalaması","value":35400,"unit":"TL", "direction":"risk","importance":0.18},
            {"feature":"monthly_income_computed", "display":"Düzenli gelir",            "value":35000,"unit":"TL", "direction":"safe","importance":0.10},
            {"feature":"spend_MARKET",            "display":"Market harcaması",         "value":9200, "unit":"TL", "direction":"risk","importance":0.09},
        ],
        "transactions": [
            {"tarih":"2026-06-01","aciklama":"BIM BIRLESIK MAGAZALAR","tutar":485.6, "is_income":False,"predicted_category":"MARKET",    "decision_path":"Regex","confidence":0.99},
            {"tarih":"2026-06-02","aciklama":"MIGROS AS",             "tutar":920.0, "is_income":False,"predicted_category":"MARKET",    "decision_path":"Regex","confidence":0.99},
            {"tarih":"2026-06-03","aciklama":"TRENDYOL ALISVERIS",   "tutar":2150.0,"is_income":False,"predicted_category":"ALISVERIS",  "decision_path":"SVC",  "confidence":0.93},
            {"tarih":"2026-06-05","aciklama":"MAAS ODEMESI",          "tutar":35000.0,"is_income":True,"predicted_category":"VIRMAN",   "decision_path":"Regex","confidence":0.99},
            {"tarih":"2026-06-08","aciklama":"STARBUCKS KAFE",        "tutar":250.0, "is_income":False,"predicted_category":"YEME_ICME", "decision_path":"Regex","confidence":0.99},
            {"tarih":"2026-06-10","aciklama":"ZXM CRYPT 992",         "tutar":180.0, "is_income":False,"predicted_category":"DIGER",     "decision_path":"Güvenli Bekletme","confidence":0.42},
            {"tarih":"2026-06-12","aciklama":"NETFLIX ODEME",         "tutar":150.0, "is_income":False,"predicted_category":"EGLENCE",   "decision_path":"Regex","confidence":0.99},
        ],
    },
    "ayse": {
        "persona": {
            "id": "ayse",
            "name": "Ayşe Hanım",
            "subtitle": "Tasarrufçu Profil",
            "description": "Gelir-gider dengesi pozitif, düzenli tasarruf eğilimi var.",
            "avatar": "A",
        },
        "summary": {
            "total_income":      42000.0,
            "total_expense":     22100.0,
            "net_cashflow":      19900.0,
            "savings_rate_pct":  47.4,
            "txn_count":         66,
            "categorized_count": 65,
            "avg_confidence":    0.94,
            "uncategorized_count": 1,
        },
        "user_profile": {
            "cluster_id":        1,
            "cluster_name":      "Güçlü Tasarrufçular",
            "spending_rhythm":   "Hafta içi harcayıcı",
            "dominant_category": "FATURA",
            "cash_flow":         "Pozitif",
            "savings_trend":     "Yükselme",
        },
        "category_breakdown": {
            "FATURA":         4800.0,
            "MARKET":         3900.0,
            "ULASIM":         2800.0,
            "YEME_ICME":      2200.0,
            "ALISVERIS":      2000.0,
            "BANKA_KESINTISI":1800.0,
            "SAGLIK":         1600.0,
            "EGLENCE":        1200.0,
            "NAKIT_ISLEMLERI": 900.0,
            "DIGER":           900.0,
        },
        "monthly_trend": [
            {"month": "2026-01", "income": 42000, "expense": 20100},
            {"month": "2026-02", "income": 42000, "expense": 21500},
            {"month": "2026-03", "income": 42000, "expense": 19800},
            {"month": "2026-04", "income": 42000, "expense": 22400},
            {"month": "2026-05", "income": 42000, "expense": 21200},
            {"month": "2026-06", "income": 42000, "expense": 22100},
        ],
        "ai_forecast": {
            "next_month_expected_expense": 21500.0,
            "trend": "Azalış",
        },
        "ai_coach": {
            "action_label":        "GREAT_SAVER",
            "label_display":       "Tasarrufçu",
            "personalized_message":"Harika! Bütçenizi çok iyi yönetiyor ve tasarruf ediyorsunuz. Gelirinizin %47'sini biriktiriyorsunuz.",
            "class_probabilities": {"GREAT_SAVER": 0.80, "NEEDS_BUDGETING": 0.15, "HIGH_DEBT_RISK": 0.05},
        },
        "shap_features": [
            {"feature":"net_cashflow",           "display":"Net nakit akışı",           "value":19900,"unit":"TL", "direction":"safe","importance":0.40},
            {"feature":"savings_rate",            "display":"Tasarruf oranı",            "value":47.4, "unit":"%",  "direction":"safe","importance":0.28},
            {"feature":"expense_rolling3m_mean",  "display":"Son 3 ay gider ortalaması","value":21100,"unit":"TL", "direction":"safe","importance":0.15},
            {"feature":"monthly_income_computed", "display":"Düzenli gelir",            "value":42000,"unit":"TL", "direction":"safe","importance":0.12},
            {"feature":"spend_MARKET",            "display":"Market harcaması",         "value":3900, "unit":"TL", "direction":"neutral","importance":0.05},
        ],
        "transactions": [
            {"tarih":"2026-06-02","aciklama":"PETROLOFISI",            "tutar":563.37,"is_income":False,"predicted_category":"ULASIM",    "decision_path":"Regex","confidence":0.99},
            {"tarih":"2026-06-05","aciklama":"MAAS ODEMESI",           "tutar":42000.0,"is_income":True,"predicted_category":"VIRMAN",   "decision_path":"Regex","confidence":0.99},
            {"tarih":"2026-06-08","aciklama":"MIGROS AS",              "tutar":780.0, "is_income":False,"predicted_category":"MARKET",    "decision_path":"Regex","confidence":0.99},
            {"tarih":"2026-06-10","aciklama":"INTERNET FATURASI",      "tutar":450.0, "is_income":False,"predicted_category":"FATURA",    "decision_path":"Regex","confidence":0.99},
            {"tarih":"2026-06-15","aciklama":"RESTAURANT SOFRA",       "tutar":320.0, "is_income":False,"predicted_category":"YEME_ICME", "decision_path":"SVC",  "confidence":0.87},
        ],
    },
    "zeynep": {
        "persona": {
            "id": "zeynep",
            "name": "Zeynep Hanım",
            "subtitle": "Bütçeleme Yapmalı",
            "description": "Geliri yeterli ancak harcama dağılımı dengesiz.",
            "avatar": "Z",
        },
        "summary": {
            "total_income":      28000.0,
            "total_expense":     26500.0,
            "net_cashflow":      1500.0,
            "savings_rate_pct":  5.4,
            "txn_count":         123,
            "categorized_count": 119,
            "avg_confidence":    0.89,
            "uncategorized_count": 4,
        },
        "user_profile": {
            "cluster_id":        3,
            "cluster_name":      "Dengeli Tasarrufçular",
            "spending_rhythm":   "Hafta sonu yoğunlaşma",
            "dominant_category": "YEME_ICME",
            "cash_flow":         "Pozitif",
            "savings_trend":     "Dengesiz",
        },
        "category_breakdown": {
            "YEME_ICME":      6200.0,
            "MARKET":         5400.0,
            "ALISVERIS":      4800.0,
            "FATURA":         3200.0,
            "ULASIM":         2600.0,
            "BANKA_KESINTISI":1800.0,
            "EGLENCE":        1200.0,
            "SAGLIK":          900.0,
            "DIGER":           400.0,
        },
        "monthly_trend": [
            {"month": "2026-01", "income": 28000, "expense": 22800},
            {"month": "2026-02", "income": 28000, "expense": 24100},
            {"month": "2026-03", "income": 28000, "expense": 25200},
            {"month": "2026-04", "income": 28000, "expense": 25800},
            {"month": "2026-05", "income": 28000, "expense": 26100},
            {"month": "2026-06", "income": 28000, "expense": 26500},
        ],
        "ai_forecast": {
            "next_month_expected_expense": 27800.0,
            "trend": "Artış",
        },
        "ai_coach": {
            "action_label":        "NEEDS_BUDGETING",
            "label_display":       "Bütçeleme Yapmalı",
            "personalized_message":"Bütçenizi kontrol etmeniz gerekiyor. Bu ay en büyük değişken harcamanız yeme-içme kategorisinde. Kısıntıya gidin.",
            "class_probabilities": {"GREAT_SAVER": 0.10, "NEEDS_BUDGETING": 0.68, "HIGH_DEBT_RISK": 0.22},
        },
        "shap_features": [
            {"feature":"net_cashflow",           "display":"Net nakit akışı",           "value":1500,"unit":"TL","direction":"neutral","importance":0.32},
            {"feature":"savings_rate",            "display":"Tasarruf oranı",            "value":5.4, "unit":"%", "direction":"risk",   "importance":0.26},
            {"feature":"expense_rolling3m_mean",  "display":"Son 3 ay gider ortalaması","value":25000,"unit":"TL","direction":"risk",  "importance":0.20},
            {"feature":"monthly_income_computed", "display":"Düzenli gelir",            "value":28000,"unit":"TL","direction":"safe",  "importance":0.12},
            {"feature":"spend_YEME_ICME",         "display":"Yeme-içme harcaması",      "value":6200,"unit":"TL","direction":"risk",   "importance":0.10},
        ],
        "transactions": [
            {"tarih":"2026-06-01","aciklama":"CARREFOURSA",          "tutar":402.05,"is_income":False,"predicted_category":"MARKET",   "decision_path":"Regex","confidence":0.99},
            {"tarih":"2026-06-05","aciklama":"MAAS ODEMESI",          "tutar":28000.0,"is_income":True,"predicted_category":"VIRMAN",  "decision_path":"Regex","confidence":0.99},
            {"tarih":"2026-06-07","aciklama":"KADAYIFCI MURAT",       "tutar":320.0, "is_income":False,"predicted_category":"YEME_ICME","decision_path":"SVC", "confidence":0.88},
            {"tarih":"2026-06-09","aciklama":"ZARA GIYIM",            "tutar":1800.0,"is_income":False,"predicted_category":"ALISVERIS","decision_path":"SVC", "confidence":0.91},
            {"tarih":"2026-06-11","aciklama":"ELEKTRIK FATURASI",     "tutar":680.0, "is_income":False,"predicted_category":"FATURA",  "decision_path":"Regex","confidence":0.99},
        ],
    },
}


@router.get("/personas")
async def list_personas():
    return [v["persona"] for v in DEMO_RESULTS.values()]


@router.get("/analyze/{persona_id}")
async def demo_analyze(persona_id: str):
    if persona_id not in DEMO_RESULTS:
        raise HTTPException(404, f"Demo persona bulunamadı: {persona_id}")
    return DEMO_RESULTS[persona_id]
