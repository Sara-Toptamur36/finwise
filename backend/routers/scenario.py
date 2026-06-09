# -*- coding: utf-8 -*-
"""
Senaryo Testi endpoint'i — finansal simulasyon
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter()

LABEL_TR = {
    'HIGH_DEBT_RISK':  'Riskli',
    'NEEDS_BUDGETING': 'Butceleme Yapmali',
    'GREAT_SAVER':     'Tasarrufcu',
}


class ScenarioRequest(BaseModel):
    # Mevcut degerler
    income:          float
    expense:         float
    savings_rate:    float
    net_cashflow:    float
    action_label:    str
    class_probs:     dict

    # Degisim yuzdesi (-50 ile +50 arasi)
    income_change_pct:   float = Field(default=0.0, ge=-50, le=50)
    expense_change_pct:  float = Field(default=0.0, ge=-50, le=50)
    market_change_pct:   float = Field(default=0.0, ge=-50, le=50)
    yemek_change_pct:    float = Field(default=0.0, ge=-50, le=50)
    savings_change_pct:  float = Field(default=0.0, ge=-30, le=30)


def _classify(savings_rate: float, net_cashflow: float, budget_util: float) -> tuple:
    """Basit kural tabanli siniflandirma."""
    if savings_rate >= 0.20 and net_cashflow > 0:
        label = 'GREAT_SAVER'
        probs = {'GREAT_SAVER': max(0.5, min(0.95, 0.4 + savings_rate)), 'NEEDS_BUDGETING': 0.15, 'HIGH_DEBT_RISK': 0.05}
    elif net_cashflow < 0 or budget_util > 1.05:
        label = 'HIGH_DEBT_RISK'
        risk  = min(0.95, 0.4 + abs(net_cashflow) / 10000)
        probs = {'GREAT_SAVER': 0.05, 'NEEDS_BUDGETING': max(0.05, 0.95 - risk), 'HIGH_DEBT_RISK': risk}
    else:
        label = 'NEEDS_BUDGETING'
        nb    = min(0.90, 0.3 + (1 - savings_rate))
        probs = {'GREAT_SAVER': max(0.05, 1 - nb - 0.15), 'NEEDS_BUDGETING': nb, 'HIGH_DEBT_RISK': max(0.05, 1 - nb - 0.10)}

    # Normalize
    total = sum(probs.values())
    probs = {k: round(v / total, 3) for k, v in probs.items()}
    return label, probs


def _confidence_level(income_ch: float, expense_ch: float) -> str:
    total_change = abs(income_ch) + abs(expense_ch)
    if total_change <= 20:
        return "Yuksek"
    elif total_change <= 35:
        return "Orta"
    else:
        return "Dusuk"


@router.post("/test")
async def scenario_test(req: ScenarioRequest):
    # Senaryo degerlerini hesapla
    new_income  = req.income  * (1 + req.income_change_pct  / 100)
    new_expense = req.expense * (1 + req.expense_change_pct / 100)
    new_cashflow    = new_income - new_expense
    new_savings_rate = new_cashflow / new_income if new_income > 0 else 0
    new_budget_util  = new_expense / new_income if new_income > 0 else 999
    new_forecast     = new_expense * 1.035

    new_label, new_probs = _classify(new_savings_rate, new_cashflow, new_budget_util)
    confidence = _confidence_level(req.income_change_pct, req.expense_change_pct)

    # Degisim senaryosu OOD kontrolu
    total_change = abs(req.income_change_pct) + abs(req.expense_change_pct) + abs(req.market_change_pct) + abs(req.yemek_change_pct)
    ood_warning = total_change > 40

    # Metinsel oneri
    improvement = req.class_probs.get('HIGH_DEBT_RISK', 0) - new_probs.get('HIGH_DEBT_RISK', 0)
    if improvement > 0.1:
        narrative = (
            f"Bu senaryoda giderlerinizi %{abs(req.expense_change_pct):.0f} azaltmaniz, "
            f"Riskli sinif olasiligini %{req.class_probs.get('HIGH_DEBT_RISK',0)*100:.0f}'den "
            f"%{new_probs.get('HIGH_DEBT_RISK',0)*100:.0f}'e dusurdu. "
            f"Net nakit akisiniz {new_cashflow:+.0f} TL seviyesine yukseliyor."
        )
    elif new_label == 'GREAT_SAVER' and req.action_label != 'GREAT_SAVER':
        narrative = (
            f"Bu degisiklikler sizi Tasarrufcu segmentine tasidi. "
            f"Tasarruf oraniniz %{new_savings_rate*100:.1f}'e yukseldi."
        )
    else:
        narrative = (
            f"Senaryo degerlendirmesi: Net nakit akisiniz {new_cashflow:+.0f} TL, "
            f"tasarruf oraniniz %{new_savings_rate*100:.1f} olarak hesaplandi."
        )

    return {
        "current": {
            "action_label":    req.action_label,
            "label_display":   LABEL_TR.get(req.action_label, req.action_label),
            "income":          req.income,
            "expense":         req.expense,
            "net_cashflow":    req.net_cashflow,
            "savings_rate_pct": round(req.savings_rate * 100, 1),
            "class_probs":     req.class_probs,
        },
        "scenario": {
            "action_label":    new_label,
            "label_display":   LABEL_TR.get(new_label, new_label),
            "income":          round(new_income, 0),
            "expense":         round(new_expense, 0),
            "net_cashflow":    round(new_cashflow, 0),
            "savings_rate_pct": round(new_savings_rate * 100, 1),
            "forecast":        round(new_forecast, 0),
            "class_probs":     new_probs,
        },
        "confidence_level": confidence,
        "ood_warning":       ood_warning,
        "narrative":         narrative,
    }
