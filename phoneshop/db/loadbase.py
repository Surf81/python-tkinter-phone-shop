import json
from core.settings import DATABASE
from phoneshop.db.db import DB


def load_phone_base():
    phone_shop_base = DB(DATABASE["SQLITE"])

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
                        phone_shop_base.add_phone(content)
                    elif key.strip().lower() == "characteristic":
                        phone_shop_base.add_characteristic(content)
    
    phone_shop_base.close()


