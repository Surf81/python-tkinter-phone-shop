import tkinter as tk
from tkinter import ttk

from core.router import PageRunner
from phoneshop.admin.useradmin import UserAdminPage
from phoneshop.admin.phoneadmin import PhoneAdminPage


class AdminForm(object):
    def __init__(self, master_window, browser):
        self.master = master_window
        self.browser = browser
        self.router = browser.router
        self.access = browser.access
        self.user = browser.user
        self.window = tk.Frame(self.master)
        self.pages = dict()
        self.frames = dict()
        self.__init()

    def __init(self) -> None:
        """Инициализация панели администратора"""
        self.__init_pages()
        self.__create_router()
        self.__create_form()
        self.__create_pages()

    def __init_pages(self) -> None:
        """Регистрация стартеров для будущих страниц"""
        for page in ("user-admin-app", "phone-admin-app"):
            self.pages[page] = PageRunner()

    def __create_router(self) -> None:
        """Регистрация в роутере команд запуска приложений"""
        self.router.register_rout(
            "user-admin-app", self.pages["user-admin-app"].launch("run")
        )
        self.router.register_rout(
            "phone-admin-app", self.pages["phone-admin-app"].launch("run")
        )

    def __create_form(self) -> None:
        """Формирование окна панели администратора"""
        win = self.window
        tk.Grid.columnconfigure(win, 0, weight=1, minsize=200)
        tk.Grid.columnconfigure(win, 1, weight=15)
        tk.Grid.rowconfigure(win, 1, weight=1)

        self.frames["topbar"] = TopBarFrame(win, self.browser)
        self.frames["topbar"].grid(row=0, column=0, columnspan=2, sticky="WE")
        self.frames["sidebar"] = SideBarFrame(win, self.browser)
        self.frames["sidebar"].grid(row=1, column=0, sticky="WENS")
        self.frames["mainframe"] = MainFrame(win, self.browser)
        self.frames["mainframe"].grid(row=1, column=1, sticky="WENS")

    def __create_pages(self) -> None:
        """Создание окон, отображаемых в панели администратора"""
        win = self.frames["mainframe"]
        self.pages["user-admin-app"].set_page(UserAdminPage(win, self.browser))
        self.pages["phone-admin-app"].set_page(PhoneAdminPage(win, self.browser))

    def __clear_browser(self) -> None:
        """Очистка окна-родителя в котором отображается панель администратора"""
        for item in self.master.grid_slaves():
            item.grid_forget()

    def run(self) -> None:
        """Запуск панели администратора"""
        self.__clear_browser()
        self.frames["topbar"].refresh()
        if self.access.is_allow("adminpage"):
            self.window.grid(sticky="WENS")


class TopBarFrame(tk.Frame):
    def __init__(self, master_window, browser, *args, **kwargs):
        super().__init__(master_window, *args, **kwargs)
        self.browser = browser
        self.master = master_window
        self.user = browser.user
        self.login_lbl = None
        self.role_lbl = None
        self.__create_form()

    def __create_form(self):
        tk.Grid.columnconfigure(self, 1, weight=1)

        ttk.Label(self, text="Текущий пользователь:").grid(
            row=0, column=0, pady=[10, 0], padx=[20, 5], sticky="w"
        )
        ttk.Label(self, text="Уровень доступа:").grid(
            row=1, column=0, padx=[20, 5], sticky="w"
        )
        self.login_lbl = tk.Label(self, text=self.user.user["login"], fg="red")
        self.login_lbl.grid(row=0, column=1, pady=[10, 0], sticky="w")
        self.role_lbl = tk.Label(self, text=self.user.user["role_descriptor"], fg="red")
        self.role_lbl.grid(row=1, column=1, sticky="w")
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(
            row=2, column=0, columnspan=2, pady=[10, 0], sticky="WE"
        )

    def refresh(self):
        self.login_lbl.config(text=self.user.user["login"])
        self.role_lbl.config(text=self.user.user["role_descriptor"])


class SideBarFrame(tk.Frame):
    def __init__(self, master_window, browser, *args, **kwargs):
        super().__init__(master_window, *args, **kwargs)
        self.browser = browser
        self.master = master_window
        self.router = browser.router
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

        ttk.Button(
            menuframe, text="Пользователи", command=self.router("user-admin-app")
        ).grid(row=2, column=0, sticky="WE")
        ttk.Button(
            menuframe, text="Телефоны", command=self.router("phone-admin-app")
        ).grid(row=6, column=0, sticky="WE")


class MainFrame(tk.Frame):
    def __init__(self, master_window, browser, *args, **kwargs):
        super().__init__(master_window, *args, **kwargs)
        self.browser = browser
        self.master = master_window
        self.__create_form()

    def __create_form(self):
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.rowconfigure(self, 0, weight=1)
