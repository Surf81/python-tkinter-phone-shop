from pathlib import Path

APPNAME = "phoneshop"
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / APPNAME
SETTINGS_FILE = BASE_DIR / "settings.json"

DATABASE = {
    'SQLITE': BASE_DIR / 'db.sqlite3',
    'JSON': BASE_DIR / 'phone_base.json',
}


PASSWORD_LENGTH_MIN = 3
LOGIN_LENGTH_MIN = 3
PASSWORD_LENGTH_MAX = 16
LOGIN_LENGTH_MAX = 16