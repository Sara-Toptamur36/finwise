"""Kural motorunu test et"""
import json, re

nb_path = r'c:\Users\sarat\Desktop\veri_seti\colab_training\01_stage1_bert_classifier.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']
c3 = ''.join(cells[3]['source'])
c10 = ''.join(cells[10]['source'])
c11 = ''.join(cells[11]['source'])

# _RULES listesini al ve calistir
exec_globals = {'re': re}
# c3'ten sadece _RULES ve rule_clf kismini calistir
exec(c3, exec_globals)

rule_clf_fn = exec_globals['rule_clf']

test_cases = [
    ('MIGROS YEMEK SIPARIS', 'YEME_ICME'),
    ('MIGROSYEMEK ISTANBUL', 'YEME_ICME'),
    ('MIGROSEATS TR', 'YEME_ICME'),
    ('MONEYPAY MIGROS YEMEK', 'YEME_ICME'),
    ('MIGROS MARKET ALISVERIS', 'MARKET'),
    ('MIGROS BIM A101', 'MARKET'),
    ('GETIR YEMEK SIPARIS', 'YEME_ICME'),
    ('GETIRYEMEK ODEME', 'YEME_ICME'),
    ('GETIRGO ISTANBUL', 'YEME_ICME'),
    ('GETIR GO YEMEK', 'YEME_ICME'),
    ('GETIR MARKET SIPARIS', 'MARKET'),
    ('TRENDYOLYEM SIPARIS', 'YEME_ICME'),
    ('TRENDYOL YEM ODEME', 'YEME_ICME'),
    ('TRENDYOL GO YEMEK', 'YEME_ICME'),
    ('TRENDYOLGO ISTANBUL', 'YEME_ICME'),
    ('GOOGLE PLAY STORE OYUN', 'EGLENCE'),
    ('HAVALE GOOGLE PAY EFT', 'VIRMAN'),   # VIRMAN > EGLENCE: HAVALE once geliyor
    ('KREDI KARTI ODEME FATURA', 'FATURA'), # FATURA > BANKA_KES
]

print('=== KURAL MOTORU TESTI ===')
all_pass = True
for text, expected in test_cases:
    result = rule_clf_fn(text)
    ok = result == expected
    if not ok: all_pass = False
    icon = 'OK' if ok else 'HATA'
    print(f'  [{icon}] {text:45s} -> {result:20s} (beklenen: {expected})')

print()
if all_pass:
    print('TUM KURAL TESTLERI GECTI!')
else:
    print('BAZI TESTLER BASARISIZ')

print()
print('=== DİĞER KONTROLLER ===')
diger_40 = "'DIGER'           : 40" in c3
print(f"  DIGER TIER=40: {'OK' if diger_40 else 'HATA'}")
conf_ok = '0.55' in c10 and '0.70' not in c10 and '0.65' not in c10
print(f"  conf.thr max 0.55: {'OK' if conf_ok else 'HATA'}")
trend_aug = 'TRENDYOLYEM' in c11 and 'MIGROSYEMEK' in c11 and 'GETIRYEMEK' in c11
print(f"  YEME_ICME AUG (TRENDYOLYEM/MIGROSYEMEK/GETIRYEMEK): {'OK' if trend_aug else 'HATA'}")
person_gone = 'PERSON NAME' not in c11
print(f"  DIGER AUG sahis ismi kaldirildi: {'OK' if person_gone else 'HATA'}")
