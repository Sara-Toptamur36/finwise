# -*- coding: utf-8 -*-
"""
Analiz endpoint'leri — CSV/Excel yukleme ve pipeline calistirma
"""
import io, json, os, uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Header
from typing import Optional
import pandas as pd

router = APIRouter()

# In-memory analiz sonuclari deposu: email -> result (en son sonuc)
_results: dict = {}

# Rapor gecmisi dosyasi
_REPORTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'reports_store.json')


def _load_reports() -> dict:
    try:
        with open(_REPORTS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_reports(data: dict):
    with open(_REPORTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _append_report(email: str, filename: str, result: dict):
    """Analiz sonucunu kalici depolara ekler."""
    all_reports = _load_reports()
    user_reports = all_reports.get(email, [])

    diagnosis = result.get('ai_coach', {}).get('label_display', '-')
    txn_count = result.get('summary', {}).get('txn_count', 0)

    entry = {
        'id': str(uuid.uuid4()),
        'created_at': datetime.now().isoformat(),
        'date': datetime.now().strftime('%d.%m.%Y'),
        'filename': filename,
        'mode': 'Kişisel',
        'txnCount': txn_count,
        'diagnosis': diagnosis,
        'result': result,
    }
    user_reports.append(entry)
    all_reports[email] = user_reports
    _save_reports(all_reports)


def _get_user(authorization: Optional[str] = Header(None)) -> str:
    from routers.auth import get_current_user
    return get_current_user(authorization)


def _norm(s: str) -> str:
    """Kolon adını normalize et: küçük harf, Türkçe→ASCII, boşluk→_, nokta kaldır."""
    s = str(s).lower().strip()
    for tr, en in [('ç','c'),('ş','s'),('ğ','g'),('ü','u'),('ö','o'),
                   ('ı','i'),('İ','i'),('Ç','c'),('Ş','s'),('Ğ','g'),('Ü','u'),('Ö','o')]:
        s = s.replace(tr, en)
    return s.replace(' ', '_').replace('-', '_').replace('.', '').replace('/', '_')


# Anahtar kelime listesi — normalize edilmiş sütun adında bu kelime GEÇİYORSA eşleşir
_KEYWORDS = {
    'tarih':     ['tarih', 'date', 'islem_tarih'],
    'aciklama':  ['aciklama', 'description', 'islem_aciklama', 'detay', 'islem_bilgi'],
    'tutar':     ['tutar', 'amount', 'miktar', 'islem_tutar'],
    'is_income': ['is_income', 'gelir_gider', 'tip', 'type', 'direction', 'borc_alacak'],
    'borc':      ['borc'],
    'alacak':    ['alacak'],
}


def _detect_header_row(raw_df: pd.DataFrame, max_scan: int = 20) -> int:
    """
    Excel'de gerçek başlık satırının indeksini bulur.
    İlk 20 satırı tarayarak en az 2 zorunlu kolona sahip satırı döndürür.
    Bulamazsa 0 döndürür.
    """
    # Zorunlu kolonlar için normalize edilmiş anahtar kelimeler (düz liste)
    must_have = ['tarih', 'date', 'aciklama', 'description', 'tutar', 'amount',
                 'miktar', 'islem', 'borc', 'alacak', 'bakiye']

    for i in range(min(max_scan, len(raw_df))):
        row_vals = [_norm(str(v)) for v in raw_df.iloc[i] if str(v) not in ('nan', 'None', '')]
        matches = sum(1 for v in row_vals if any(kw in v for kw in must_have))
        if matches >= 2:
            return i
    return 0


def _read_excel_smart(content: bytes) -> pd.DataFrame:
    """Excel dosyasını başlık satırını otomatik tespit ederek okur."""
    # Önce başlıksız oku
    raw = pd.read_excel(io.BytesIO(content), header=None)
    header_row = _detect_header_row(raw)
    if header_row == 0:
        # Zaten ilk satır başlık, normal oku
        return pd.read_excel(io.BytesIO(content))
    # Gerçek başlık satırından itibaren yeniden oku
    df = pd.read_excel(io.BytesIO(content), header=header_row)
    # Tamamen boş satırları temizle
    df = df.dropna(how='all').reset_index(drop=True)
    return df


def _find_col(df_columns: list, canonical: str):
    """Normalize edilmiş anahtar kelime eşleşmesiyle sütun bul."""
    norm_map = {_norm(c): c for c in df_columns}
    for kw in _KEYWORDS[canonical]:
        for norm_c, orig_c in norm_map.items():
            if kw in norm_c or norm_c == kw:
                return orig_c
    return None


def _normalize_df(df: pd.DataFrame) -> list:
    """DataFrame'i pipeline formatına dönüştürür — esnek kolon eşleme ile."""
    col_map = {}
    for canonical in ['tarih', 'aciklama', 'tutar', 'is_income']:
        found = _find_col(list(df.columns), canonical)
        if found:
            col_map[canonical] = found

    missing = [k for k in ['tarih', 'aciklama', 'tutar'] if k not in col_map]
    if missing:
        found_cols = list(df.columns)
        raise ValueError(
            f"Eksik kolonlar: {missing}. "
            f"Dosyadaki kolonlar: {found_cols}. "
            f"Beklenen: tarih/date, açıklama/description, tutar/amount"
        )

    # Borç/Alacak ayrı sütun kontrolü (bazı banka formatları)
    borc_col   = _find_col(list(df.columns), 'borc')   if 'borc'   not in col_map else None
    alacak_col = _find_col(list(df.columns), 'alacak') if 'alacak' not in col_map else None

    transactions = []
    for _, row in df.iterrows():
        tarih    = str(row[col_map['tarih']])
        aciklama = str(row[col_map['aciklama']])

        # Tutar: önce doğrudan sütun, sonra borç/alacak ayrımı
        try:
            raw_str = str(row[col_map['tutar']]).replace(',', '.').strip()
            raw_val = float(raw_str) if raw_str not in ('', 'nan', 'None', '-') else None
        except Exception:
            raw_val = None

        if raw_val is None:
            continue

        tutar     = abs(raw_val)
        is_income = raw_val > 0   # varsayılan: pozitif = gelir

        # is_income sütunu varsa onu kullan
        if 'is_income' in col_map:
            val = str(row[col_map['is_income']]).lower().strip()
            is_income = val in ('true', '1', 'gelir', 'income', 'alacak', 'giris', '+', 'a')

        transactions.append({
            'tarih':     tarih,
            'aciklama':  aciklama,
            'tutar':     tutar,
            'is_income': is_income,
        })
    return transactions


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    email: str = Depends(_get_user),
):
    """CSV veya Excel dosyasi yukle ve pipeline'i calistir."""
    content = await file.read()
    filename = file.filename or ""

    try:
        if filename.endswith('.csv') or file.content_type in ('text/csv', 'application/csv'):
            df = None
            for enc in ('utf-8', 'utf-8-sig', 'latin-1', 'cp1254'):
                try:
                    raw_csv = pd.read_csv(io.BytesIO(content), encoding=enc, header=None)
                    header_row = _detect_header_row(raw_csv)
                    df = pd.read_csv(io.BytesIO(content), encoding=enc, header=header_row)
                    df = df.dropna(how='all').reset_index(drop=True)
                    break
                except Exception:
                    continue
            if df is None:
                raise ValueError("CSV dosyasi okunamadi")
        elif filename.endswith(('.xlsx', '.xls')):
            df = _read_excel_smart(content)
        else:
            raise ValueError("Desteklenmeyen dosya formati. CSV veya Excel yukleyin.")
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(400, f"Dosya okunamadi: {e}")

    # Ham veri ozeti
    raw_summary = {
        "row_count":        len(df),
        "col_count":        len(df.columns),
        "null_rate":        round(df.isnull().mean().mean() * 100, 1),
        "masked_sensitive": 0,
        "valid_rate":       0.0,
    }

    try:
        transactions = _normalize_df(df)
    except ValueError as e:
        raise HTTPException(422, str(e))

    raw_summary["valid_rate"]   = round(len(transactions) / len(df) * 100, 1)

    # Pipeline'i calistir
    try:
        from services.pipeline_service import run_pipeline
        result = run_pipeline(transactions)
    except RuntimeError as e:
        raise HTTPException(503, f"Pipeline hatasi: {e}")
    except Exception as e:
        raise HTTPException(500, f"Analiz hatasi: {e}")

    result["raw_summary"] = raw_summary
    result["filename"]    = filename
    _results[email]       = result

    # Kalici depoya kaydet
    _append_report(email, filename, result)

    return result


@router.get("/result")
async def get_result(email: str = Depends(_get_user)):
    """Son analiz sonucunu dondurur."""
    result = _results.get(email)
    if not result:
        # Bellekte yoksa JSON'dan son sonucu yukle
        all_reports = _load_reports()
        user_reports = all_reports.get(email, [])
        if user_reports:
            result = user_reports[-1]['result']
            _results[email] = result
    if not result:
        raise HTTPException(404, "Analiz sonucu bulunamadi. Once dosya yukleyin.")
    return result


@router.get("/history")
async def get_history(email: str = Depends(_get_user)):
    """Kullanicinin tum analiz gecmisini dondurur (tam sonuc olmadan)."""
    all_reports = _load_reports()
    user_reports = all_reports.get(email, [])
    # Tam result'u donme, sadece metadata
    history = [
        {
            'id':        r['id'],
            'date':      r['date'],
            'filename':  r['filename'],
            'mode':      r['mode'],
            'txnCount':  r['txnCount'],
            'diagnosis': r['diagnosis'],
            'created_at': r['created_at'],
        }
        for r in reversed(user_reports)  # En yeniden eskiye
    ]
    return history


@router.get("/result/{report_id}")
async def get_result_by_id(report_id: str, email: str = Depends(_get_user)):
    """Belirli bir rapor ID'sine gore tam analiz sonucunu dondurur."""
    all_reports = _load_reports()
    user_reports = all_reports.get(email, [])
    for r in user_reports:
        if r['id'] == report_id:
            return r['result']
    raise HTTPException(404, "Rapor bulunamadi.")


@router.delete("/data")
async def delete_analysis_data(email: str = Depends(_get_user)):
    """Kullanicinin bellekteki analiz sonucunu siler."""
    _results.pop(email, None)
    return {"message": "Analiz verisi silindi."}


@router.delete("/reports")
async def delete_reports(email: str = Depends(_get_user)):
    """Kullanicinin tum rapor gecmisini siler."""
    _results.pop(email, None)
    all_reports = _load_reports()
    all_reports.pop(email, None)
    _save_reports(all_reports)
    return {"message": "Rapor gecmisi temizlendi."}
