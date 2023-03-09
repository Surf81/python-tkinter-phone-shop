from pathlib import Path


# Папка в которой находится запускаемый файл
BASE_DIR = Path(__file__).resolve().parent.parent


# Файл с настройками браузера
SETTINGS_FILE = BASE_DIR / "settings.json"


# Файл базы данных и файл демонстрационных данных
DATABASE = {
    "SQLITE": BASE_DIR / "db.sqlite3",
    "JSON": BASE_DIR / "phone_base.json",
}


# Папка со статическими файлами
STATIC_ROOT = BASE_DIR / "assets"


# Настройки логина и пароля. Не менять после создания базы данных
PASSWORD_LENGTH_MIN = 3
LOGIN_LENGTH_MIN = 3
PASSWORD_LENGTH_MAX = 16
LOGIN_LENGTH_MAX = 16