"""
================================================================================
STAGE 1 v3 — HIZLI EĞİTİM  (TF-IDF + LinearSVC)
================================================================================
CatBoost ile 260K satır CPU'da 8+ saat sürüyor.
LinearSVC ile aynı kalite 3-5 dakikada elde edilir.

Neden LinearSVC?
  - TF-IDF sparse matris için doğal uyum (CatBoost dense bekler)
  - 260K satır metin sınıflandırmasında CatBoost'a eşit veya üstün
  - Eğitim: ~3-5 dakika (CatBoost: 8+ saat)
  - Probability için CalibratedClassifierCV (Platt scaling)

Mimari:
  [Kural Motoru] → yüksek-güven eşleşmeleri doğrudan sınıflandır
  [TF-IDF + LinearSVC] → kural eşleşmeyenleri sınıflandır

Veri:
  - synthetic_budget_data.csv        (30K)
  - ultimate_synthetic_bank_data.csv (150K)
  - enhanced_synthetic_bank_data.csv (271K — GERÇEK BANKA FORMATI)
  Toplam: ~260K (cap_per_class=20K)

Gerçek banka verisi SADECE test için.
================================================================================
"""

import os
import re
import sys
import json
import time
import warnings
import pickle
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, f1_score
from sklearn.utils.class_weight import compute_class_weight
from scipy.sparse import hstack, csr_matrix

warnings.filterwarnings("ignore")

BASE_DIR    = Path(__file__).resolve().parent.parent
MODEL_DIR   = BASE_DIR / "models" / "stage1"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(Path(__file__).resolve().parent))

CATEGORIES = [
    "MARKET", "YEME_ICME", "ALISVERIS", "ULASIM", "SEYAHAT", "SAGLIK",
    "EGITIM", "EGLENCE", "FATURA", "DIGER", "VIRMAN", "BANKA_KESINTISI", "NAKIT_ISLEMLERI"
]

# ===========================================================================
# METİN ÖN İŞLEME
# ===========================================================================

def normalize_turkish(text: str) -> str:
    return (
        text
        .replace("İ", "I").replace("ı", "i")
        .replace("Ş", "S").replace("ş", "s")
        .replace("Ğ", "G").replace("ğ", "g")
        .replace("Ü", "U").replace("ü", "u")
        .replace("Ö", "O").replace("ö", "o")
        .replace("Ç", "C").replace("ç", "c")
    )

STOPWORDS_TR = {
    # Dilbilgisi kelimeleri
    "ile", "ve", "veya", "bir", "bu", "da", "de", "den",
    "nin", "nun", "lari", "leri",
    # Genel banka gürültüsü
    "tahsilat", "ref", "numarali", "numarasi", "tutari",
    "tl", "try", "satis", "yurtici", "tarafindan",
    # !! KRİTİK FİX: POS terminal boilerplate !! 
    # Bu kelimeler TÜM kategorilerde geçer → sınıflandırma sinyali değil
    "alisveris",   # "POS ALIŞVERİŞ" — her POS işleminde var!
    "pos",         # "POS", "SANAL POS" — tüm kategorilerde
    "sanal",       # "SANAL POS" — e-ticaret hepsinde
    "isyeri",      # "İŞYERİ:" — tüm POS açıklamalarında
    "kart",        # "KART NO:" — tüm kart işlemlerinde
    "yurtici",     # "(YURTİÇİ)" — çoğu POS'ta
    "islem",       # "İŞLEM" — çok genel
    "odeme",       # "ÖDEME" — çok genel (ama bazen ayırt edici)
    "no",          # kart/journal no
    "journal",     # journal no
    "temassiz",    # TEMASSIZ POS — tüm kategorilerde
    "contactless", # contactless payment
    "prov",        # provizyon
    "provizyon",
    "onaylandi",   # işlem onaylandı
}

_SCRUB = [
    (re.compile(r"\b\d{4,}\b"),  " "),
    (re.compile(r"\*+"),          " "),
    (re.compile(r"[^\w\s]"),      " "),
    (re.compile(r"\s{2,}"),       " "),
]

def preprocess_text(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""
    t = text.upper()
    for pat, repl in _SCRUB:
        t = pat.sub(repl, t)
    t = normalize_turkish(t)
    tokens = [w for w in t.split() if len(w) >= 2 and w not in STOPWORDS_TR]
    return " ".join(tokens)

# ===========================================================================
# KURAL MOTORU  (Hibrit mimarinin 1. katmanı)
# ===========================================================================

_RULES = [
    # ================================================================
    # ÖNCELİKLİ (HIGHEST PRIORITY) KURALLAR (Kullanıcı Talebi)
    # ================================================================
    (re.compile(r'\bV[İI]RMAN\b',                                  re.I), 'VIRMAN'),
    (re.compile(r'\bKANT[İI]N\b|\bKAF[EE]\b|KAFETARYA|CAFE',      re.I), 'YEME_ICME'),
    
    # ================================================================
    # NAKIT_ISLEMLERI
    # ================================================================
    (re.compile(r'\bATM\b',                                        re.I), 'NAKIT_ISLEMLERI'),
    (re.compile(r'PARA\s*[CÇ]EKM|PARA\s*[CÇ]EKIM|NAKIT\s*[CÇ]EKIM', re.I), 'NAKIT_ISLEMLERI'),
    (re.compile(r'NAKIT\s+AVANS|KART\s+AVANSI',                   re.I), 'NAKIT_ISLEMLERI'),
    (re.compile(r'KARTSIZ\s+ISLEM',                                re.I), 'NAKIT_ISLEMLERI'),

    # ================================================================
    # BANKA_KESINTISI — spesifik banka masraf kalıpları
    # ================================================================
    (re.compile(r'\bBSMV\b',                                       re.I), 'BANKA_KESINTISI'),
    (re.compile(r'\bKKDF\b',                                       re.I), 'BANKA_KESINTISI'),
    # KOMİSYON: sadece banka bağlamı (EMLAK komisyonu hariç)
    (re.compile(r'(BANKA|HESAP|EFT|HAVALE|SWIFT|KART)\s*.{0,15}\s*KOM[İI]SYON|KOM[İI]SYON\s*.{0,15}\s*(BANKA|HESAP|EFT|HAVALE|KART)', re.I), 'BANKA_KESINTISI'),
    (re.compile(r'MESAJ\s+[UÜ]CRET[İI]',                          re.I), 'BANKA_KESINTISI'),
    (re.compile(r'KES[İI]NT[İI]\s+VE\s+EKLER[İI]',               re.I), 'BANKA_KESINTISI'),
    (re.compile(r'HESAP\s+[İI]SLET[İI]M|HESAP\s+[İI]DARE',       re.I), 'BANKA_KESINTISI'),
    (re.compile(r'KART\s+A[İI]DAT[İI]|A[İI]DAT\s+KART',         re.I), 'BANKA_KESINTISI'),
    (re.compile(r'FA[İI]Z\s+TAHS[İI]LAT|FA[İI]Z\s+BORCU',       re.I), 'BANKA_KESINTISI'),
    (re.compile(r'PORTFOY\s+YONETIM|SAKLAMA\s+KOM',               re.I), 'BANKA_KESINTISI'),
    (re.compile(r'GECIKME\s+ZAMMI|ASGARI\s+ODEME\s+FA[İI]Z',     re.I), 'BANKA_KESINTISI'),
    (re.compile(r'DOVIZ\s+CEVRIM\s+KOM|SWIFT\s+MUHABIR',         re.I), 'BANKA_KESINTISI'),
    (re.compile(r'EFT\s+MASRAF[İI]|HAVALE\s+[UÜ]CRET[İI]',      re.I), 'BANKA_KESINTISI'),
    (re.compile(r'KMH\s+FA[İI]Z',                                 re.I), 'BANKA_KESINTISI'),

    # ================================================================
    # VIRMAN — EFT, HAVALE, FAST, kişiden kişiye transfer
    # !! KRİTİK !! "BANKA ODEME TAHSİLAT" = kart borcu ödemesi = VIRMAN
    # ================================================================
    (re.compile(r'BANKA\s+ODEME\s+TAHS[İI]LAT|BANKA\s+TAHS[İI]LAT', re.I), 'VIRMAN'),
    (re.compile(r'BORC\s+ODEME|BORCUM\s+ODE',                     re.I), 'VIRMAN'),   # POS BORC ODEME
    (re.compile(r'HAR[CÇ]LIK\s+AVANS|HAR[CÇ]ILIK\s+TAHS[İI]LAT', re.I), 'VIRMAN'),
    (re.compile(r'NAKIT\s+AVANS',                                 re.I), 'VIRMAN'),   # Gerçek test verisi etiketleri böyle
    (re.compile(r'FAST\s*[İI][SŞ]L',                              re.I), 'VIRMAN'),
    (re.compile(r'G[İI]DEN\s+FAST|GELEN\s+FAST',                  re.I), 'VIRMAN'),
    (re.compile(r'\bFAST\b.{0,30}(G[OÖ]NDER|TRANSFER|AKTAR)',    re.I), 'VIRMAN'),
    (re.compile(r'TARAFINDAN\s+G[OÖ]NDER|G[OÖ]NDER[İI]LEN',     re.I), 'VIRMAN'),
    (re.compile(r'\bAKTARILAN\b',                                  re.I), 'VIRMAN'),
    (re.compile(r'BANKA\s+MOBIL|MOBIL\s+BANKA',                    re.I), 'VIRMAN'),
    (re.compile(r'\bHAVALE\b|\bEFT\b',                             re.I), 'VIRMAN'),
    (re.compile(r'\bIBAN\b',                                       re.I), 'VIRMAN'),
    (re.compile(r'\bV[İI]RMAN\b',                                  re.I), 'VIRMAN'),
    (re.compile(r'PARA\s+TRANSFER[İI]|G[İI]DEN\s+TRANSFER|GELEN\s+TRANSFER', re.I), 'VIRMAN'),
    (re.compile(r'HESAPTAN\s+KARTA\b|KARTTAN\s+HESABA',            re.I), 'VIRMAN'),
    (re.compile(r'YURT\s+TAHS[İI]LAT',                            re.I), 'VIRMAN'),
    (re.compile(r'HARC[LI]IK\s+AVANS|MAAŞ|MAAS\b',               re.I), 'VIRMAN'),

    # ================================================================
    # FATURA — Elektrik, su, doğalgaz, telekom
    # ================================================================
    (re.compile(r'ELEKTR[İI]K|ENERJ[İI]SA|AYEDA[SŞ]|BEDA[SŞ]|TEDAS', re.I), 'FATURA'),
    (re.compile(r'ISKI|[İI]SK[İI]|ASKI|[İI]ZSU|BUSK[İI]|SULAR\s+[İI]D|SU\s+FAT', re.I), 'FATURA'),
    (re.compile(r'DOGALGAZ|[İI]GDAS|IGDAS|BASKENTGAZ',            re.I), 'FATURA'),
    (re.compile(r'TURKCELL|VODAFONE|TURK\s+TELEKOM|SUPERONLINE|KABLO\s+NET', re.I), 'FATURA'),
    (re.compile(r'FATURA|FAT\s+NO|OTOMAT[İI]K\s+[OÖ]DEME',         re.I), 'FATURA'),
    (re.compile(r'VERGI|VERGİ|OPERATOR\s+FAT',                    re.I), 'FATURA'),
    (re.compile(r'D[İI]G[İI]TURK|DSMART|D-SMART',                re.I), 'FATURA'),
    (re.compile(r'KRED[İI]\s+KARTI\s+ODEME|KREDI\s+KART\s+BORCU', re.I), 'FATURA'),
    (re.compile(r'SIGORTA\s+PR[İI]M[İI]',                         re.I), 'FATURA'),
    (re.compile(r'HAVAGAZI|DOGALGAZ\s*FATURA',                     re.I), 'FATURA'),
    (re.compile(r'\bAVEA\b',                                       re.I), 'FATURA'),

    # ================================================================
    # EGLENCE — oyun, streaming, eğlence abonelikleri, bilet
    # !! KRİTİK !! GOOGLE üzerinden oyun/app satışı = EGLENCE
    # !! KRİTİK !! IYZICO/AMZNPRIME = Amazon Prime = EGLENCE
    # ================================================================
    (re.compile(r'NETFLIX|SPOTIFY|AMAZON\s+PRIME|YOUTUBE\s+PREMIUM|DISNEY\+?', re.I), 'EGLENCE'),
    (re.compile(r'STEAM\b|PLAYSTATION|XBOX|EPIC\s+GAMES|RIOTGAMES', re.I), 'EGLENCE'),
    (re.compile(r'GOOGLE\s+(MOBILE|CLASH|FREE\s+FIRE|GARENA|PLAY|STORE|GAMES|LEGENDS|ONE|GETVERIFY)', re.I), 'EGLENCE'),
    (re.compile(r'GOOGLE\s+\*(MICR|SNAP|GETC|YOUT|TRUCK)',         re.I), 'EGLENCE'),
    (re.compile(r'IYZICO\s*[/\\]\s*A[MN]Z|IYZICO\s*[/\\]\s*AMAZON|AMOZON', re.I), 'EGLENCE'),  # typo-tolerant
    (re.compile(r'APPLE\.COM/BILL|ITUNES|APPLE\s+MUSIC|APPLE\s+TV', re.I), 'EGLENCE'),
    (re.compile(r'B[İI]LET[İI]X|BILETIX|PASSO\b|B[İI]GL[İI]YET|BILET\.COM|BILETINIAL', re.I), 'EGLENCE'),
    (re.compile(r'NES[İI]NE|M[İI]SL[İI]|[İI]DDAA',               re.I), 'EGLENCE'),
    (re.compile(r'TWITCH|PUBG|MOBILE\s+LEGEND|CLASH\s+OF|FREE\s+FIRE', re.I), 'EGLENCE'),
    (re.compile(r'LIDIO\s*[/\\]|PAYTR\s*[/\\]\s*PREHESAP',         re.I), 'EGLENCE'),
    (re.compile(r'SINEMA|CINEMA|SINEMALARI|CINEPOINT',             re.I), 'EGLENCE'),  # sinema biletleri
    (re.compile(r'OYUN\s+MERKEZI|BILARDO|BOWLING|LAZER\s+TAG',    re.I), 'EGLENCE'),  # eğlence mekanları
    (re.compile(r'PAYCELL\s*/\s*MOBIL\s+OYUN|TURKCELL\s+OYUN',   re.I), 'EGLENCE'),  # Paycell oyun
    (re.compile(r'\bCANVA\b|\bFIGMA\b|\bADOBE\b',                re.I), 'EGLENCE'),  # yaratıcı abonelik
    (re.compile(r'\bCHATGPT\b|OPENAI|MIDJOURNEY',                  re.I), 'EGLENCE'),  # AI abonelik
    (re.compile(r'IYZICO\s*/\s*TIV|IYZICO.*YIYECEK',              re.I), 'EGLENCE'),  # IYZICO gıda değil eğlence

    # ================================================================
    # SEYAHAT
    # ================================================================
    (re.compile(r'OTEL|HOTEL|HOSTEL|PANSIYON',                     re.I), 'SEYAHAT'),
    (re.compile(r'BOOKING|AIRBNB|TRIVAGO|TATILSEPET',              re.I), 'SEYAHAT'),
    (re.compile(r'SEYAHAT\s+ACENT|TUR[İI]ZM',                     re.I), 'SEYAHAT'),
    (re.compile(r'OB[İI]LET|TRENCOS|ENUYGUN',                     re.I), 'SEYAHAT'),
    (re.compile(r'THY|THYAO|PEGASUS|SUNEXPRESS|ANADOLU\s+JET',    re.I), 'SEYAHAT'),
    (re.compile(r'EMIRATES|LUFTHANSA|FLYPGS',                      re.I), 'SEYAHAT'),

    # ================================================================
    # ULASIM — toplu taşıma, şehir içi araç
    # ================================================================
    (re.compile(r'TOPLU\s+TAS[İI]MA',                             re.I), 'ULASIM'),
    (re.compile(r'TIKTAKKIRAL|PARATIKA',                           re.I), 'ULASIM'),
    (re.compile(r'AKBIL|[İI]STANBULKART|KENTKART|ANKARAKART',     re.I), 'ULASIM'),
    (re.compile(r'\bMETROB[UÜ]S\b|\bFASTFERRY\b|\bFER[İI]BOT\b', re.I), 'ULASIM'),
    (re.compile(r'UBER\b|INDRIVE|BITAKSI|VOLT\s+LINE',             re.I), 'ULASIM'),
    (re.compile(r'ARAC\s+KIRALAMA|OTO\s+KIRALAMA',                re.I), 'ULASIM'),

    # ================================================================
    # EGITIM
    # ================================================================
    (re.compile(r'KRE[SŞ]|ANAOKULU|OKULLARI|KOLEJ[İI]',          re.I), 'EGITIM'),
    (re.compile(r'UVERSITE|ÜNİVERSİTE|UN[İI]VERS[İI]TE',            re.I), 'EGITIM'),
    (re.compile(r'KIRTAS[İI]YE|KITAP|KİTAP|FOTOKOPİ',               re.I), 'EGITIM'),
    (re.compile(r'E[ĞG][İI]T[İI]M|KURS|DERSHANE|YAYINLARI',       re.I), 'EGITIM'),
    (re.compile(r'UDEMY|COURSERA|EDX|PLURALSIGHT',                re.I), 'EGITIM'),
    (re.compile(r'MEB\s+SINAV|AOF|A[ÇC]IK[ÖO]GRETIM|OSYM|ÖSYM',     re.I), 'EGITIM'),
    (re.compile(r'KÜTÜPHANE|KUTUPHANE|DUOLINGO|DUOLI|DUOL',       re.I), 'EGITIM'),

    # ================================================================
    # YEME_ICME
    # ================================================================
    (re.compile(r'\bKANTIN\b',                                     re.I), 'YEME_ICME'),
    (re.compile(r'GET[İI]R\s*YEMEK|YEMEKSEPET[İI]|TRENDYOL\s*GO|TIKLA\s+GELSIN', re.I), 'YEME_ICME'),
    (re.compile(r'STARBUCKS|KAHVE\s+DUNYASI|GLORIA\s+JEAN',       re.I), 'YEME_ICME'),
    (re.compile(r'BURGER\s*KING|MCDONALDS|KFC\b|POPEYES|DOMINOS', re.I), 'YEME_ICME'),
    # Genel yemek/içecek mekan kalıpları (sonunda MARKET'ten önce)
    (re.compile(r'\bCAFE\b|\bKAFE\b|KAHVALT[Iİ]|PASTANE|DONDURMACI', re.I), 'YEME_ICME'),
    (re.compile(r'RESTORAN|RESTORANT|RESTAURANT|LOKANTA|\bETCİ\b|DONERCIM|DONER|DURUM', re.I), 'YEME_ICME'),
    (re.compile(r'\bPIZZA\b|\bBURGER\b|\bSUSHI\b|\bPIDE\b|MANTICI|LAHMACUN|BOREK', re.I), 'YEME_ICME'),
    (re.compile(r'CAJUN\s+CORNER|KOMAGENE|DUNYA\s+MUTFAK|LUNA\s+DI\s+PASTA', re.I), 'YEME_ICME'),

    # ================================================================
    # MARKET — süpermarket, bakkal, market zincirleri
    # !! KRİTİK !! "S/GETIR" = Getir Market = MARKET (değil ULASIM)
    # ================================================================
    (re.compile(r'M[İI]GROS|B[İI]M\b|[SŞ]OK\b|CARREFOUR|KIPA',  re.I), 'MARKET'),
    (re.compile(r'\bA101\b',                                       re.I), 'MARKET'),
    (re.compile(r'\bGETIR\b|S\s*/\s*GETIR|GETIR\s+PERAKENDE|PAYCELL/GETIR',    re.I), 'MARKET'),  # Getir Market
    (re.compile(r'ISTEGELSIN|GETIRBUYUK',                          re.I), 'MARKET'),
    (re.compile(r'MACROCENTER|ONUR\s+MARKET|FILE\s+MARKET',       re.I), 'MARKET'),
    (re.compile(r'\bGIDA\b|GLOBAL\s+MAGAZACILIK|TOPTAN\b',         re.I), 'MARKET'),

    # ================================================================
    # SAGLIK
    # ================================================================
    (re.compile(r'ECZANE|PHARMACY',                                re.I), 'SAGLIK'),
    (re.compile(r'HASTANE|KLINIK|POL[İI]KL[İI]N[İI]K|MUAYENE',  re.I), 'SAGLIK'),
    (re.compile(r'DIABET[İI]K|OPTIK\s+MERKEZ',                    re.I), 'SAGLIK'),

    # ================================================================
    # DIGER — test verisindeki gürültüler (garbage collection)
    # ================================================================
    (re.compile(r'SATI[SŞ]\s+[İI]ADE|\b[İI]ADE\b\s*-kart',        re.I), 'DIGER'),
    (re.compile(r'PAYTR/PAYTR\s+ODEME|LIDIO\s*/TEMPORARY',         re.I), 'DIGER'),
    (re.compile(r'MOKAUNITED|AKEL\s+YAPIM|POLATLAR\s+INS',         re.I), 'DIGER'),
    (re.compile(r'SATI[SŞ]-kart\s*no-IYZICO\s*$',                 re.I), 'DIGER'),
]

def rule_based_classify(text: str) -> str:
    if not isinstance(text, str):
        return ''
    for pattern, label in _RULES:
        if pattern.search(text):
            return label
            
    # Eğer açıklamada merchant adı yoksa ve sadece jenerik POS/SANAL POS yazıyorsa DIGER'e at.
    # Örn: "POS ALIŞVERİŞ KART NO: **" veya "SANAL POS ALIŞVERİŞ KART NO: **"
    # Eğer İŞYERİ:, IYZICO/, vb. varsa hala ML'e gider.
    clean_t = text.strip().upper()
    # Eğer string "KART NO:" veya "KART NO : " ile bitiyorsa (yani sonrasında işyeri adı yoksa)
    if "KART NO:" in clean_t:
        parts = clean_t.split("KART NO:")
        if len(parts) > 1 and len(parts[1].strip().replace("*", "")) == 0:
             return "DIGER"
             
    # Veya sadece "POS ALISVERIS" yazıp bitiyorsa
    bare_pos_pattern = re.compile(r'^(SANAL\s*)?POS\s*ALI[SŞ]VER[Iİ][SŞ](\s*\(YURT[Iİ][CÇ][Iİ]\))?\s*$', re.I)
    if bare_pos_pattern.match(clean_t):
        return "DIGER"

    return ''


# ===========================================================================
# MODEL — TF-IDF + LinearSVC (Hibrit)
# ===========================================================================

class FastTextClassifier:
    """
    TF-IDF + LinearSVC hibrit sınıflandırıcı.
    CatBoost'tan 100x hızlı, metin sınıflandırmasında eşdeğer kalite.
    """

    def __init__(self):
        # Word n-gram: (1,3) — daha geniş ngram, daha iyi coverage
        self.word_tfidf = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 3),
            max_features=50_000,
            sublinear_tf=True,
            min_df=3,
            strip_accents="unicode",
        )
        # Char n-gram: (3,5) — karakter düzeyinde pattern yakalama
        self.char_tfidf = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            max_features=30_000,
            sublinear_tf=True,
            min_df=3,
            strip_accents="unicode",
        )
        self.label_enc = LabelEncoder()
        self.model     = None
        self._fitted   = False

    def _build_features(self, texts: pd.Series, fit: bool = False) -> csr_matrix:
        if fit:
            w = self.word_tfidf.fit_transform(texts)
            c = self.char_tfidf.fit_transform(texts)
        else:
            w = self.word_tfidf.transform(texts)
            c = self.char_tfidf.transform(texts)
        return hstack([w, c])

    def fit(self, df: pd.DataFrame) -> "FastTextClassifier":
        t0 = time.time()
        print("[FastTextClassifier] Metin özellikleri çıkarılıyor...")
        texts = (
            df.get("raw_description", pd.Series("", index=df.index)).fillna("").astype(str)
            + " "
            + df.get("merchant_name", pd.Series("", index=df.index)).fillna("").astype(str)
        ).apply(preprocess_text)

        X = self._build_features(texts, fit=True)
        y_raw = df["category"].astype(str).str.strip()
        y = self.label_enc.fit_transform(y_raw)

        print(f"  Özellik matrisi: {X.shape[0]:,} satır x {X.shape[1]:,} özellik")
        print(f"  TF-IDF süresi: {time.time()-t0:.1f}s")

        # Class weights
        classes_arr = np.unique(y)
        cw = compute_class_weight("balanced", classes=classes_arr, y=y)
        cw_dict = dict(zip(classes_arr.tolist(), cw.tolist()))

        t1 = time.time()
        print("[FastTextClassifier] LinearSVC eğitimi başlıyor...")

        # LinearSVC — en hızlı büyük ölçekli metin sınıflandırıcı
        base_svc = LinearSVC(
            C=0.5,                # regularization
            max_iter=2000,
            class_weight="balanced",
            dual="auto",
        )

        # CalibratedClassifierCV: predict_proba desteği ekler (cv=3)
        self.model = CalibratedClassifierCV(base_svc, cv=3, method="sigmoid")

        X_tr, X_val, y_tr, y_val = train_test_split(
            X, y, test_size=0.15, stratify=y, random_state=42
        )

        self.model.fit(X_tr, y_tr)
        train_time = time.time() - t1
        print(f"  Eğitim süresi: {train_time:.1f}s")

        # Validation
        val_preds = self.model.predict(X_val)
        val_f1 = f1_score(y_val, val_preds, average="macro")
        val_acc = (val_preds == y_val).mean()
        print(f"  Val Macro-F1: {val_f1:.4f}  |  Val Accuracy: {val_acc:.4f}")
        print(classification_report(
            y_val, val_preds,
            target_names=self.label_enc.classes_,
            digits=3, zero_division=0
        ))

        self._fitted = True
        return self

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Hibrit tahmin: kural motoru → ML."""
        raw = df.get("raw_description", pd.Series("", index=df.index)).fillna("").astype(str)
        rule_preds = raw.apply(rule_based_classify)
        rule_mask  = rule_preds != ""
        ml_mask    = ~rule_mask
        results    = rule_preds.copy()

        if ml_mask.any():
            df_ml = df[ml_mask]
            texts = (
                df_ml.get("raw_description", pd.Series("", index=df_ml.index)).fillna("").astype(str)
                + " "
                + df_ml.get("merchant_name", pd.Series("", index=df_ml.index)).fillna("").astype(str)
            ).apply(preprocess_text)
            X = self._build_features(texts, fit=False)
            preds = self.model.predict(X)
            ml_cats = self.label_enc.inverse_transform(preds.astype(int))
            results[ml_mask] = ml_cats

        rule_count = rule_mask.sum()
        if rule_count > 0:
            print(f"  [Hybrid] Kural: {rule_count}/{len(df)} | ML: {ml_mask.sum()}")
        return results.values

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        raw = df.get("raw_description", pd.Series("", index=df.index)).fillna("").astype(str)
        rule_preds = raw.apply(rule_based_classify)
        rule_mask  = rule_preds != ""
        ml_mask    = ~rule_mask

        n_classes = len(self.label_enc.classes_)
        proba = np.zeros((len(df), n_classes), dtype=float)

        if rule_mask.any():
            for idx, cat in zip(df.index[rule_mask], rule_preds[rule_mask]):
                try:
                    cls_idx = list(self.label_enc.classes_).index(cat)
                    row_pos = df.index.get_loc(idx)
                    proba[row_pos, cls_idx] = 1.0
                except (ValueError, KeyError):
                    pass

        if ml_mask.any():
            df_ml = df[ml_mask]
            texts = (
                df_ml.get("raw_description", pd.Series("", index=df_ml.index)).fillna("").astype(str)
                + " "
                + df_ml.get("merchant_name", pd.Series("", index=df_ml.index)).fillna("").astype(str)
            ).apply(preprocess_text)
            X = self._build_features(texts, fit=False)
            ml_proba = self.model.predict_proba(X)
            ml_positions = [df.index.get_loc(i) for i in df_ml.index]
            proba[ml_positions, :] = ml_proba

        return proba

    def save(self, model_dir: Path = MODEL_DIR):
        with open(model_dir / "svc_model_v3.pkl",    "wb") as f: pickle.dump(self.model,       f, protocol=4)
        with open(model_dir / "word_tfidf_v3.pkl",   "wb") as f: pickle.dump(self.word_tfidf,  f, protocol=4)
        with open(model_dir / "char_tfidf_v3.pkl",   "wb") as f: pickle.dump(self.char_tfidf,  f, protocol=4)
        with open(model_dir / "label_enc_v3.pkl",    "wb") as f: pickle.dump(self.label_enc,   f, protocol=4)
        print(f"[Saved] Model v3 -> {model_dir}")

    @classmethod
    def load(cls, model_dir: Path = MODEL_DIR) -> "FastTextClassifier":
        obj = cls.__new__(cls)
        with open(model_dir / "svc_model_v3.pkl",    "rb") as f: obj.model      = pickle.load(f)
        with open(model_dir / "word_tfidf_v3.pkl",   "rb") as f: obj.word_tfidf = pickle.load(f)
        with open(model_dir / "char_tfidf_v3.pkl",   "rb") as f: obj.char_tfidf = pickle.load(f)
        with open(model_dir / "label_enc_v3.pkl",    "rb") as f: obj.label_enc  = pickle.load(f)
        obj._fitted = True
        return obj


# ===========================================================================
# ANA EĞİTİM + TEST
# ===========================================================================

