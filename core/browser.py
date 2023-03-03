import tkinter as tk
from tkinter import ttk
from core.mainmenu import MainMenu
from core.router import PageRunner, Router

from core.settings import SETTINGS_FILE
from phoneshop.admin.admin import Admin
from phoneshop.auth.auth import Auth
from phoneshop.shop.shop import Shop

import json
from core.dotdict import DotDict

CENTER = -1


class Browser(object):
    def __init__(self, database, user, access, *args, **kwargs):
        self.db = database
        self.user = user
        self.access = access
        self.browser = tk.Tk()
        self.window = tk.Frame(self.browser, bd=6, relief=tk.GROOVE)
        self.settings = None
        self.router = None
        self.menu = None
        self.pages = dict()
        self.__init_pages()
        self.__base_init()
        self.__init()
        self.__create_pages()
        self.browser.mainloop()

    def __init_pages(self):
        for page in ("logon", "shop", "admin"):
            self.pages[page] = PageRunner()

    def __base_init(self):
        self.__load_settings()
        self.__create_router()
        self.__create_virtual_events()
        self.__create_environment()
        self.__create_mainwindow()

    def __init(self):
        self.__create_menu()

    refresh = __init

    def __create_pages(self):
        self.pages["logon"].set_page(Auth(self.window, self.user))
        self.pages["shop"].set_page(Shop(self.window, self.db, self.access, self.user))
        self.pages["admin"].set_page(Admin(self.window, self.db, self.access, self.user))

    def __create_mainwindow(self):
        self.window.grid(sticky="WENS")

        tk.Grid.columnconfigure(self.window, 0, weight=1)
        tk.Grid.rowconfigure(self.window, 0, weight=1)

    def __load_settings(self):
        if not self.settings:
            self.settings = BrowserSettings(SETTINGS_FILE)

    def __create_router(self):
        if not self.router:
            self.router = Router()
            self.router.register_rout("refresh", self.refresh)
            self.router.register_rout("shop", self.pages["shop"].run, history=True)
            self.router.register_rout("admin", self.pages["admin"].run, history=True)
            self.router.register_rout("logon", self.pages["logon"].run)
            self.router.register_rout("changeuser", self.pages["logon"].run)
            self.router.register_rout("quit", self.browser.destroy)

    def __create_menu(self):
        if not self.menu:
            self.menu = MainMenu(self.browser, self.router, self.access)
            # self.window.add_menu(self.menu.menu())
            self.browser.config(menu=self.menu.menu())
        else:
            self.menu.refresh()

    def __create_virtual_events(self):
        self.browser.event_add("<<UserChange>>", "None")
        self.browser.bind("<<UserChange>>", self.router.refresh_event, "%d")

    def __create_environment(self):
        self.browser.title(self.settings.title)
        self.browser.minsize(width=800, height=600)

        tk.Grid.columnconfigure(self.browser, 0, weight=1)
        tk.Grid.rowconfigure(self.browser, 0, weight=1)

        width = min(self.settings.screen.scale.width, self.browser.winfo_screenwidth())
        height = min(
            self.settings.screen.scale.height, self.browser.winfo_screenheight()
        )

        if (
            self.settings.screen.position.translate_x < 0
            or self.settings.screen.position.translate_x + width
            > self.browser.winfo_screenwidth()
        ):
            trans_x = (self.browser.winfo_screenwidth() - width) // 2
        else:
            trans_x = self.settings.screen.position.translate_x

        if (
            self.settings.screen.position.translate_y < 0
            or self.settings.screen.position.translate_y + height
            > self.browser.winfo_screenheight()
        ):
            trans_y = (self.browser.winfo_screenheight() - height) // 2
        else:
            trans_y = self.settings.screen.position.translate_y
        self.browser.geometry("{}x{}+{}+{}".format(width, height, trans_x, trans_y))
        # self.deiconify()


class BrowserSettings(object):
    """Load app settings

    Args:
        settings_file: str
            path to .json file with app settings

    Returns:
        None:
    """

    _defaultsettings = DotDict(
        {
            "title": "Магазин 'Телефоны даром'",
            "screen": DotDict(
                {
                    "scale": DotDict(
                        {
                            "width": 1200,
                            "height": 800,
                        }
                    ),
                    "position": DotDict(
                        {
                            "translate_x": CENTER,
                            "translate_y": CENTER,
                        }
                    ),
                }
            ),
        }
    )

    def __init__(self, settings_file) -> None:
        self._current_settings = self._defaultsettings
        self.__settings_file = settings_file
        self.__load_settings()

    def __compare(self, default: DotDict, load: dict) -> DotDict:
        settings = DotDict()
        for cursor in default:
            if isinstance(default[cursor], DotDict):
                settings[cursor] = self.__compare(
                    default[cursor], load.get(cursor, dict())
                )
            else:
                settings[cursor] = (
                    prop
                    if type(prop := load.get(cursor, None)) == type(default[cursor])
                    else None
                ) or default[cursor]
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
