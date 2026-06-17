"""
라이선스 관리 모듈
- 무료: 설치일로부터 14일 체험
- 유료: 라이선스 키 입력 후 영구 사용
- 키 형식: BEEF-SEED-XXXX-XXXX
  SEED: 4자리 시드 (이메일/주문번호 앞부분)
  XXXX-XXXX: hmac(secret, SEED) 앞 8자리 → 오프라인 검증 가능
"""
import hashlib
import hmac as _hmac
import os
from datetime import date
from data.database import get_setting, save_setting

_SECRET = b"beeftracker2025_sehen_rgb"
FREE_TRIAL_DAYS = 14


def _today() -> str:
    return date.today().isoformat()


def get_install_date() -> str:
    d = get_setting("install_date", "")
    if not d:
        d = _today()
        save_setting("install_date", d)
    return d


def get_license_key() -> str:
    return get_setting("license_key", "")


def save_license_key(key: str):
    save_setting("license_key", key.strip().upper())


def _sign(seed: str) -> str:
    """seed(4자) → hmac 앞 8자리 대문자"""
    h = _hmac.new(_SECRET, seed.upper().encode(), hashlib.sha256).hexdigest().upper()
    return h[:8]


def validate_key(key: str) -> bool:
    """
    BEEF-SEED-XXXX-XXXX 검증
    XXXX-XXXX == hmac(secret, SEED)[:8]
    """
    key = key.strip().upper()
    parts = key.split("-")
    if len(parts) != 4 or parts[0] != "BEEF":
        return False
    seed = parts[1]
    expected = _sign(seed)
    actual = parts[2] + parts[3]
    return actual == expected


def generate_key_for_email(email: str) -> str:
    """
    판매자용: 이메일에서 4자리 시드 추출 → 키 생성
    같은 이메일 → 항상 같은 키
    """
    seed = _hmac.new(_SECRET, email.lower().encode(), hashlib.sha256).hexdigest().upper()[:4]
    sig = _sign(seed)
    return f"BEEF-{seed}-{sig[:4]}-{sig[4:]}"


def get_license_status() -> dict:
    """
    반환:
        plan: "free_trial" | "expired" | "premium"
        days_left: int (체험판 남은 일수, premium이면 -1)
        is_active: bool
    """
    key = get_license_key()
    if key and validate_key(key):
        return {"plan": "premium", "days_left": -1, "is_active": True}

    install = get_install_date()
    try:
        install_dt = date.fromisoformat(install)
    except ValueError:
        install_dt = date.today()
        save_setting("install_date", _today())

    elapsed = (date.today() - install_dt).days
    days_left = max(0, FREE_TRIAL_DAYS - elapsed)

    if days_left > 0:
        return {"plan": "free_trial", "days_left": days_left, "is_active": True}
    else:
        return {"plan": "expired", "days_left": 0, "is_active": False}


def is_premium() -> bool:
    return get_license_status()["plan"] == "premium"
