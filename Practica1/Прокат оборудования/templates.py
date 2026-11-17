INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts", "catalog", "rentals",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_USER_MODEL = "accounts.User"   # кастомный юзер с ролями
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "catalog"
LANGUAGE_CODE = "ru"
TIME_ZONE = "Asia/Novosibirsk"
USE_TZ = True
