import json
from core.settings import DATABASE


def load_phone_base(phone_db_manager):
    try:
        with open(DATABASE["JSON"], "rt", encoding="UTF-8") as json_file:
            load_info = json.load(json_file)
    except (FileNotFoundError, UnicodeDecodeError, json.decoder.JSONDecodeError) as e:
        print(e)

        load_info = list()

    if not isinstance(load_info, (list, tuple)):
        return

    for item in load_info:
        if isinstance(item, dict):
            for key, content in item.items():
                if isinstance(content, dict):
                    if key.strip().lower() == "phone":
                        phone_db_manager.add_or_update_phone(content)
                    elif key.strip().lower() == "characteristic":
                        phone_db_manager.add_characteristic(content)
