# Don't edit this file. To override settings please use instance/production.py

VERSION = '0.1.0'
LANGUAGES = {
    'de': 'Deutsch',
    'en': 'English',
    'sr': 'Српски',
    'el': 'Ελληνικά',
    'cnr': 'Crnogorski'}
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
