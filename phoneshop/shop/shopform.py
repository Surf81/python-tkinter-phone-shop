import tkinter as tk
from tkinter import ttk
from core.checkboxtreeview import MyCheckboxTreeview
from core.router import PageRunner


class ShopForm(object):
    """Панель магазина"""

    def __init__(self, master_window, browser):
        self.master = master_window
        self.browser = browser
        self.access = browser.access
        self.user = browser.user
        self.window = tk.Frame(self.master)
        self.frames = dict()
        self.router = browser.router
        self.pages = dict()
        self.__init()

    def __init(self) -> None:
        """Инициализация приложения"""
        self.__init_pages()
        self.__create_router()
        self.__create_form()
        self.__create_pages()

    def __init_pages(self) -> None:
        """Создание стартеров будущих прилождений"""
        for page in ("shop-app",):
            self.pages[page] = PageRunner()

    def __create_router(self) -> None:
        """Регистрация команд запуска приложений"""
        self.router.register_rout("shop-app", self.pages["shop-app"].launch("run"))
        self.router.register_rout(
            "shop-app-filter", self.pages["shop-app"].launch("setfilter")
        )

    def __create_pages(self) -> None:
        """Указание в стартере приложений"""
        win = self.frames["mainframe"]
        self.pages["shop-app"].set_page(ShopPageContent(win, self.browser))

    def __create_form(self) -> None:
        """Формирование окна магазина"""
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

    def __clear_browser(self) -> None:
        """Очистка окна-родителя"""
        for item in self.master.grid_slaves():
            item.grid_forget()

    def run(self) -> None:
        """Запуск приложения"""
        self.__clear_browser()
        self.frames["topbar"].refresh()
        self.frames["sidebar"].refresh()
        self.router("shop-app")()
        self.window.grid(sticky="WENS")


class TopBarFrame(tk.Frame):
    def __init__(self, master_window, browser, *args, **kwargs):
        super().__init__(master_window, *args, **kwargs)
        self.browser = browser
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
    """Боковая панель с фильтрами"""

    def __init__(self, master_window, browser, *args, **kwargs):
        super().__init__(master_window, *args, **kwargs)
        self.master = master_window
        self.browser = browser
        self.router = browser.router
        self.tree = None
        self.filteractive = None
        self.__create_form()

    def __make_filter(self) -> dict:
        """Создание информационного объекта фильтра"""
        shop_db_manager = self.browser.db_managers["shop"]
        components = dict()
        iid = 0
        for key, item in shop_db_manager.get_components().items():
            iid += 1
            group_iid = str(iid)
            component = components.setdefault(group_iid, dict())
            component["key"] = key
            component["description"] = item["description"]
            component["checked"] = True
            values = component.setdefault("values", dict())
            for v in item["values"]:
                iid += 1
                value = values.setdefault(group_iid + "-" + str(iid), dict())
                value["key"] = v
                value["description"] = v
                value["checked"] = True
        return components

    def __create_form(self) -> None:
        """Создание формы фильтра"""
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.rowconfigure(self, 0, weight=1)

        frame1 = tk.Frame(self)
        frame1.grid(row=0, column=0, sticky="NS")
        frame2 = tk.Frame(self)
        frame2.grid(row=0, column=1, sticky="NS")

        tk.Grid.columnconfigure(frame1, 0, weight=1)
        tk.Grid.rowconfigure(frame1, 2, weight=1)
        tk.Grid.columnconfigure(frame2, 0, weight=1)
        tk.Grid.rowconfigure(frame2, 0, weight=1)

        ttk.Label(
            frame1, text="Магазин\n'Телефоны даром'", font=("Arial", 12, "bold")
        ).grid(row=0, column=0, sticky="WE", pady=20)

        ttk.Label(frame1, text="Фильтр товаров", font=("Arial", 12, "bold")).grid(
            row=1, column=0, sticky="WE", pady=20
        )

        self.tree = MyCheckboxTreeview(frame1, self.__make_filter(), show="tree")
        self.tree.grid(row=2, column=0, sticky="WENS")

        self.tree.bind(
            "<Button-1>",
            lambda _: self.__set_filter() if self.filteractive.get() else None,
            True,
        )

        self.filteractive = tk.BooleanVar(frame1)
        tk.Checkbutton(
            frame1,
            text="Применить фильтр",
            variable=self.filteractive,
            command=self.__set_filter,
        ).grid(row=3, column=0, sticky="W", pady=[20, 20])
        ttk.Separator(frame2, orient=tk.VERTICAL).grid(
            row=1, column=1, sticky="NS", padx=0
        )

    def __set_filter(self) -> None:
        """Применение фильтра"""
        if self.filteractive.get():
            components = dict()
            for _, item in self.tree.get_content().items():
                if item["checked"]:
                    values = components.setdefault(item["key"], list())
                    for _, values_item in item["values"].items():
                        if values_item["checked"]:
                            values.append(values_item["key"])
            self.router("shop-app-filter")(components)
        else:
            self.router("shop-app-filter")(None)

    def refresh(self) -> None:
        """Обновление дерева фильтра"""
        self.tree.refresh(self.__make_filter())


class MainFrame(tk.Frame):
    def __init__(self, master_window, browser, *args, **kwargs):
        super().__init__(master_window, *args, **kwargs)
        self.browser = browser
        self.master = master_window
        self.__create_form()

    def __create_form(self):
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.rowconfigure(self, 0, weight=1)


class ShopPageContent(object):
    def __init__(self, master_window, browser):
        self.browser = browser
        self.master = master_window
        self.content = dict()
        self.filter = None
        self.window = tk.Frame(self.master)
        self.table = None
        self.__create_form()

    def __create_form(self):
        win = self.window
        tk.Grid.columnconfigure(win, 0, weight=1)
        tk.Grid.rowconfigure(win, 0, weight=1)
        self.__create_table()

    def __refresh_table(self) -> None:
        """Обновление табличной части из базы данных"""
        shop_db_manager = self.browser.db_managers["shop"]
        table = self.table
        for item in table.get_children():
            table.delete(item)

        self.content = shop_db_manager.load_content(self.filter)

        phone_count = 0
        for phone_id, phone_item in self.content.items():
            phone_count += 1
            item = (
                phone_count,
                phone_item["modelname"],
                "стоимость:",
                phone_item["price"],
            )
            table.insert("", tk.END, values=item, text=str(phone_id), tags=("group",))

            for _, value_dict in phone_item["components"].items():
                item = (
                    "",
                    "",
                    value_dict["description"],
                    value_dict["value"],
                )
                table.insert("", tk.END, values=item, text=str(phone_id))

    def __create_table(self) -> None:
        """Создание табличной части"""
        win = self.window
        columns = ("count", "model", "charact", "value")
        self.table = ttk.Treeview(
            win, columns=columns, show="headings", selectmode="none"
        )
        self.table.grid(row=0, column=0, sticky="nsew")

        table = self.table
        table.heading("count", text="№ п/п", anchor="w")
        table.heading("model", text="Модель", anchor="w")
        table.heading("charact", text="Характеристика", anchor="w")
        table.heading("value", text="Значение", anchor="w")

        table.column("count", minwidth=0, width=50, stretch=tk.NO)

        table.tag_configure(
            "group",
            background="#A65500",
            foreground="white",
            font=("Arial", 10, "bold"),
        )

        vsb = tk.Scrollbar(win, orient=tk.VERTICAL, command=table.yview)
        table.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="NS")
        self.__refresh_table()

    def __clear_browser(self) -> None:
        """Очистка окна-родителя"""
        for item in self.master.grid_slaves():
            item.grid_forget()

    def setfilter(self, filt: dict) -> None:
        """Открытие окна с фильтром"""
        self.filter = filt
        self.run()

    def run(self) -> None:
        """Открытие окна без фильтра"""
        self.__clear_browser()
        self.__refresh_table()

        self.window.grid(sticky="WENS")
