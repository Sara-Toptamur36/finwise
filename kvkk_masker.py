"""
KVKK Anonimlestirilme Modulu
=============================
FIX 3: Hardcoded isim listesi kaldirildi.
Genel pattern tabanli Turkce isim tespiti yapiliyor.
"""
import re

# Sabit pattern'lar (bir kez derleniyor)
_IBAN_FULL    = re.compile(r'TR\s*\d{2}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{2}')
_IBAN_COMPACT = re.compile(r'TR\d{24}')
_LONG_NUMBER  = re.compile(r'\b\d{10,16}\b')

# Transfer prefix sonrasi isim: "Gonderici: AHMET YILMAZ"
# [A-Z] burada BUYUK HARF -- IGNORECASE YOK, banka isimleri title case oldugu icin gecmez
_TRANSFER_PREFIX = re.compile(
    r'(G[oO]nd(?:erici)?\s*:|Al[iI]c[iI]\s*:|GIDEN\s+FAST\s*-)\s*'
    r'([A-Z]{2,}(?:\s+[A-Z]{2,}){1,3})'
)

# Banka adi oncesi ad-soyad: "AHMET YILMAZ Ziraat Mobil Havale"
# Sadece TAM BUYUK HARF tokenlari eslestir, sonrasinda title-case banka adi gelir
_NAME_BEFORE_BANK = re.compile(
    r'^([A-Z]{2,}(?:\s+[A-Z]{2,}){1,3})\s+'
    r'(Ziraat|Garanti|Halk|Vakif|Akbank|YapiKredi|Ing|Deniz|QNB|Havale|EFT|FAST)\b'
)

# Bilinen magaza/islem kelimeleri -- bunlar isim DEGILDIR
_NON_NAME = frozenset([
    'MIGROS', 'BIMSA', 'GETIR', 'TRENDYOL', 'HEPSIBURADA', 'AMAZON',
    'NETFLIX', 'SPOTIFY', 'STARBUCKS', 'KFC', 'BURGER', 'MARKET',
    'ATM', 'EFT', 'HAVALE', 'FAST', 'POS', 'IBAN', 'TRY', 'TL',
    'MAAS', 'KIRA', 'FATURA', 'ODEME', 'VIRMAN', 'TAHSILAT',
    'BANKA', 'KREDI', 'KART', 'HESAP', 'TRANSFER',
    'ZIRAAT', 'GARANTI', 'AKBANK', 'ISBANK', 'HALKBANK', 'VAKIFBANK',
    'TURKCELL', 'VODAFONE', 'TURK', 'TELEKOM',
])


def _mask_word(w):
    """ilk 2 karakter gorunur, gerisi *"""
    return w[:2] + '*' * max(0, len(w) - 2)


def _mask_name(name_str):
    return ' '.join(_mask_word(w) for w in name_str.split())


def _is_name(tokens):
    """Token listesinin kisi ismi olup olmadigi heuristik kontrolu."""
    upper = [t.upper() for t in tokens]
    if any(t in _NON_NAME for t in upper):
        return False
    if any(len(t) < 2 for t in tokens):
        return False
    return True


def mask_kvkk(text):
    """
    Banka islem aciklamasindaki kisisel verileri maskeler.
    Maskelenen: IBAN, uzun sayilar (TCKN/tel/kart), transfer isimleri, banka-oncesi isimler.
    Hardcoded isim listesi KULLANILMAZ -- pattern ile tespit edilir.
    """
    if not isinstance(text, str):
        return text

    # 1. IBAN
    text = _IBAN_FULL.sub('TR**********************', text)
    text = _IBAN_COMPACT.sub('TR**********************', text)

    # 2. Uzun sayilar (TCKN, telefon, kart no)
    text = _LONG_NUMBER.sub(lambda m: '*' * len(m.group()), text)

    # 3. Transfer prefix sonrasi isim (Gonderici: AD SOYAD)
    def _transfer_sub(m):
        prefix = m.group(1)
        name   = m.group(2)
        tokens = name.split()
        if _is_name(tokens):
            return prefix + ' ' + _mask_name(name)
        return m.group(0)
    text = _TRANSFER_PREFIX.sub(_transfer_sub, text)

    # 4. Banka adi oncesindeki tam buyuk harf isim (AHMET YILMAZ Ziraat Mobil)
    def _bank_sub(m):
        name_p = m.group(1)
        bank_p = m.group(2)
        tokens = name_p.split()
        if _is_name(tokens):
            return _mask_name(name_p) + ' ' + bank_p
        return m.group(0)
    text = _NAME_BEFORE_BANK.sub(_bank_sub, text)

    return text
