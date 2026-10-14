import os
from pathlib import Path

# Don't edit this file. To override settings please use instance/production.py

BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = Path(os.environ.get('STORAGE_DIR', BASE_DIR / 'storage'))
DATA_DIR = Path(os.environ.get('DATA_DIR', STORAGE_DIR / 'data'))
MEDIA_FOLDER = Path(os.environ.get('MEDIA_FOLDER', STORAGE_DIR / 'media'))
TIB_DB_PATH = Path(os.environ.get('TIB_DB_PATH', DATA_DIR / 'tib_register.db'))

VERSION = '0.1.0'
LANGUAGES = {
    'de': 'Deutsch',
    'en': 'English'}
DEBUG = False
SECRET_KEY = '1E600383250F0F63E9627E650B683DCE'

# Security
SESSION_COOKIE_SECURE = False
REMEMBER_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'Lax'

MOP_API_PATH = ''
ORTHO_API_PATH = 'https://openatlas.orthodoxes-europa.at/api/'
API_PROXY = ''

# Caching
CACHE_TYPE = 'RedisCache'
CACHE_REDIS_URL = 'redis://localhost:6379/0'
CACHE_DEFAULT_TIMEOUT = 604800  # 1 week
