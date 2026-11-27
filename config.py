import os
from pathlib import Path
import secrets
import tempfile

# Don't edit this file. To override settings please use instance/production.py
# or environment variables.

BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = Path(os.environ.get('STORAGE_DIR', BASE_DIR / 'storage'))
DATA_DIR = Path(os.environ.get('DATA_DIR', STORAGE_DIR / 'data'))
MEDIA_FOLDER = Path(os.environ.get('MEDIA_FOLDER', STORAGE_DIR / 'media'))
TIB_DB_PATH = Path(
    os.environ.get('TIB_DB_PATH', DATA_DIR / 'tib_register.db'))

VERSION = '0.1.0'
LANGUAGES = {
    'de': 'Deutsch',
    'en': 'English'}
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1')

INSECURE_SECRET_PLACEHOLDERS = {
    'insecure-dev-key-change-in-production',
    'change-this-to-a-secure-random-secret-key-32-chars',
    'generate-a-long-random-string-here'}


def _load_or_create_secret_key(data_dir: Path) -> str:
    env_key = os.environ.get('SECRET_KEY', '').strip()
    if env_key and env_key not in INSECURE_SECRET_PLACEHOLDERS:
        return env_key

    key_file = data_dir / '.secret_key'
    tmp_path: Path | None = None
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        if key_file.exists():
            existing = key_file.read_text(encoding='utf-8').strip()
            if existing:
                return existing
        generated = secrets.token_hex(32)
        with tempfile.NamedTemporaryFile(
                mode='w',
                dir=data_dir,
                prefix='.secret_key.',
                delete=False,
                encoding='utf-8') as tmp_file:
            tmp_path = Path(tmp_file.name)
            os.chmod(tmp_path, 0o600)
            tmp_file.write(generated)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
        try:
            os.link(tmp_path, key_file)
            return generated
        except FileExistsError:
            existing = key_file.read_text(encoding='utf-8').strip()
            if existing:
                return existing
    except OSError:
        pass
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)
    return secrets.token_hex(32)


SECRET_KEY = _load_or_create_secret_key(DATA_DIR)

_RAW_TRUSTED = os.environ.get('TRUSTED_HOSTS', '')
TRUSTED_HOSTS: list[str] | None = (
    [h.strip() for h in _RAW_TRUSTED.split(',') if h.strip()] or None)
USE_PROXY_FIX = os.environ.get(
    'USE_PROXY_FIX', 'False').lower() in ('true', '1')
PUBLIC_BASE_URL = os.environ.get('PUBLIC_BASE_URL', '').strip().rstrip('/')
IIIF_ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get('IIIF_ALLOWED_HOSTS', '').split(',')
    if h.strip()]

# Security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = os.environ.get(
    'SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1')
REMEMBER_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'Lax'

MOP_API_PATH = os.environ.get('MOP_API_PATH', '')
ORTHO_API_PATH = os.environ.get(
    'ORTHO_API_PATH', 'https://openatlas.orthodoxes-europa.at/api/')
API_PROXY = os.environ.get('API_PROXY', '')

# Caching
CACHE_TYPE = os.environ.get('CACHE_TYPE', 'RedisCache')
CACHE_REDIS_URL = os.environ.get(
    'CACHE_REDIS_URL', 'redis://localhost:6379/0')
CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 604800))
