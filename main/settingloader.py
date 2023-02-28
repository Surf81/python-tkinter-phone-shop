import json
from main.dotdict import DotDict

CENTER = -1

class PhoneShopSettings(object):
    """Load app settings

    Args:
        settings_file: str
            path to .json file with app settings

    Returns:
        None: 
    """
    _defaultsettings = DotDict({
        "title": "Магазин 'Телефоны даром'",
        "screen": DotDict({
            "scale": DotDict({
                "width": 1200,
                "height": 800,
            }),
            "position": DotDict({
                "translate_x": CENTER,
                "translate_y": CENTER,
            })
        }),
    })

    def __init__(self, settings_file) -> None:
        self._current_settings = self._defaultsettings
        self.__settings_file = settings_file
        self.__load_settings()

    def __compare(self, default: DotDict, load: dict) -> DotDict:
        settings = DotDict()
        for cursor in default:
            if isinstance(default[cursor], DotDict):
                settings[cursor] = self.__compare(default[cursor], load.get(cursor, dict()))
            else:
                settings[cursor] = (prop if type(prop := load.get(cursor, None)) == type(default[cursor]) else None) or default[cursor]
        for cursor in load:
            if cursor not in settings:
                if isinstance(load[cursor], dict):
                    settings[cursor] = self.__compare(DotDict(), load[cursor])
                else:
                    settings[cursor] = load[cursor]
        return settings

    def __load_settings(self) -> None:
        try:
            with open(self.__settings_file, "rt", encoding="UTF-8") as settings_file:
                load_settings = json.load(settings_file)
        except (FileNotFoundError, UnicodeDecodeError, json.decoder.JSONDecodeError):
            load_settings = dict()

        self._current_settings = self.__compare(self._defaultsettings, load_settings)
        
    def __getattr__(self, name):
        return self._current_settings.get(name, None)
    
