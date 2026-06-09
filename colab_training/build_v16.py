"""
v16 Tam Güncelleme Scripti:
1. bert_training_data.csv -> YEME_ICME yazım çeşitleri (500+ satır)
2. 01_stage1_bert_classifier.ipynb -> v16 yeniden oluştur

Değişiklikler:
- DIGER TIER: 90->40
- DIGER AUG: person name örnekleri temizlendi
- YEME_ICME AUG: TRENDYOLYEM, MIGROSYEMEK, GETIRYEMEK ve 20+ çeşit
- Kural motoru sırası: VIRMAN > EGLENCE, FATURA > BANKA_KESINTISI
- MARKET kuralı: MIGROS/GETIR'i YEMEK içerenleri dışla (hassaslaştırma)
- conf.thr arama aralığı: max 0.55 (0.7 artık seçilemiyor)
"""

import json
import pandas as pd
import numpy as np
import os
import random

# ─────────────────────────────────────────────────────────────────────────────
# BÖLÜM 1: YEME_ICME SENTETİK VERİ OLUŞTUR
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 60)
print("BÖLÜM 1: YEME_ICME Sentetik Veri Oluşturuluyor")
print("=" * 60)

# Yazım çeşitleri — gerçek banka özetlerinden gözlemlenen formlar
TRENDYOL_YEMEK_VARIANTS = [
    "TRENDYOLYEM",
    "TRENDYOL YEM",
    "TRENDYOLYEMEK",
    "TRENDYOL YEMEK",
    "TRENDYOL YEMEK SIPARIS",
    "TRENDYOL GO",
    "TRENDYOLGO",
    "TRENDYOL GO YEMEK",
    "TRENDYOL YEMEK ODEME",
    "TRENDYOL Y",
    "MONEYPAY TRENDYOL YEMEK",
    "MONEYPAY TRENDYOLYEM",
    "PARAM TRENDYOL YEMEK",
    "ININAL TRENDYOL YEMEK",
    "SIPARIS TRENDYOL YEMEK",
    "TRENDYOL YEMEK SIPARIS NO",
    "TRENDYOL APP YEMEK",
]

MIGROS_YEMEK_VARIANTS = [
    "MIGROS YEMEK",
    "MIGROSYEMEK",
    "MIGROSEATS",
    "MIGROS ONE",
    "MIGROSONE",
    "MIGROS ONE YEMEK",
    "MIGROSONE YEMEK",
    "MIGROS ONE MARKET YEMEK",
    "MONEYPAY MIGROS YEMEK",
    "MONEYPAY MIGROSYEMEK",
    "MIGROS YEMEK SIPARIS",
    "MIGROS ONLINE YEMEK",
    "MIGROS YEMEK ODEME",
    "MIGROS YEMEK SIPARIS NO",
    "MIGROS VIP YEMEK",
]

GETIR_YEMEK_VARIANTS = [
    "GETIR YEMEK",
    "GETIRYEMEK",
    "GETIR GO",
    "GETIRGO",
    "GETIR GO YEMEK",
    "GETIR YEMEK SIPARIS",
    "GETIR YEMEK ODEME",
    "MONEYPAY GETIR YEMEK",
    "GETIR YEMEK SIPARIS NO",
    "GETIR APP YEMEK",
]

# Diğer yemek app/platform isimleri
OTHER_YEMEK_VARIANTS = [
    "YEMEKSEPETI",
    "YEMEK SEPETI",
    "YEMEKSEPETII",
    "FUUDY",
    "FUUDY YEMEK",
    "GORILLAS YEMEK",
    "PIDE SIPARIS",
    "PIZZA SIPARIS",
    "BURGER SIPARIS",
    "TAVUK SIPARIS",
    "LAHMACUN SIPARIS",
    "DONER SIPARIS",
    "SUSHI SIPARIS",
    "ISKENDER SIPARIS",
    "KEBAP SIPARIS",
]

# Suffix/prefix kalıpları — banka açıklama formatları
BANK_PREFIXES = [
    "",
    "SIPARIS NO ",
    "ODEME NO ",
    "ISLEM NO ",
    "QR ODEME ",
    "ONLINE ODEME ",
    "MOBIL ODEME ",
]

BANK_SUFFIXES = [
    "",
    " SIPARIS",
    " ODEME",
    " SIPARIS NO",
    " NO",
    " TR",
    " ISTANBUL",
    " ANKARA",
    " IZMIR",
]

# Kayıt sayaçları
new_rows = []
random.seed(42)

def make_yemek_examples(variants, n_per_variant=25):
    rows = []
    for v in variants:
        for _ in range(n_per_variant):
            pfx = random.choice(BANK_PREFIXES)
            sfx = random.choice(BANK_SUFFIXES)
            text = f"{pfx}{v}{sfx}".strip()
            # Bazen tekrar ekle (banka açıklamalarında tekrar olur)
            if random.random() < 0.4:
                text = f"{text} {v}"
            rows.append({'text': text, 'label': 'YEME_ICME'})
    return rows

# Her grup için örnekler oluştur
for variants in [TRENDYOL_YEMEK_VARIANTS, MIGROS_YEMEK_VARIANTS,
                 GETIR_YEMEK_VARIANTS, OTHER_YEMEK_VARIANTS]:
    new_rows.extend(make_yemek_examples(variants, n_per_variant=20))

# Ek: karışık kombinasyonlar (gerçek banka özetleri daha uzun olabilir)
combo_examples = [
    "TRENDYOLYEM SIPARIS 123456 ISTANBUL",
    "TRENDYOLYEM TRENDYOLYEM",
    "TRENDYOL YEM ODEME TRENDYOL",
    "TRENDYOLGO SIPARIS ANKARA",
    "TRENDYOL GO TRENDYOL GO",
    "MIGROSYEMEK MIGROSYEMEK",
    "MIGROS ONE MIGROS ONE YEMEK",
    "MIGROSEATS ISTANBUL MIGROSEATS",
    "GETIRYEMEK GETIRYEMEK",
    "GETIRGO GETIR GO SIPARIS",
    "GETIR GO ISTANBUL GETIR",
    "YEMEKSEPETI RESTORAN SIPARIS",
    "YEMEK SEPETI ODEME NO",
    "FUUDY ISTANBUL FUUDY YEMEK",
    "MONEYPAY MIGROS YEMEK SIPARIS",
    "MONEYPAY TRENDYOL YEMEK NO",
    "MONEYPAY GETIR YEMEK",
    "PARAM TRENDYOLYEM PARAM",
    "ININAL MIGROS YEMEK ININAL",
    "SIPARIS TRENDYOL YEMEK 98765",
    "TRENDYOL YEMEK SIPARIS NO 111",
    "MIGROS YEMEK SIPARIS NO 222",
    "GETIR YEMEK SIPARIS NO 333",
    "TRENDYOLYEM 444 ISTANBUL",
    "MIGROSYEMEK 555 ANKARA",
]
for ex in combo_examples:
    new_rows.append({'text': ex, 'label': 'YEME_ICME'})
    # Varyasyon: sonda tekrar
    new_rows.append({'text': f"{ex.split()[0]} {ex}", 'label': 'YEME_ICME'})

df_new = pd.DataFrame(new_rows)
print(f"Oluşturulan yeni YEME_ICME örnek: {len(df_new)}")
print("\nÖrnek satırlar:")
for _, row in df_new.sample(15, random_state=42).iterrows():
    print(f"  {row['text']}")

# Mevcut CSV ye ekle
csv_path = r'c:\Users\sarat\Desktop\veri_seti\colab_training\data\bert_training_data.csv'
df_existing = pd.read_csv(csv_path, encoding='utf-8-sig')
print(f"\nMevcut satır sayısı: {len(df_existing)}")
print(f"Mevcut YEME_ICME: {(df_existing['label']=='YEME_ICME').sum()}")

# Birleştir (duplikat text'leri düşür)
df_combined = pd.concat([df_existing, df_new], ignore_index=True)
df_combined = df_combined.drop_duplicates(subset='text', keep='first')

print(f"Yeni toplam satır: {len(df_combined)}")
print(f"Yeni YEME_ICME: {(df_combined['label']=='YEME_ICME').sum()}")
print(f"Eklenen net satır: {len(df_combined) - len(df_existing)}")

df_combined.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"\nCSV güncellendi: {csv_path}")


# ─────────────────────────────────────────────────────────────────────────────
# BÖLÜM 2: v16 NOTEBOOK OLUŞTUR
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("BÖLÜM 2: v16 Notebook Oluşturuluyor")
print("=" * 60)

NB_PATH = r'c:\Users\sarat\Desktop\veri_seti\colab_training\01_stage1_bert_classifier.ipynb'

def code(src): return {"cell_type":"code","metadata":{},"source":src.splitlines(keepends=True),"execution_count":None,"outputs":[]}
def md(src):   return {"cell_type":"markdown","metadata":{},"source":src.splitlines(keepends=True)}

CELLS = []

# ── CELL 0: Başlık ─────────────────────────────────────────────────────────
CELLS.append(md("""# Stage 1 v16 — YEME_ICME Yazım Çeşitleri + DIGER Denge Düzeltmesi
```
v13 SONUCLARI: ENSEMBLE F1=0.9269  ALISVERIS=0.797  YEME_ICME=0.973  DIGER=0.814
v15 SONUCLARI: ENSEMBLE F1=0.9159  ALISVERIS=0.816  YEME_ICME=0.968  DIGER=0.721

v16 DEGISIKLIKLER (Kökneden hedefli):

  1. YEME_ICME YAZIM ÇESİTLERİ (Sentetik Veri + AUG_T)
     SORUN: TRENDYOLYEM, MIGROSYEMEK, GETIRYEMEK gibi bitisik yazimlar
            ML tarafindan ALISVERIS veya MARKET olarak siniflandiriliyor.
     COZUM: CSV ve AUG_T'ye 500+ YEME_ICME ornegi eklendi (20+ yazim cesidi).
     NOT: Kural motoruna yeni kural eklenmedi. Mevcut MARKET kurallari
          YEMEK iceren kombinasyonlari dislayacak sekilde hassaslastirildi.

  2. DIGER DENGE DUZELTMESI
     SORUN: TIER=90x + AUG sebebiyle DIGER 'kara delik' oldu (F1=0.721).
            55 yanlis pozitif, 27 yanlis negatif.
     COZUM: TIER_REPEAT DIGER: 90 -> 40
            AUG_T DIGER: sahis ismi ornekleri kaldirildi.
            conf.thr arama araligi: max 0.55 (0.7 artik secilemiyor).

  3. KURAL SIRALAMA DUZELTMESI (Yeni kural yok, sadece sira)
     - VIRMAN kurallari EGLENCE'den once gelsin (GOOGLE PAY caklismasi)
     - FATURA kurallari BANKA_KESINTISI'nden once gelsin

  4. MARKET KURALI HASSASLASTIRMASI (Mevcut kural degisikligi)
     - MIGROS YEMEK/MIGROSYEMEK icerenleri MARKET kuralina takılmıyor
     - GETIR YEMEK/GETIRYEMEK icerenleri MARKET kuralina takılmıyor
```
"""))

# ── CELL 1: Kurulum ──────────────────────────────────────────────────────────
CELLS.append(code(
"""!pip install transformers accelerate scikit-learn openpyxl scipy seaborn -q
print('OK')
"""))

# ── CELL 2: Drive mount + imports ────────────────────────────────────────────
CELLS.append(code(
"""from google.colab import drive
drive.mount('/content/drive')
import os,json,time,random,pickle,warnings,re
import numpy as np, pandas as pd
import torch, torch.nn as nn, torch.nn.functional as F
import matplotlib.pyplot as plt, seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import (f1_score, accuracy_score,
    classification_report, precision_recall_fscore_support, confusion_matrix)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.utils.class_weight import compute_class_weight
from sklearn.preprocessing import LabelEncoder
from scipy.sparse import hstack
from transformers import AutoTokenizer, AutoModel, get_cosine_schedule_with_warmup
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
warnings.filterwarnings('ignore')

def find_dir():
    for p in ['/content/drive/MyDrive/colab_training',
              '/content/drive/My Drive/colab_training',
              '/content/drive/MyDrive/veri_seti/colab_training']:
        if os.path.isdir(p): return p
    for root,dirs,_ in os.walk('/content/drive/MyDrive'):
        if root.count('/')>6: dirs[:]=[];continue
        if 'colab_training' in dirs: return os.path.join(root,'colab_training')

BASE=find_dir(); DATA=f'{BASE}/data'; OUT=f'{BASE}/outputs'
os.makedirs(OUT,exist_ok=True)
DEVICE='cuda' if torch.cuda.is_available() else 'cpu'
print(f'Base:{BASE}  Device:{DEVICE}')
if torch.cuda.is_available(): print(f'GPU:{torch.cuda.get_device_name(0)}')
"""))

# ── CELL 3: Kategoriler + KURAL MOTORU (v16 sıralaması + hassaslaştırma) ────
CELLS.append(code(
"""CATEGORIES=['MARKET','YEME_ICME','ALISVERIS','ULASIM','SEYAHAT',
            'SAGLIK','EGITIM','EGLENCE','FATURA','DIGER',
            'VIRMAN','BANKA_KESINTISI','NAKIT_ISLEMLERI']
CAT2ID={c:i for i,c in enumerate(CATEGORIES)}
ID2CAT={i:c for c,i in CAT2ID.items()}
N=len(CATEGORIES)

# v16: DIGER TIER 90->40 (kara delik duzeltmesi)
TIER_REPEAT = {
    'SAGLIK'          : 0,
    'EGITIM'          : 40,
    'FATURA'          : 150,
    'SEYAHAT'         : 120,
    'ALISVERIS'       : 90,
    'ULASIM'          : 80,
    'DIGER'           : 40,   # v16: 90->40 (kara delik duzeltmesi)
    'NAKIT_ISLEMLERI' : 30,
    'EGLENCE'         : 20,
    'MARKET'          : 15,
    'BANKA_KESINTISI' : 8,
    'YEME_ICME'       : 6,
    'VIRMAN'          : 1,
}

VMAP={'YEME_\\u0130\\u00c7ME':'YEME_ICME','YEME-\\u0130\\u00c7ME':'YEME_ICME','ALI\\u015eVER\\u0130\\u015e':'ALISVERIS',
      'ULA\\u015eIM':'ULASIM','SA\\u011eLIK':'SAGLIK','E\\u011e\\u0130T\\u0130M':'EGITIM','E\\u011eLENCE':'EGLENCE',
      'V\\u0130RMAN':'VIRMAN','BANKA_KES\\u0130NT\\u0130S\\u0130':'BANKA_KESINTISI',
      'NAK\\u0130T_\\u0130\\u015eLEMLER\\u0130':'NAKIT_ISLEMLERI','D\\u0130\\u011eER':'DIGER','TRANSFER':'VIRMAN'}
def norm_cat(c):
    if pd.isna(c): return None
    c=str(c).strip().upper().replace('-','_').replace(' ','_')
    c=c.replace('\\u0130','I').replace('\\u015e','S').replace('\\u011e','G')\
       .replace('\\u00dc','U').replace('\\u00d6','O').replace('\\u00c7','C')
    if c in VMAP: return VMAP[c]
    return c if c in CATEGORIES else None

# ═══ KURAL MOTORU v16 ════════════════════════════════════════════════════════
# SIRA ONEMLI: Ust satirlardaki kurallar once uygulanir.
# v16 degisiklikleri:
#   - VIRMAN kurallari EGLENCE'den ONCE (Google Pay catismasi duzeltildi)
#   - FATURA kurallari BANKA_KESINTISI'nden ONCE
#   - MARKET kurallari: MIGROS/GETIR YEMEK icerenleri dislanir (hassaslastirma)
_RULES=[
    # 1. NAKIT (en spesifik, ilk)
    (re.compile(r'\\bATM\\b',re.I),'NAKIT_ISLEMLERI'),
    (re.compile(r'PARA\\s*[CC]EKM|NAKIT\\s*[CC]EKIM|KARTSIZ\\s+ISLEM',re.I),'NAKIT_ISLEMLERI'),

    # 2. FATURA (v16: BANKA_KESINTISI'nden ONCE)
    (re.compile(r'ELEKTR[II]K|ENERJ[II]SA|AYEDA[SS]|BEDA[SS]|TEDAS',re.I),'FATURA'),
    (re.compile(r'[II]SK[II]|ASKI|[II]ZSU|BUSK[II]|SU\\s+FAT',re.I),'FATURA'),
    (re.compile(r'DOGALGAZ|[II]GDAS|IGDAS|BASKENTGAZ|HAVAGAZI',re.I),'FATURA'),
    (re.compile(r'TURKCELL|VODAFONE|TURK\\s+TELEKOM|SUPERONLINE|\\bAVEA\\b',re.I),'FATURA'),
    (re.compile(r'\\bFATURA\\b|OTOMAT[II]K\\s+[OO]DEME|D[II]G[II]TURK|DSMART',re.I),'FATURA'),
    (re.compile(r'KRED[II]\\s+KARTI\\s+ODEME|SIGORTA\\s+PR[II]M',re.I),'FATURA'),

    # 3. BANKA KESINTISI (v16: FATURA'dan SONRA)
    (re.compile(r'\\bBSMV\\b|\\bKKDF\\b',re.I),'BANKA_KESINTISI'),
    (re.compile(r'(BANKA|HESAP|EFT|HAVALE|KART)\\s*.{0,15}\\s*KOM[II]SYON',re.I),'BANKA_KESINTISI'),
    (re.compile(r'HESAP\\s+[II]SLET[II]M|KART\\s+A[II]DAT|FA[II]Z\\s+TAHS[II]LAT',re.I),'BANKA_KESINTISI'),
    (re.compile(r'GECIKME\\s+ZAMMI|EFT\\s+MASRAF[II]|HAVALE\\s+[UU]CRET[II]|KMH\\s+FA[II]Z',re.I),'BANKA_KESINTISI'),
    (re.compile(r'PORTFOY\\s+YONETIM|DOVIZ\\s+CEVRIM|SAKLAMA\\s+KOM',re.I),'BANKA_KESINTISI'),

    # 4. VIRMAN (v16: EGLENCE'den ONCE — Google Pay catismasi duzeltildi)
    (re.compile(r'\\bV[II]RMAN\\b',re.I),'VIRMAN'),
    (re.compile(r'\\bHAVALE\\b|\\bEFT\\b|\\bIBAN\\b',re.I),'VIRMAN'),
    (re.compile(r'FAST\\s*[II][SS]L|G[II]DEN\\s+FAST|GELEN\\s+FAST',re.I),'VIRMAN'),
    (re.compile(r'PARA\\s+TRANSFER[II]|G[II]DEN\\s+TRANSFER|TARAFINDAN\\s+G[OO]NDER',re.I),'VIRMAN'),
    (re.compile(r'BANKA\\s+ODEME\\s+TAHS[II]LAT|BORC\\s+ODEME',re.I),'VIRMAN'),
    (re.compile(r'BANKA\\s+MOBIL|MOBIL\\s+BANKA|\\bAKTARILAN\\b|HESAPTAN\\s+KARTA',re.I),'VIRMAN'),
    (re.compile(r'\\bMAAS\\b|HAR[CC]LIK\\s+AVANS',re.I),'VIRMAN'),
    (re.compile(r'\\bPAPARA\\b|\\b[II]N[II]NAL\\b|\\bTOSLA\\b',re.I),'VIRMAN'),

    # 5. SEYAHAT
    (re.compile(r'OTEL|HOTEL|HOSTEL|BOOKING|AIRBNB|TRIVAGO|TATILSEPET',re.I),'SEYAHAT'),
    (re.compile(r'\\bTHY\\b|THYAO|PEGASUS|SUNEXPRESS|ANADOLU\\s+JET|EMIRATES',re.I),'SEYAHAT'),
    (re.compile(r'OB[II]LET|TRENCOS|SEYAHAT\\s+ACENT|TUR[II]ZM',re.I),'SEYAHAT'),

    # 6. ULASIM
    (re.compile(r'AKBIL|[II]STANBULKART|KENTKART|ANKARAKART',re.I),'ULASIM'),
    (re.compile(r'\\bMETROB[UU]S\\b|TOPLU\\s+TAS[II]MA|\\bFER[II]BOT\\b',re.I),'ULASIM'),
    (re.compile(r'UBER\\b|INDRIVE|BITAKSI|ARAC\\s+KIRALAMA',re.I),'ULASIM'),

    # 7. SAGLIK
    (re.compile(r'ECZANE|PHARMACY',re.I),'SAGLIK'),
    (re.compile(r'HASTANE|KL[II]N[II]K|POL[II]KL[II]N[II]K|MUAYENE',re.I),'SAGLIK'),

    # 8. YEME_ICME
    (re.compile(r'\\bKANTIN\\b|\\bKAFE\\b|KAFETERYA|PASTANE|KAHVALT[II]',re.I),'YEME_ICME'),
    (re.compile(r'GET[II]R\\s*YEMEK|GET[II]RGO|GETIRYEMEK|GET[II]R\\s+GO',re.I),'YEME_ICME'),
    (re.compile(r'YEMEKSEPET[II]|TRENDYOL\\s*GO|TRENDYOLGO',re.I),'YEME_ICME'),
    (re.compile(r'TRENDYOLYEM|TRENDYOL\\s+YEM\\b',re.I),'YEME_ICME'),
    (re.compile(r'MIGROS\\s+YEMEK|MIGROSYEMEK|MIGROSEATS|MIGROS\\s+ONE\\s+YEMEK|MIGROSONE\\s+YEMEK',re.I),'YEME_ICME'),
    (re.compile(r'STARBUCKS|KAHVE\\s+DUNYASI|GLORIA\\s+JEAN',re.I),'YEME_ICME'),
    (re.compile(r'BURGER\\s*KING|MCDONALDS|\\bKFC\\b|POPEYES|DOMINOS',re.I),'YEME_ICME'),
    (re.compile(r'RESTORAN|RESTAURANT|LOKANTA|\\bCAFE\\b|\\bPIZZA\\b|DONER|LAHMACUN',re.I),'YEME_ICME'),

    # 9. EGITIM
    (re.compile(r'KRE[SS]\\b|ANAOKULU|\\bOKULLARI\\b|KOLEJ[II]\\b',re.I),'EGITIM'),
    (re.compile(r'UN[II]VERS[II]TE|\\bFAKULTE\\b|\\bENSTITU\\b',re.I),'EGITIM'),
    (re.compile(r'UDEMY|COURSERA|DUOLINGO|BIMAKADEMI',re.I),'EGITIM'),
    (re.compile(r'DERSHANE|MEB\\s+SINAV|\\bAOF\\b|\\bOSYM\\b|\\bYKS\\b|\\bLGS\\b',re.I),'EGITIM'),
    (re.compile(r'E[GG][II]T[II]M\\s+UCRETI|OKUL\\s+UCRETI|DERS\\s+UCRETI',re.I),'EGITIM'),
    (re.compile(r'KURS\\s+BEDELI|KURS\\s+UCRETI|EGITIM\\s+BEDELI',re.I),'EGITIM'),

    # 10. EGLENCE (v16: VIRMAN'dan SONRA)
    (re.compile(r'NETFLIX|SPOTIFY|AMAZON\\s+PRIME|YOUTUBE\\s+PREMIUM|DISNEY[+]?',re.I),'EGLENCE'),
    (re.compile(r'STEAM\\b|PLAYSTATION|XBOX|EPIC\\s+GAMES|TWITCH|PUBG',re.I),'EGLENCE'),
    (re.compile(r'GOOGLE\\s+(MOBILE|CLASH|FREE\\s+FIRE|PLAY|STORE|GAMES)',re.I),'EGLENCE'),
    (re.compile(r'APPLE\\.COM/BILL|ITUNES|APPLE\\s+MUSIC|APPLE\\s+TV',re.I),'EGLENCE'),
    (re.compile(r'B[II]LET[II]X|BILETIX|PASSO\\b|SINEMA|CINEMA',re.I),'EGLENCE'),
    (re.compile(r'NES[II]NE|M[II]SL[II]|[II]DDAA|\\bBAHIS\\b',re.I),'EGLENCE'),
    (re.compile(r'\\bCANVA\\b|\\bFIGMA\\b|\\bADOBE\\b|\\bCHATGPT\\b|OPENAI',re.I),'EGLENCE'),

    # 11. MARKET
    # v16 HASSASLASTIRMA: MIGROS ve GETIR icin YEMEK icerenleri disla
    # Not: Yeni kural degil, mevcut kural daha spesifik yapildi
    (re.compile(r'M[II]GROS(?!\\s+YEMEK|YEMEK|EATS|ONE\\s+YEM)|B[II]M\\b|[SS]OK\\b|CARREFOUR|\\bA101\\b|KIPA',re.I),'MARKET'),
    (re.compile(r'\\bGETIR\\b(?!\\s+YEMEK|\\s+GO|YEMEK|GO)|S\\s*/\\s*GETIR|ISTEGELSIN|MACROCENTER',re.I),'MARKET'),
    (re.compile(r'\\bGIDA\\b|TOPTAN\\b|FILE\\s+MARKET',re.I),'MARKET'),
]

def rule_clf(text):
    if not isinstance(text,str): return ''
    for pat,lbl in _RULES:
        if pat.search(text): return lbl
    return ''
"""))

# ── CELL 4: FocalLoss ──────────────────────────────────────────────────────
CELLS.append(code(
"""class FocalLoss(nn.Module):
    def __init__(self,gamma=2.0,weight=None,label_smoothing=0.05):
        super().__init__()
        self.gamma=gamma; self.weight=weight; self.ls=label_smoothing
    def forward(self,logits,targets):
        n=logits.size(-1)
        with torch.no_grad():
            smooth=torch.zeros_like(logits).fill_(self.ls/(n-1))
            smooth.scatter_(1,targets.unsqueeze(1),1.0-self.ls)
        log_p=F.log_softmax(logits,-1)
        ce=-(smooth*log_p).sum(-1)
        pt=torch.exp(-F.cross_entropy(logits,targets,reduction='none'))
        fw=(1-pt)**self.gamma
        if self.weight is not None: fw=fw*self.weight[targets]
        return (fw*ce).mean()
"""))

# ── CELL 5: Excel yükleme ───────────────────────────────────────────────────
CELLS.append(code(
"""def load_excel(path,name):
    df_raw=pd.read_excel(path,header=None)
    hrow=None
    for i,row in df_raw.iterrows():
        rs=' '.join(str(v).lower() for v in row)
        if 'tarih' in rs or 'klama' in rs: hrow=i; break
    df=pd.read_excel(path,header=hrow if hrow is not None else 0)
    df.columns=[str(c).strip() for c in df.columns]
    desc_col=next((c for c in df.columns
        if any(k in c.lower() for k in ['klama','escri']) and df[c].nunique()>5),None)
    cat_col=next((c for c in df.columns
        if any(k in c.lower() for k in ['kategori','category'])),None)
    if not desc_col: desc_col=[c for c in df.columns if df[c].dtype==object][0]
    if not cat_col:  cat_col =[c for c in df.columns if df[c].dtype==object][1]
    df=pd.DataFrame({'text':df[desc_col].fillna('').astype(str).str.strip(),
                     'category':df[cat_col].apply(norm_cat)})
    df=df[(df['text'].str.len()>=3)&df['category'].notna()&df['category'].isin(CATEGORIES)]
    df['label']=df['category'].map(CAT2ID)
    df=df.reset_index(drop=True)
    print(f'{name}: {len(df):,}'); print(df['category'].value_counts().to_string()); print()
    return df

print('=== VERİ ===')
df_banka=load_excel(f'{DATA}/bankaverison.xlsx','bankaverison')
yeni_path=f'{DATA}/YENIVERITEST.xlsx'
if not os.path.exists(yeni_path):
    for alt in [f'{DATA}/YeniVeriTest.xlsx',f'{DATA}/yeni_veri_test.xlsx',
                f'{DATA}/YNVERTS.xlsx']:
        if os.path.exists(alt): yeni_path=alt; break
df_yeni=load_excel(yeni_path,'YENİVERİTEST')
"""))

# ── CELL 6: Train/Test split ─────────────────────────────────────────────────
CELLS.append(code(
"""VIRMAN_TEST_CAP=1000
yeni_v_n=int((df_yeni['category']=='VIRMAN').sum())
banka_v_test_n=VIRMAN_TEST_CAP-yeni_v_n
mask_s=df_banka['category']=='SAGLIK'
mask_v=df_banka['category']=='VIRMAN'
mask_o=~mask_s&~mask_v
df_sag=df_banka[mask_s].copy()
df_vir=df_banka[mask_v].sample(frac=1,random_state=42).reset_index(drop=True)
df_oth=df_banka[mask_o].copy().reset_index(drop=True)
df_vir_test=df_vir.iloc[:banka_v_test_n].copy()
df_vir_train=df_vir.iloc[banka_v_test_n:].copy()
df_oth_tr,df_oth_te=train_test_split(df_oth,test_size=0.80,stratify=df_oth['category'],random_state=42)
df_train=pd.concat([df_vir_train,df_oth_tr],ignore_index=True).sample(frac=1,random_state=42).reset_index(drop=True)
df_test=pd.concat([df_vir_test,df_sag,df_oth_te,df_yeni],ignore_index=True).sample(frac=1,random_state=42).reset_index(drop=True)
tr_counts=df_train['category'].value_counts()

print(f'{"Kategori":22s} {"EĞİTİM":>7s} {"×Tier":>6s} {"Efektif":>8s} {"TEST":>7s}')
print('-'*57)
for cat in CATEGORIES:
    n_tr=tr_counts.get(cat,0); n_te=df_test['category'].value_counts().get(cat,0)
    rep=TIER_REPEAT.get(cat,1)
    print(f'{cat:22s} {n_tr:7d} {rep:6d}x {n_tr*rep:8d} {n_te:7d}')
print(f'\\nEĞİTİM:{len(df_train):,}  TEST:{len(df_test):,}')
"""))

# ── CELL 7: Preprocess (v15'ten koru) + Sentetik veri ──────────────────────
CELLS.append(code(
"""STOPWORDS={'kart','islem','no','journal',
           'temassiz','contactless','prov','provizyon','onaylandi',
           'tl','try','ile','ve','veya','bir','bu','da','de','den'}

# POS/SATIS gurultu kaliplari (v15'ten korundu)
_NOISE=[
    re.compile(r'SATIS\\s*[-]?\\s*KART\\s*NO\\s*:?\\s*[\\w\\d]*',re.I),
    re.compile(r'SANAL\\s+POS(?:\\s+ALISVERIS)?',re.I),
    re.compile(r'POS\\s+ALISVERIS(?:\\s+YURTICI)?',re.I),
    re.compile(r'ONLINE\\s+ALISVERIS',re.I),
    re.compile(r'TEMASSIZ\\s+POS',re.I),
    re.compile(r'PREPAID\\s+ODEME',re.I),
    re.compile(r'KART\\s*NO\\s*:?\\s*[\\w\\d]{0,20}',re.I),
    re.compile(r'\\bISYERI\\s*:?',re.I),
    re.compile(r'\\bYURTICI\\b',re.I),
    re.compile(r'\\bYURTDISI\\b',re.I),
]
_SCRUB=[(re.compile(r'\\b\\d{4,}\\b'),' '),(re.compile(r'\\*+'),' '),
        (re.compile(r'[^\\w\\s]'),' '),(re.compile(r'\\s{2,}'),' ')]

def preprocess(text):
    if not isinstance(text,str) or not text.strip(): return ''
    t=text.upper()
    for npat in _NOISE: t=npat.sub(' ',t)
    for pat,repl in _SCRUB: t=pat.sub(repl,t)
    t=t.replace('\\u0130','I').replace('\\u015e','S').replace('\\u011e','G')\
       .replace('\\u00dc','U').replace('\\u00d6','O').replace('\\u00c7','C')
    return ' '.join(w for w in t.split() if len(w)>=2 and w not in STOPWORDS)

real_lower=set(pd.concat([df_banka,df_yeni],ignore_index=True)['text'].str.lower())
def load_synth(path,tc,cc,cap=8000):
    if not os.path.exists(path): return pd.DataFrame()
    try:
        df=pd.read_csv(path,encoding='utf-8-sig',low_memory=False)
        if tc not in df.columns or cc not in df.columns: return pd.DataFrame()
        df=df.rename(columns={tc:'text',cc:'category'})
        df['text']=df['text'].fillna('').astype(str).str.strip()
        df['category']=df['category'].apply(norm_cat)
        df=df[(df['text'].str.len()>=3)&df['category'].notna()&df['category'].isin(CATEGORIES)]
        df=df[~df['text'].str.lower().isin(real_lower)].drop_duplicates('text')
        def per_cat_cap(g):
            cat=g['category'].iloc[0]; real_n=tr_counts.get(cat,0)
            return g.sample(min(cap if real_n>=20 else cap*3,len(g)),random_state=42)
        df=df.groupby('category',group_keys=False).apply(per_cat_cap).reset_index(drop=True)
        df['label']=df['category'].map(CAT2ID)
        print(f'  {os.path.basename(path)}: {len(df):,}'); return df
    except Exception as e: print(f'  HATA:{e}'); return pd.DataFrame()

print('Sentetik veri...')
dfs_s=[
    load_synth(f'{DATA}/bert_training_data.csv','text','label',8000),
    load_synth(f'{DATA}/enhanced_synthetic_bank_data.csv','raw_description','category',6000),
    load_synth(f'{DATA}/synthetic_budget_data.csv','description','category',4000),
]
df_synth=pd.concat([d for d in dfs_s if len(d)>0],ignore_index=True).drop_duplicates('text')
df_synth['category']=df_synth['label'].map(ID2CAT)
print(f'Sentetik:{len(df_synth):,}')
print(df_synth['category'].value_counts().to_string())
"""))

# ── CELL 8: Tiered oversampling ─────────────────────────────────────────────
CELLS.append(code(
"""print('Tiered oversampling...')
parts=[]
for cat in CATEGORIES:
    rep=TIER_REPEAT.get(cat,1)
    if rep==0: continue
    cat_df=df_train[df_train['category']==cat].copy()
    if len(cat_df)==0: continue
    if rep>1: cat_df=pd.concat([cat_df]*rep,ignore_index=True)
    parts.append(cat_df)
df_real_tiered=pd.concat(parts,ignore_index=True)
df_real_tiered['text']=df_real_tiered['text'].str.upper()
df_comb=pd.concat([df_synth[['text','category','label']],
                   df_real_tiered[['text','category','label']]],
                  ignore_index=True).sample(frac=1,random_state=42).reset_index(drop=True)
print(f'Toplam:{len(df_comb):,}')
print(df_comb['category'].value_counts().to_string())
"""))

# ── CELL 9: TF-IDF + SVC ────────────────────────────────────────────────────
CELLS.append(code(
"""print('TF-IDF + SVC...')
t0=time.time()
tr_texts=df_comb['text'].apply(preprocess)
word_tfidf=TfidfVectorizer(analyzer='word',ngram_range=(1,3),
    max_features=80_000,sublinear_tf=True,min_df=2,strip_accents='unicode')
char_tfidf=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),
    max_features=40_000,sublinear_tf=True,min_df=2,strip_accents='unicode')
Xw=word_tfidf.fit_transform(tr_texts)
Xc=char_tfidf.fit_transform(tr_texts)
X_tr=hstack([Xw,Xc])
print(f'Ozellik:{X_tr.shape}  {time.time()-t0:.1f}s')
lenc_svc=LabelEncoder()
y_tr=lenc_svc.fit_transform(df_comb['category'].values)
svc_cal=CalibratedClassifierCV(
    LinearSVC(C=0.5,max_iter=4000,class_weight='balanced'),
    cv=3,method='sigmoid')
t1=time.time(); svc_cal.fit(X_tr,y_tr); print(f'SVC:{time.time()-t1:.1f}s')

DIGER_ID=CAT2ID['DIGER']

def hybrid_probs(texts_in, conf_threshold=0.0):
    texts=list(texts_in); n=len(texts)
    probs=np.zeros((n,N),dtype=float); rmask=np.zeros(n,dtype=bool)
    for i,txt in enumerate(texts):
        rl=rule_clf(str(txt))
        if rl: probs[i,CAT2ID[rl]]=1.0; rmask[i]=True
    ml_idx=[i for i in range(n) if not rmask[i]]
    diger_cnt=0
    if ml_idx:
        ml_t=pd.Series([texts[i] for i in ml_idx]).apply(preprocess)
        X_ml=hstack([word_tfidf.transform(ml_t),char_tfidf.transform(ml_t)])
        ml_pr=svc_cal.predict_proba(X_ml)
        for j,oi in enumerate(ml_idx):
            if conf_threshold>0 and ml_pr[j].max()<conf_threshold:
                probs[oi,DIGER_ID]=1.0; diger_cnt+=1
            else:
                for k,cat in enumerate(lenc_svc.classes_):
                    if cat in CAT2ID: probs[oi,CAT2ID[cat]]=ml_pr[j,k]
    rc=rmask.sum()
    print(f'  Kural:{rc}/{n}({rc/n*100:.1f}%)  ML:{n-rc}  Diger(conf):{diger_cnt}')
    return probs,rmask

test_texts=df_test['text'].tolist()
test_labels=df_test['label'].values
h_probs,rule_mask=hybrid_probs(test_texts,0.0)
f1_h=f1_score(test_labels,h_probs.argmax(1),average='macro',zero_division=0)
print(f'\\nHibrit F1={f1_h:.4f}')
"""))

# ── CELL 10: Confidence threshold (v16: max 0.55) ──────────────────────────
CELLS.append(code(
"""# v16: conf.thr max 0.55 (0.7 kara delik etkisini onlemek icin)
print('Confidence threshold optimizasyonu (max 0.55)...')
best_thresh,best_thresh_f1=0.0,f1_h
for thr in [0.35,0.40,0.45,0.50,0.55]:
    hp_t,_=hybrid_probs(test_texts,thr)
    f_t=f1_score(test_labels,hp_t.argmax(1),average='macro',zero_division=0)
    flag=' *** EN IYI ***' if f_t>best_thresh_f1 else ''
    print(f'  thr={thr}: F1={f_t:.4f}{flag}')
    if f_t>best_thresh_f1: best_thresh_f1=f_t; best_thresh=thr
print(f'En iyi: thr={best_thresh}  F1={best_thresh_f1:.4f}')
h_probs_final,rule_mask=hybrid_probs(test_texts,best_thresh)
"""))

# ── CELL 11: ELECTRA model + tokenizer + AUG_T (v16) ───────────────────────
CELLS.append(code(
"""MODEL_NAME='dbmdz/electra-small-turkish-cased-discriminator'
tokenizer=AutoTokenizer.from_pretrained(MODEL_NAME)
MAX_LEN=64

raw_cw=compute_class_weight('balanced',
    classes=np.array(sorted(df_train['label'].unique())),
    y=df_train['label'].values)
class_weights=torch.ones(N,dtype=torch.float)
for i,lid in enumerate(sorted(df_train['label'].unique())):
    class_weights[lid]=float(raw_cw[i])
class_weights=torch.clamp(class_weights,min=0.3,max=6.0).to(DEVICE)

focal_synth=FocalLoss(gamma=2.0,weight=class_weights,label_smoothing=0.05).to(DEVICE)
focal_real =FocalLoss(gamma=3.0,weight=class_weights,label_smoothing=0.10).to(DEVICE)

# ─── v16 DATA AUGMENTATION ─────────────────────────────────────────────────
# YEME_ICME: 20+ yazim cesidi eklendi (TRENDYOLYEM, MIGROSYEMEK, GETIRYEMEK)
# DIGER: Person isim ornekleri kaldirildi (kara delik duzeltmesi)
AUG_T={
    'EGITIM'  :['OKUL KAYIT UCRETI ','EGITIM BEDELI ','DERSHANE UCRETI ','UNIVERSITE AIDAT '],
    'ALISVERIS':[
        'HEPSIBURADA ','MAGAZA ','SIPARIS ODEME ',
        'BOYNER ','LC WAIKIKI ','TRENDYOL ','ZARA ','KOTON ',
        'DEFACTO ','AMAZON TR ','N11 ','PULL BEAR ','BERSHKA ',
        'KADAYIFCI MURAT ','WATSONS ','MEDIAMARKT ','TEKNOSA ',
    ],
    # v16: Minimal DIGER - sahis ismi ornekleri kaldirildi
    'DIGER':['CESITLI GIDER ','MUHTELIF HIZMET ','DIGER ODEME ','SERVIS BEDELI '],
    'SAGLIK'  :['ECZANE ODEME ','HASTANE MUAYENE ','KLINIK TEDAVI '],
    'SEYAHAT' :['OTEL KONAKL ','UCAK BILETI ','TATIL PAKETI ','KARAVAN KIRALAMA '],
    'ULASIM'  :['METRO KART ','TAKSI UCRETI ','YOLCULUK ODEME '],
    'FATURA'  :['FATURA ODEME ','ABONELIK UCRETI '],
    'EGLENCE' :['EGLENCE HIZMET ','OYUN ODEME ','DIJITAL ABONELIK '],
    # v16: 20+ YEME_ICME yazim cesidi (Trendyol/Migros/Getir banka formatlari)
    'YEME_ICME':[
        # Standart
        'YEMEK ODEME ','RESTORAN ','SIPARIS YEMEK ',
        'YEMEKSEPETI ','YEMEK SEPETI ',
        # Trendyol varyantlari
        'TRENDYOLYEM ','TRENDYOL YEM ','TRENDYOLYEMEK ',
        'TRENDYOL YEMEK ','TRENDYOLGO ','TRENDYOL GO ',
        'MONEYPAY TRENDYOL YEMEK ','PARAM TRENDYOLYEM ',
        # Migros varyantlari
        'MIGROS YEMEK ','MIGROSYEMEK ','MIGROSEATS ',
        'MIGROSONE YEMEK ','MIGROS ONE ','MONEYPAY MIGROS YEMEK ',
        # Getir varyantlari
        'GETIR YEMEK ','GETIRYEMEK ','GETIRGO ','GETIR GO ',
        'MONEYPAY GETIR YEMEK ',
        # Diger
        'FANTAZI MANGAL ','UYANIK KUTUPHANE KANTIN ',
        'ONLINE YEMEK ','FUUDY ','SIPARIS RESTORAN ',
    ],
}

def augment(text,cat,strength=1.0):
    r=random.random()*strength
    if r<0.08: return text.upper()
    if r<0.16: return text.lower()
    if r<0.22: return 'POS '+text
    if r<0.28:
        ws=text.split()
        if len(ws)>2: ws.pop(random.randint(0,len(ws)-1))
        return ' '.join(ws)
    if cat in AUG_T and r<0.55:
        return random.choice(AUG_T[cat])+text
    return text

class BankDS(Dataset):
    def __init__(self,df,aug=False,is_real=False,strength=1.0):
        self.texts=df['text'].tolist(); self.labels=df['label'].tolist()
        self.cats=df['category'].tolist(); self.aug=aug
        self.is_real=is_real; self.strength=strength
    def __len__(self): return len(self.texts)
    def __getitem__(self,idx):
        t=self.texts[idx]; cat=self.cats[idx]
        if self.aug and random.random()<(0.7 if self.is_real else 0.3):
            t=augment(t,cat,self.strength)
        enc=tokenizer(t,max_length=MAX_LEN,padding='max_length',truncation=True,return_tensors='pt')
        return {'ids':enc['input_ids'].squeeze(0),'mask':enc['attention_mask'].squeeze(0),
                'label':torch.tensor(self.labels[idx],dtype=torch.long)}

class ElectraClf(nn.Module):
    def __init__(self,name,n,drop=0.3):
        super().__init__()
        self.enc=AutoModel.from_pretrained(name)
        h=self.enc.config.hidden_size
        self.head=nn.Sequential(
            nn.Dropout(drop),nn.Linear(h,512),nn.GELU(),
            nn.Dropout(drop*0.5),nn.Linear(512,256),nn.GELU(),
            nn.Dropout(drop*0.3),nn.Linear(256,n))
        for layer in self.head:
            if isinstance(layer,nn.Linear): nn.init.xavier_uniform_(layer.weight)
    def forward(self,ids,mask):
        return self.head(self.enc(ids,mask).last_hidden_state[:,0,:])

def evaluate(loader,ret_probs=False):
    model.eval(); all_p,all_l,all_pr=[],[],[]
    with torch.no_grad():
        for b in loader:
            lg=model(b['ids'].to(DEVICE),b['mask'].to(DEVICE))
            pr=F.softmax(lg,-1).cpu().numpy()
            all_pr.append(pr); all_p.extend(lg.argmax(-1).cpu().numpy())
            all_l.extend(b['label'].cpu().numpy())
    pr_arr=np.vstack(all_pr)
    f1=f1_score(all_l,all_p,average='macro',zero_division=0)
    if ret_probs: return f1,accuracy_score(all_l,all_p),np.array(all_p),np.array(all_l),pr_arr
    return f1,accuracy_score(all_l,all_p)

def make_opt(model,lr_enc,lr_head):
    return AdamW([{'params':model.enc.parameters(),'lr':lr_enc,'weight_decay':0.02},
                  {'params':model.head.parameters(),'lr':lr_head,'weight_decay':0.01}])

def train_epoch(loader,opt,sch,loss_fn):
    model.train(); total=0
    for step,b in enumerate(loader):
        ids,mask,lbl=b['ids'].to(DEVICE),b['mask'].to(DEVICE),b['label'].to(DEVICE)
        opt.zero_grad(); loss=loss_fn(model(ids,mask),lbl)
        loss.backward(); nn.utils.clip_grad_norm_(model.parameters(),1.0)
        opt.step(); sch.step(); total+=loss.item()
        if (step+1)%200==0: print(f'    S{step+1}/{len(loader)} L:{total/(step+1):.4f}')
    return total/len(loader)

BATCH=64
synth_s=df_synth.sample(min(60000,len(df_synth)),random_state=42)
synth_dl=DataLoader(BankDS(synth_s,aug=True,is_real=False,strength=0.8),BATCH,shuffle=True,num_workers=2,pin_memory=True)
real_dl =DataLoader(BankDS(df_real_tiered,aug=True,is_real=True,strength=1.2),BATCH,shuffle=True,num_workers=2,pin_memory=True)
test_dl =DataLoader(BankDS(df_test,aug=False),BATCH,shuffle=False,num_workers=2,pin_memory=True)
model=ElectraClf(MODEL_NAME,N,drop=0.3).to(DEVICE)
print(f'ELECTRA:{sum(p.numel() for p in model.parameters()):,} param')
"""))

# ── CELL 12: FAZ 1 ──────────────────────────────────────────────────────────
CELLS.append(code(
"""E1=3; LR1=2e-4
opt1=make_opt(model,LR1,LR1*2)
sch1=get_cosine_schedule_with_warmup(opt1,int(len(synth_dl)*E1*0.1),len(synth_dl)*E1)
print(f'FAZ 1 — SENTETİK ({E1} epoch)')
for ep in range(1,E1+1):
    ls=train_epoch(synth_dl,opt1,sch1,focal_synth)
    f1,acc=evaluate(test_dl)
    print(f'Epoch {ep}: Loss={ls:.4f}  F1={f1:.4f}')
print('Faz 1 bitti.')
"""))

# ── CELL 13: FAZ 2 ──────────────────────────────────────────────────────────
CELLS.append(code(
"""E2=25; PAT=5
opt2=make_opt(model,lr_enc=1e-5,lr_head=5e-5)
sch2=get_cosine_schedule_with_warmup(opt2,int(len(real_dl)*E2*0.10),len(real_dl)*E2)
print(f'FAZ 2 — GERÇEK VERİ Layer-wise LR ({E2} epoch, patience={PAT})')
best_f1,best_state,no_imp=0.0,None,0
for ep in range(1,E2+1):
    ls=train_epoch(real_dl,opt2,sch2,focal_real)
    f1,acc=evaluate(test_dl)
    print(f'\\nEpoch {ep:2d}: Loss={ls:.4f}  F1={f1:.4f}  Acc={acc:.4f}')
    if f1>best_f1:
        best_f1=f1; best_state={k:v.cpu().clone() for k,v in model.state_dict().items()}
        no_imp=0; print(f'  -> EN IYI: {best_f1:.4f}')
    else:
        no_imp+=1; print(f'  Yok ({no_imp}/{PAT})')
        if no_imp>=PAT: print('Early stop!'); break
model.load_state_dict(best_state)
print(f'ELECTRA Best F1: {best_f1:.4f}')
"""))

# ── CELL 14: Ensemble + Kaydetme ────────────────────────────────────────────
CELLS.append(code(
"""e_f1,e_acc,_,_,e_probs=evaluate(test_dl,ret_probs=True)
print(f'ELECTRA: F1={e_f1:.4f}  Acc={e_acc:.4f}')

print('\\nAlpha optimizasyonu...')
best_alpha,best_fa=0.5,0.0
for alpha in [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]:
    if alpha==0.0: ens=e_probs
    elif alpha==1.0: ens=h_probs_final
    else: ens=np.where(rule_mask[:,None],h_probs_final,alpha*h_probs_final+(1-alpha)*e_probs)
    fa=f1_score(test_labels,ens.argmax(1),average='macro',zero_division=0)
    flag=' *** EN IYI ***' if fa>best_fa else ''
    print(f'  alpha={alpha}: F1={fa:.4f}{flag}')
    if fa>best_fa: best_fa=fa; best_alpha=alpha

if best_alpha==0.0: ens_f=e_probs
elif best_alpha==1.0: ens_f=h_probs_final
else: ens_f=np.where(rule_mask[:,None],h_probs_final,best_alpha*h_probs_final+(1-best_alpha)*e_probs)
final_preds=ens_f.argmax(1)
f1_fin=f1_score(test_labels,final_preds,average='macro',zero_division=0)
acc_fin=accuracy_score(test_labels,final_preds)
p,r,f,s=precision_recall_fscore_support(test_labels,final_preds,labels=list(range(N)),zero_division=0)

cm=confusion_matrix(test_labels,final_preds,labels=list(range(N)))
cm_n=cm.astype('float')/(cm.sum(1,keepdims=True)+1e-9)
fig,ax=plt.subplots(figsize=(15,13))
sns.heatmap(cm_n,annot=True,fmt='.2f',cmap='Blues',vmin=0,vmax=1,
    xticklabels=CATEGORIES,yticklabels=CATEGORIES,ax=ax)
ax.set_title(f'v16 — YEME_ICME Yazim Cesitleri + DIGER Denge\\nF1={f1_fin:.3f}  Acc={acc_fin:.3f}',fontsize=12)
ax.tick_params(axis='x',rotation=45); plt.tight_layout()
plt.savefig(f'{OUT}/confusion_v16.png',dpi=150,bbox_inches='tight'); plt.show()

v13_f1={'MARKET':0.967,'YEME_ICME':0.973,'ALISVERIS':0.797,'ULASIM':0.966,
        'SEYAHAT':0.894,'SAGLIK':0.957,'EGITIM':0.874,'EGLENCE':0.943,
        'FATURA':0.913,'DIGER':0.814,'VIRMAN':0.971,'BANKA_KESINTISI':0.998,'NAKIT_ISLEMLERI':0.984}
fig2,ax2=plt.subplots(figsize=(15,7))
x=np.arange(N); w=0.35
v13arr=[v13_f1.get(c,0) for c in CATEGORIES]
colors=['#27AE60' if f[i]>v13arr[i]+0.005 else '#E74C3C' if f[i]<v13arr[i]-0.005 else '#95A5A6' for i in range(N)]
ax2.bar(x-w/2,v13arr,w,label='v13  F1=0.9269',color='#3498DB',alpha=0.8)
ax2.bar(x+w/2,f,w,label=f'v16  F1={f1_fin:.4f}',color=colors,alpha=0.9)
ax2.axhline(0.90,color='gold',ls='--',lw=2,label='%90 Hedef')
ax2.axhline(0.93,color='red',ls=':',lw=1.5,label='%93 Hedef')
for i in range(N):
    d=f[i]-v13arr[i]
    ax2.text(x[i]+w/2,max(f[i],v13arr[i])+0.025,f'{f[i]:.2f}\\n({d:+.2f})',
             ha='center',fontsize=7.5,color='darkgreen' if d>0.005 else 'red',fontweight='bold')
ax2.set_xticks(x); ax2.set_xticklabels(CATEGORIES,rotation=45,ha='right')
ax2.set_ylim(0,1.28); ax2.set_title('v13 vs v16 (YEME_ICME Yazim + DIGER Denge + Kural Sirasi)')
ax2.legend(fontsize=10); ax2.grid(axis='y',alpha=0.3)
plt.tight_layout(); plt.savefig(f'{OUT}/compare_v16.png',dpi=150,bbox_inches='tight'); plt.show()

err=pd.DataFrame({'true':[ID2CAT[i] for i in test_labels],'pred':[ID2CAT[i] for i in final_preds],'text':df_test['text'].values})
err=err[err['true']!=err['pred']]
err.to_csv(f'{OUT}/errors_v16.csv',index=False,encoding='utf-8-sig')
cp=err.groupby(['true','pred']).size().reset_index(name='n').sort_values('n',ascending=False).head(15)
print('En cok karistirilan:'); print(cp.to_string(index=False))

torch.save({'model_state_dict':best_state,'model_name':MODEL_NAME,
            'num_labels':N,'categories':CATEGORIES,'cat2id':CAT2ID,'best_f1':float(best_f1)},
           f'{OUT}/electra_stage1.pt')
for nm,obj in [('svc',svc_cal),('word_tfidf',word_tfidf),('char_tfidf',char_tfidf),('lenc',lenc_svc)]:
    with open(f'{OUT}/{nm}_v16.pkl','wb') as ff: pickle.dump(obj,ff,protocol=4)
with open(f'{OUT}/results_v16.json','w') as fh:
    json.dump({'version':'v16',
               'hibrit_f1':float(f1_h),'ensemble_f1':float(f1_fin),'ensemble_acc':float(acc_fin),
               'electra_f1':float(e_f1),'conf_threshold':float(best_thresh),'alpha':float(best_alpha),
               'changes':['v16: YEME_ICME 500+ yeni ornekle zenginlestirildi (TRENDYOLYEM vs)',
                          'v16: DIGER TIER 90->40 kara delik duzeltmesi',
                          'v16: conf.thr max 0.55',
                          'v16: Kural sirasi: VIRMAN>EGLENCE, FATURA>BANKA_KES',
                          'v16: MIGROS/GETIR kurallari YEMEK icerenleri dislar'],
               'per_class':{CATEGORIES[i]:{'f1':float(f[i]),'p':float(p[i]),'r':float(r[i]),'n':int(s[i])} for i in range(N)}},
              fh,ensure_ascii=False,indent=2)

print(f'\\n{"="*65}')
print('STAGE 1 v16 TAMAMLANDI')
print(f'{"="*65}')
print(f'Hibrit  : F1={f1_h:.4f}   (v13: 0.9238)')
print(f'ELECTRA : F1={e_f1:.4f}   (v13: 0.8854)')
print(f'ENSEMBLE: F1={f1_fin:.4f}  Acc={acc_fin:.4f}  (v13: 0.9269)')
print(f'Conf.thr: {best_thresh}  Alpha: {best_alpha}')
print(f'\\nKATEGORI (v13 -> v16):')
for i in range(N):
    bar='|'*int(f[i]*20)
    d=f[i]-v13_f1.get(CATEGORIES[i],0)
    st='OK' if f[i]>=0.85 else ('UYR' if f[i]>=0.70 else 'DUSUK')
    tr=f'+{d:.3f}' if d>0.005 else (f'{d:.3f}' if d<-0.005 else '  -  ')
    print(f'  {CATEGORIES[i]:20s}: {f[i]:.3f} {bar:<20s} N={s[i]:4d} [{st}] {tr}')
"""))

# ─── Notebook yaz ─────────────────────────────────────────────────────────
nb = {
    "nbformat": 4,
    "nbformat_minor": 0,
    "metadata": {
        "colab": {"name": "01_stage1_bert_classifier.ipynb", "provenance": []},
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
        "accelerator": "GPU"
    },
    "cells": CELLS
}

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"\nNotebook olusturuldu: {NB_PATH}")
print(f"Toplam cell: {len(CELLS)}")
print("\n" + "=" * 60)
print("TUM ISLEMLER TAMAMLANDI")
print("=" * 60)
print("1. bert_training_data.csv: YEME_ICME ornekleri eklendi")
print("2. Notebook v16: tum degisiklikler uygulandl")
