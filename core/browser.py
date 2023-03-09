import tkinter as tk

from core.db.dbmanager import AuthDBManager, ShopDBManager
from core.dotdict import DotDict
from core.mainmenu import MainMenu
from core.router import PageRunner, Router
from core.settings import SETTINGS_FILE

from phoneshop.admin.adminform import AdminForm
from phoneshop.auth.accesscontroller import AccessController
from phoneshop.auth.authform import AuthForm
from phoneshop.auth.user import User
from phoneshop.shop.shopform import ShopForm

import json


class Browser(object):
    def __init__(self, database):
        self.db = database
        self.user = None
        self.access = None
        self.browser = self
        self.browser_tk = tk.Tk()
        self.window = tk.Frame(self.browser_tk, bd=6, relief=tk.GROOVE)
        self.settings = None
        self.router = None
        self.menu = None
        self.pages = dict()
        self.db_managers = dict()

    def run(self):
        self.__init_app()
        self.browser_tk.mainloop()

    def __init_app(self):
        self.__create_db_managers()
        self.__load_settings()
        self.__init_pages()
        self.__create_router()
        self.__create_virtual_events()
        self.__create_environment()
        self.__create_mainwindow()
        self.__init_user()
        self.__create_or_refresh_menu()
        self.__create_pages()

    def __create_db_managers(self):
        self.db_managers["auth"] = AuthDBManager(self.db)
        self.db_managers["shop"] = ShopDBManager(self.db)

    def __load_settings(self):
        if not self.settings:
            self.settings = BrowserSettings(SETTINGS_FILE)

    def __init_pages(self):
        for page in ("logon", "main-shop", "main-admin"):
            self.pages[page] = PageRunner()

    def __create_router(self):
        if not self.router:
            self.router = Router()
            self.router.register_rout("main-shop", self.pages["main-shop"].launch("run"), history=True)
            self.router.register_rout("main-admin", self.pages["main-admin"].launch("run"), history=True)
            self.router.register_rout("logon", self.pages["logon"].launch("run"))
            self.router.register_rout("changeuser", self.pages["logon"].launch("run"))
            self.router.register_rout("quit", self.browser_tk.destroy)

    def refresh(self, *args, **kwargs):
        self.__create_or_refresh_menu()
        self.router.call_history()

    def __create_virtual_events(self):
        self.browser_tk.event_add("<<UserChange>>", "None")
        self.browser_tk.bind("<<UserChange>>", self.refresh, "%d")

    def __create_environment(self):
        self.browser_tk.title(self.settings.title)
        self.browser_tk.minsize(width=800, height=600)

        tk.Grid.columnconfigure(self.browser_tk, 0, weight=1)
        tk.Grid.rowconfigure(self.browser_tk, 0, weight=1)

        width = min(self.settings.screen.scale.width, self.browser_tk.winfo_screenwidth())
        height = min(
            self.settings.screen.scale.height, self.browser_tk.winfo_screenheight()
        )

        if (
            self.settings.screen.position.translate_x < 0
            or self.settings.screen.position.translate_x + width
            > self.browser_tk.winfo_screenwidth()
        ):
            trans_x = (self.browser_tk.winfo_screenwidth() - width) // 2
        else:
            trans_x = self.settings.screen.position.translate_x

        if (
            self.settings.screen.position.translate_y < 0
            or self.settings.screen.position.translate_y + height
            > self.browser_tk.winfo_screenheight()
        ):
            trans_y = (self.browser_tk.winfo_screenheight() - height) // 2
        else:
            trans_y = self.settings.screen.position.translate_y
        self.browser_tk.geometry("{}x{}+{}+{}".format(width, height, trans_x, trans_y))

    def __create_mainwindow(self):
        self.window.grid(sticky="WENS")

        tk.Grid.columnconfigure(self.window, 0, weight=1)
        tk.Grid.rowconfigure(self.window, 0, weight=1)

    def __init_user(self):
        self.user = User(self.db_managers["auth"])
        self.access = AccessController(self.user)

    def __create_or_refresh_menu(self):
        if not self.menu:
            self.menu = MainMenu(self.browser_tk, self.browser)
            self.browser_tk.config(menu=self.menu.menu())
        else:
            self.menu.refresh()

    def __create_pages(self):
        self.pages["logon"].set_page(AuthForm(self.window, self.browser))
        self.pages["main-shop"].set_page(ShopForm(self.window, self.browser))
        self.pages["main-admin"].set_page(AdminForm(self.window, self.browser))



class BrowserSettings(object):
    """Load app settings

    Args:
        settings_file: str
            path to .json file with app settings

    Returns:
        None:
    """

    CENTER = -1
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
