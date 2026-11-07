import os
from pathlib import Path
import secrets

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
SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

# Security
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
