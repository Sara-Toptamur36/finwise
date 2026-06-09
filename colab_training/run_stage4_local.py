from imblearn.over_sampling import SMOTE

import os
import sys

BASE = r'c:\Users\sarat\Desktop\veri_seti\colab_training'
DATA_DIR = f'{BASE}\data'
OUT_DIR  = f'{BASE}\outputs'
os.makedirs(OUT_DIR, exist_ok=True)
print(f'DATA_DIR: {DATA_DIR}')
print(f'OUT_DIR : {OUT_DIR}')


import numpy as np
import pandas as pd
import json
import warnings
warnings.filterwarnings('ignore')

ACTION_CLASSES = [
    'EMERGENCY_WARNING','HIGH_DEBT_RISK','NEEDS_BUDGETING',
    'SAVE_MORE','GREAT_SAVER','ON_TRACK'
]
ACT2ID = {a: i for i, a in enumerate(ACTION_CLASSES)}
ID2ACT = {i: a for a, i in ACT2ID.items()}

# ── User-monthly feature matrisi ──────────────────────────────
um_enriched = f'{OUT_DIR}/stage2_user_monthly_enriched.csv'
um_base     = f'{DATA_DIR}/stage2_user_monthly_features.csv'
if os.path.exists(um_enriched):
    user_monthly = pd.read_csv(um_enriched, encoding='utf-8-sig')
    print(f'Zenginleştirilmiş veri: {user_monthly.shape}')
elif os.path.exists(um_base):
    user_monthly = pd.read_csv(um_base, encoding='utf-8-sig')
    print(f'Temel veri: {user_monthly.shape}')
else:
    raise FileNotFoundError('stage2_user_monthly_features.csv bulunamadı!')

# ── ETİKET KAYNAĞI (öncelik sırası) ──────────────────────────
coached_path = f'{DATA_DIR}/stage4_coached_users.csv'
syn_path     = f'{DATA_DIR}/synthetic_budget_data.csv'

label_source = 'unknown'

if os.path.exists(coached_path):
    df_c = pd.read_csv(coached_path, encoding='utf-8-sig', low_memory=False)
    action_col = next((c for c in df_c.columns
                       if any(k in c.lower() for k in ['action','aksiyon','recommended'])), None)
    if action_col:
        coached_lbl = df_c.groupby('user_id')[action_col].agg(lambda x: x.mode()[0]).reset_index()
        coached_lbl.columns = ['user_id','recommended_action']
        user_monthly = user_monthly.drop(columns=['recommended_action'], errors='ignore')
        user_monthly = user_monthly.merge(coached_lbl, on='user_id', how='left')
        label_source = 'stage4_coached_users.csv'
        print(f'stage4_coached_users.csv ETİKETLERİ KULLANILDı: {coached_lbl["recommended_action"].value_counts().to_string()}')

if label_source == 'unknown' or user_monthly.get('recommended_action', pd.Series()).isna().all():
    if os.path.exists(syn_path):
        df_syn = pd.read_csv(syn_path, encoding='utf-8-sig',
                             usecols=['user_id','recommended_action','available_balance',
                                      'credit_utilization','debt_to_income_ratio','cashflow_health_score'],
                             low_memory=False)
        lbl_df = df_syn.groupby('user_id').agg(
            recommended_action   =('recommended_action',   lambda x: x.mode()[0]),
            available_balance    =('available_balance',    'mean'),
            credit_utilization   =('credit_utilization',   'mean'),
            debt_to_income_ratio =('debt_to_income_ratio', 'mean'),
            cashflow_health_score=('cashflow_health_score','mean')
        ).reset_index()
        user_monthly = user_monthly.drop(columns=['recommended_action'], errors='ignore')
        user_monthly = user_monthly.merge(lbl_df, on='user_id', how='left')
        label_source = 'synthetic_budget_data.csv'

if 'recommended_action' not in user_monthly.columns or user_monthly['recommended_action'].isna().all():
    print('Kural motoru ile etiket oluşturuluyor...')
    def rule(r):
        bu=r.get('budget_utilisation',0); sr=r.get('savings_rate',0)
        eat=r.get('share_YEME_ICME',0);   shop=r.get('share_ALISVERIS',0)
        if bu>=1.4:   return 'EMERGENCY_WARNING'
        if bu>=1.05:  return 'HIGH_DEBT_RISK'
        if eat>0.12:  return 'REDUCE_EATING_OUT'
        if shop>0.10: return 'REDUCE_SHOPPING'
        if sr<0.05:   return 'INCREASE_SAVINGS'
        if sr<0.20:   return 'SAVE_MORE'
        if sr>=0.40:  return 'GREAT_SAVER'
        return 'ON_TRACK'
    user_monthly['recommended_action'] = user_monthly.apply(rule, axis=1)
    label_source = 'kural_motoru'

print(f'\nEtiket kaynağı: {label_source}')
print(user_monthly['recommended_action'].value_counts().to_string())

# ── FEATURE & LABEL HAZIRLAMA ──────────────────────────────────
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, f1_score, accuracy_score

# Azınlık sınıflarını (Bütçeleme Gerekiyor) tek sınıfta birleştir
merge_classes = ['REDUCE_EATING_OUT', 'REDUCE_SHOPPING', 'REDUCE_ENTERTAINMENT', 'INCREASE_SAVINGS']
user_monthly.loc[user_monthly['recommended_action'].isin(merge_classes), 'recommended_action'] = 'NEEDS_BUDGETING'

um = user_monthly[user_monthly['recommended_action'].notna()].copy()
um = um[um['recommended_action'].isin(ACTION_CLASSES)].copy()
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
um['label'] = le.fit_transform(um['recommended_action'])
ID2ACT = {i: c for i, c in enumerate(le.classes_)}


print(f'Toplam örnek: {len(um):,}')
print(um['recommended_action'].value_counts().to_string())

# Lag & cyclic features
um = um.sort_values(['user_id','year_month'])
for lag in [1,2,3]:
    um[f'expense_lag{lag}'] = um.groupby('user_id')['monthly_expense_computed'].shift(lag).fillna(0)
    um[f'income_lag{lag}']  = um.groupby('user_id')['monthly_income_computed'].shift(lag).fillna(0)
    um[f'savings_lag{lag}'] = um.groupby('user_id')['savings_rate'].shift(lag).fillna(0)

um['period_month'] = pd.to_datetime(um['year_month'], format='%Y-%m', errors='coerce').dt.month.fillna(1)
um['month_sin'] = np.sin(2*np.pi*um['period_month']/12)
um['month_cos'] = np.cos(2*np.pi*um['period_month']/12)

FEATURE_COLS = ['monthly_income_computed','monthly_expense_computed',
                'savings_rate','budget_utilisation','net_cashflow',
                'expense_lag1','expense_lag2','expense_lag3',
                'income_lag1','savings_lag1','savings_lag2',
                'month_sin','month_cos']
extra = ['available_balance','credit_utilization','debt_to_income_ratio',
         'cashflow_health_score','cluster','anomaly_score',
         'expense_rolling3m_mean','expense_rolling3m_std','txn_count']
share_cols = [c for c in um.columns if c.startswith('share_')]
spend_cols = [c for c in um.columns if c.startswith('spend_')][:8]
FEATURE_COLS += [c for c in extra+share_cols+spend_cols if c in um.columns]
FEATURE_COLS = list(dict.fromkeys([c for c in FEATURE_COLS if c in um.columns]))

X = um[FEATURE_COLS].fillna(0)
y = um['label']
print(f'\nX: {X.shape} | {len(FEATURE_COLS)} özellik')

# ── STRATIFIED K-FOLD CV ──────────────────────────────────────
import xgboost as xgb

print('Stratified K-Fold CV başlıyor...')
N_SPLITS = 5
skf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=42)
cv_acc, cv_f1 = [], []

for fold, (tr_idx, te_idx) in enumerate(skf.split(X, y), 1):
    X_tr, X_te = X.iloc[tr_idx], X.iloc[te_idx]
    y_tr, y_te = y.iloc[tr_idx], y.iloc[te_idx]
    clf = xgb.XGBClassifier(
        n_estimators=400, learning_rate=0.03, max_depth=4,
        subsample=0.8, colsample_bytree=0.6,
        reg_alpha=0.5, reg_lambda=1.5, gamma=1.0, min_child_weight=2,
        use_label_encoder=False, eval_metric='mlogloss',
        random_state=42, n_jobs=-1, verbosity=0
    )
    # Kullanıcı talebi üzerine ROS yerine SMOTE'a (k_neighbors=2) geri dönüldü
    from imblearn.over_sampling import SMOTE
    smote = SMOTE(random_state=42, k_neighbors=2)
    X_tr_sm, y_tr_sm = smote.fit_resample(X_tr, y_tr)
    
    clf.fit(X_tr_sm, y_tr_sm, eval_set=[(X_te, y_te)],
            verbose=False)
    preds = clf.predict(X_te)
    acc = accuracy_score(y_te, preds)
    f1  = f1_score(y_te, preds, average='macro', zero_division=0)
    cv_acc.append(acc)
    cv_f1.append(f1)
    print(f'  Fold {fold}/{N_SPLITS}: Acc={acc:.4f}  F1={f1:.4f}')

print(f'\nCV Acc  : {np.mean(cv_acc):.4f} ± {np.std(cv_acc):.4f}')
print(f'CV F1   : {np.mean(cv_f1):.4f} ± {np.std(cv_f1):.4f}')

# ── FİNAL MODEL ───────────────────────────────────────────────
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.20, stratify=y, random_state=42)

final_clf = xgb.XGBClassifier(
    n_estimators=400, learning_rate=0.03, max_depth=4,
    subsample=0.8, colsample_bytree=0.6,
    reg_alpha=0.5, reg_lambda=1.5, gamma=1.0, min_child_weight=2,
    random_state=42,
    early_stopping_rounds=50,
    eval_metric='mlogloss'
)

# Apply SMOTE to final training data as well to be consistent
from imblearn.over_sampling import SMOTE
smote_final = SMOTE(random_state=42, k_neighbors=2)
X_tr_sm_f, y_tr_sm_f = smote_final.fit_resample(X_tr, y_tr)

final_clf.fit(X_tr_sm_f, y_tr_sm_f, eval_set=[(X_te, y_te)],
              verbose=False)

preds    = final_clf.predict(X_te)
test_acc = accuracy_score(y_te, preds)
test_f1  = f1_score(y_te, preds, average='macro', zero_division=0)
print(f'\nTest Acc: {test_acc:.4f} | Test F1: {test_f1:.4f}')
print(classification_report(y_te, preds,
      target_names=[ID2ACT[i] for i in range(len(ID2ACT))],
      digits=4, zero_division=0))

# ── CONFUSION MATRIX ──────────────────────────────────────────
import matplotlib.pyplot as plt
import seaborn as sns

present = sorted(y_te.unique())
names   = [ID2ACT[i] for i in present]
cm      = confusion_matrix(y_te, preds, labels=present)
cm_norm = cm.astype('float') / (cm.sum(axis=1, keepdims=True) + 1e-9)

fig, ax = plt.subplots(figsize=(14, 11))
sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues',
            xticklabels=names, yticklabels=names,
            linewidths=0.3, ax=ax, vmin=0, vmax=1)
ax.set_title(f'XGBoost Koçluk — Confusion Matrix\nAcc={test_acc:.3f}  F1={test_f1:.3f}\nEtiket Kaynağı: {label_source}',
             fontsize=12, pad=15)
ax.set_xlabel('Tahmin', fontsize=11)
ax.set_ylabel('Gerçek', fontsize=11)
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()
cm_path = f'{OUT_DIR}/stage4_xgb_confusion_matrix.png'
plt.savefig(cm_path, dpi=150, bbox_inches='tight')
plt.close()
print(f'Kaydedildi: {cm_path}')

# ── FEATURE IMPORTANCE ────────────────────────────────────────
fi = pd.Series(final_clf.feature_importances_, index=FEATURE_COLS).sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(10, 8))
fi.head(20).plot(kind='barh', ax=ax, color='#9B59B6', edgecolor='white')
ax.invert_yaxis()
ax.set_title('XGBoost Top 20 Feature Importance', fontsize=12)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/stage4_xgb_feature_importance.png', dpi=150, bbox_inches='tight')
plt.close()

# ── SHAP ──────────────────────────────────────────────────────
import shap
explainer   = shap.TreeExplainer(final_clf)
N_SHAP      = min(800, len(X_te))
X_shap      = X_te.sample(N_SHAP, random_state=42)
shap_values = explainer.shap_values(X_shap)

plt.figure(figsize=(10, 7))
shap.summary_plot(shap_values, X_shap, plot_type='bar', max_display=20, show=False)
plt.title('SHAP — XGBoost Koçluk Modeli', fontsize=11)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/stage4_shap_importance.png', dpi=150, bbox_inches='tight')
plt.close()

# ── CV GRAFİĞİ ────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
folds = list(range(1, N_SPLITS+1))
w = 0.35
ax.bar([f-w/2 for f in folds], cv_acc, w, label='Accuracy', color='#3498DB', alpha=0.85)
ax.bar([f+w/2 for f in folds], cv_f1,  w, label='Macro-F1', color='#27AE60', alpha=0.85)
ax.axhline(np.mean(cv_acc), color='#3498DB', linestyle='--', linewidth=1.5,
           label=f'Ort.Acc={np.mean(cv_acc):.3f}')
ax.axhline(np.mean(cv_f1), color='#27AE60', linestyle='--', linewidth=1.5,
           label=f'Ort.F1={np.mean(cv_f1):.3f}')
ax.set_title('XGBoost — Stratified K-Fold CV', fontsize=12)
ax.set_xlabel('Fold'); ax.set_ylabel('Skor'); ax.set_ylim(0, 1.05)
ax.legend(); ax.set_xticks(folds)
plt.tight_layout()
plt.savefig(f'{OUT_DIR}/stage4_cv_scores.png', dpi=150, bbox_inches='tight')
plt.close()

# ── SONUÇLARI KAYDET ──────────────────────────────────────────
import pickle
from sklearn.metrics import precision_recall_fscore_support

pickle.dump(final_clf, open(f'{OUT_DIR}/xgboost_coach_model.pkl','wb'))

p, r, f, s = precision_recall_fscore_support(y_te, preds,
    labels=list(range(len(ID2ACT))), zero_division=0)

results = {
    'model'          : 'XGBoost Classifier',
    'label_source'   : label_source,
    'test_accuracy'  : float(test_acc),
    'test_macro_f1'  : float(test_f1),
    'cv_accuracy_mean': float(np.mean(cv_acc)),
    'cv_accuracy_std' : float(np.std(cv_acc)),
    'cv_f1_mean'     : float(np.mean(cv_f1)),
    'cv_f1_std'      : float(np.std(cv_f1)),
    'n_features'     : len(FEATURE_COLS),
    'feature_cols'   : FEATURE_COLS,
    'per_class'      : {}
}
for i in range(len(ID2ACT)):
    results['per_class'][le.classes_[i]] = {'precision':float(p[i]),'recall':float(r[i]),
                                            'f1':float(f[i]),'support':int(s[i])}

with open(f'{OUT_DIR}/stage4_xgb_results.json','w',encoding='utf-8') as fh:
    json.dump(results, fh, indent=2, ensure_ascii=False)

fi.reset_index().rename(columns={'index':'feature',0:'importance'}).to_csv(
    f'{OUT_DIR}/stage4_feature_importance.csv', index=False)

print('\n=== STAGE 4 ÖZET ===')
print(f'  Etiket Kaynağı : {label_source}')
print(f'  Test Acc       : {test_acc:.4f}')
print(f'  Test F1        : {test_f1:.4f}')
print(f'  CV Acc         : {np.mean(cv_acc):.4f} ± {np.std(cv_acc):.4f}')
print(f'  CV F1          : {np.mean(cv_f1):.4f} ± {np.std(cv_f1):.4f}')
print(f'  Top Özellik    : {fi.index[0]}')
print('\nDosyalar:')
for fn in sorted(os.listdir(OUT_DIR)):
    sz = os.path.getsize(f'{OUT_DIR}/{fn}') / 1024
    print(f'  {fn}  ({sz:.1f} KB)')