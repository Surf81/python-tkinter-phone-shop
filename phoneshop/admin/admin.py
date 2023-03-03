import tkinter as tk
from tkinter import ttk

from core.router import PageRunner, Router
from phoneshop.admin.useradmin import UserAdminFrame
from phoneshop.admin.phoneadmin import CharactAdminFrame, PhoneAdminFrame


class Admin(object):
    def __init__(self, browser, database, access, user):
        self.master = browser
        self.db = database
        self.access = access
        self.user = user
        self.window = tk.Frame(self.master)
        self.router = None
        self.pages = dict()
        self.widgets = dict()
        self.__init()

    def __init(self):
        self.__init_pages()
        self.__create_router()
        self.__create_form()
        self.__create_pages()

    def __create_form(self):
        win = self.window
        tk.Grid.columnconfigure(win, 0, weight=1, minsize=200)
        tk.Grid.columnconfigure(win, 1, weight=15)
        tk.Grid.rowconfigure(win, 1, weight=1)

        self.widgets["topbar"] = TopBar(win, self.user)
        self.widgets["topbar"].grid(row=0, column=0, columnspan=2, sticky="WE")
        self.widgets["sidebar"] = SideBar(win, self.router)
        self.widgets["sidebar"].grid(row=1, column=0, sticky="WENS")
        self.widgets["mainframe"] = MainFrame(win)
        self.widgets["mainframe"].grid(row=1, column=1, sticky="WENS")

    def __init_pages(self):
        for page in ("user", "characteristic", "phone"):
            self.pages[page] = PageRunner()

    def __create_router(self):
        self.router = Router()
        self.router.register_rout("user", self.pages["user"].run)
        self.router.register_rout("characteristic", self.pages["characteristic"].run)
        self.router.register_rout("phone", self.pages["phone"].run)

    def __create_pages(self):
        win = self.widgets["mainframe"]
        self.pages["user"].set_page(UserAdminFrame(win, self.db, self.user))
        self.pages["characteristic"].set_page(CharactAdminFrame(win, self.db))
        self.pages["phone"].set_page(PhoneAdminFrame(win, self.db))

    def __clear_browser(self):
        for item in self.master.grid_slaves():
            item.grid_forget()

    def run(self):
        self.__clear_browser()
        self.widgets["topbar"].refresh()
        if self.access.is_allow("adminpage"):
            self.window.grid(sticky="WENS")


class TopBar(tk.Frame):
    def __init__(self, browser, user, *args, **kwargs):
        super().__init__(browser, *args, **kwargs)
        self.user = user
        self.login_lbl = None
        self.role_lbl = None
        self.__create_form()

    def __create_form(self):
        tk.Grid.columnconfigure(self, 1, weight=1)

        ttk.Label(self, text="Текущий пользователь:").grid(
            row=0, column=0, pady=[10,0], padx=[20,5], sticky="w"
        )
        ttk.Label(self, text="Уровень доступа:").grid(
            row=1, column=0, padx=[20,5], sticky="w"
        )
        self.login_lbl = tk.Label(self, text=self.user.user["login"], fg="red")
        self.login_lbl.grid(
            row=0, column=1, pady=[10,0], sticky="w"
        )
        self.role_lbl = tk.Label(self, text=self.user.user["role_descriptor"], fg="red")
        self.role_lbl.grid(
            row=1, column=1, sticky="w"
        )
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(
            row=2, column=0, columnspan=2, pady=[10, 0], sticky="WE"
        )

    def refresh(self):
        self.login_lbl.config(text=self.user.user["login"])
        self.role_lbl.config(text=self.user.user["role_descriptor"])


class SideBar(tk.Frame):
    def __init__(self, browser, router, *args, **kwargs):
        super().__init__(browser, *args, **kwargs)
        self.master = browser
        self.router = router
        self.__create_form()

    def __create_form(self):
        win = self
        tk.Grid.columnconfigure(win, 0, weight=1)
        tk.Grid.rowconfigure(win, 0, weight=1)

        menuframe = tk.Frame(win)
        menuframe.grid(row=0, column=0, sticky="NS")
        borderframe = tk.Frame(win)
        borderframe.grid(row=0, column=1, sticky="NS")

        tk.Grid.columnconfigure(borderframe, 0, weight=1)
        tk.Grid.rowconfigure(borderframe, 0, weight=1)

        ttk.Separator(borderframe, orient=tk.VERTICAL).grid(
            row=0, column=1, sticky="NS", padx=[10, 0]
        )
        ttk.Label(menuframe, text="Меню администратора", font="Arial 12 bold").grid(
            row=0, column=0, padx=5, pady=[5, 30]
        )
        ttk.Label(menuframe, text="Пользователи", font="Arial 12 bold").grid(
            row=1, column=0, padx=5, pady=[5, 10]
        )
        ttk.Label(menuframe, text="Товары", font="Arial 12 bold").grid(
            row=4, column=0, padx=5, pady=[20, 10]
        )

        ttk.Button(menuframe, text="Пользователи", command=self.router("user")).grid(
            row=2, column=0, sticky="WE"
        )
        ttk.Button(
            menuframe, text="Характеристики", command=self.router("characteristic")
        ).grid(row=5, column=0, sticky="WE")
        ttk.Button(menuframe, text="Телефоны", command=self.router("phone")).grid(
            row=6, column=0, sticky="WE"
        )


class MainFrame(tk.Frame):
    def __init__(self, browser, *args, **kwargs):
        super().__init__(browser, *args, **kwargs)
        self.master = browser
        self.__create_form()

    def __create_form(self):
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.rowconfigure(self, 0, weight=1)
