# -*- coding: utf-8 -*-
"""
Auth — JSON dosyasına kalıcı kullanıcı kaydı, UUID token
"""
import uuid, json, os, hashlib
from datetime import datetime
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# Kullanıcılar JSON dosyasında kalıcı saklanır
_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'users.json')

# Token → email (sadece bellekte, oturum bazlı)
_tokens: dict = {}


def _load_users() -> dict:
    if os.path.exists(_DB_PATH):
        try:
            with open(_DB_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_users(users: dict):
    with open(_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    kvkk: bool
    terms: bool


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    name: str
    email: str
    token: str


@router.post("/register", response_model=UserOut)
async def register(req: RegisterRequest):
    if not req.kvkk or not req.terms:
        raise HTTPException(400, "KVKK ve kullanım koşulları onaylanmalı")
    users = _load_users()
    if req.email in users:
        raise HTTPException(409, "Bu e-posta zaten kayıtlı")
    users[req.email] = {
        "name":       req.name,
        "email":      req.email,
        "password":   _hash(req.password),
        "created_at": datetime.now().isoformat(),
    }
    _save_users(users)
    token = str(uuid.uuid4())
    _tokens[token] = req.email
    return UserOut(name=req.name, email=req.email, token=token)


@router.post("/login", response_model=UserOut)
async def login(req: LoginRequest):
    users = _load_users()
    user = users.get(req.email)
    if not user:
        raise HTTPException(401, "E-posta veya şifre yanlış")
    # Hem hash'li hem düz şifre desteği (eski kayıtlarla uyumluluk)
    pw_ok = (user["password"] == _hash(req.password)) or (user["password"] == req.password)
    if not pw_ok:
        raise HTTPException(401, "E-posta veya şifre yanlış")
    token = str(uuid.uuid4())
    _tokens[token] = req.email
    return UserOut(name=user["name"], email=req.email, token=token)


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        _tokens.pop(token, None)
    return {"message": "Çıkış yapıldı"}


@router.get("/me")
async def me(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Token gerekli")
    token = authorization[7:]
    email = _tokens.get(token)
    if not email:
        raise HTTPException(401, "Geçersiz veya süresi dolmuş token")
    users = _load_users()
    user = users[email]
    return {"name": user["name"], "email": user["email"]}


# /reset-password endpoint'i kaldırıldı:
# E-posta doğrulaması (OTP/link) olmadan sadece e-posta bilerek
# herhangi bir hesabın şifresini değiştirmeye izin veriyordu.
# Şifre değiştirmek için giriş yapıp /change-password kullanılmalı.


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/change-password")
async def change_password(req: ChangePasswordRequest, authorization: Optional[str] = Header(None)):
    """Giriş yapmış kullanıcının şifresini değiştirir."""
    email = get_current_user(authorization)
    if len(req.new_password) < 6:
        raise HTTPException(400, "Yeni şifre en az 6 karakter olmalıdır.")
    users = _load_users()
    user = users.get(email)
    if not user:
        raise HTTPException(404, "Kullanıcı bulunamadı.")
    # Mevcut şifreyi doğrula
    pw_ok = (user["password"] == _hash(req.current_password)) or (user["password"] == req.current_password)
    if not pw_ok:
        raise HTTPException(401, "Mevcut şifre yanlış.")
    users[email]["password"] = _hash(req.new_password)
    _save_users(users)
    return {"message": "Şifreniz başarıyla güncellendi."}


def get_current_user(authorization: Optional[str] = Header(None)):
    """Dependency: mevcut kullanıcının email'ini döndürür."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Token gerekli")
    token = authorization[7:]
    email = _tokens.get(token)
    if not email:
        raise HTTPException(401, "Geçersiz token")
    return email
