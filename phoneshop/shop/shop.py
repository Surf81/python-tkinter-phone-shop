import tkinter as tk
from tkinter import ttk
from core.checkboxtreeview import CheckboxTreeview
from core.router import PageRunner, Router
from phoneshop.db.db import DB


class Shop(object):
    def __init__(self, browser, database: DB, access, user):
        self.master = browser
        self.window = tk.Frame(self.master)
        self.db = database
        self.access = access
        self.user = user
        self.widgets = dict()
        self.router = None
        self.pages = dict()
        self.__init()

    def __init(self):
        self.__init_pages()
        self.__create_router()
        self.__create_form()
        self.__create_pages()

    def __init_pages(self):
        for page in ("shop",):
            self.pages[page] = PageRunner()

    def __create_router(self):
        self.router = Router()
        self.router.register_rout("shop", self.pages["shop"].launch("run"))
        self.router.register_rout("shopfilter", self.pages["shop"].launch("setfilter"))

    def __create_pages(self):
        win = self.widgets["mainframe"]
        self.pages["shop"].set_page(ShopFrame(win, self.db))

    def __create_form(self):
        win = self.window
        tk.Grid.columnconfigure(win, 0, weight=1, minsize=200)
        tk.Grid.columnconfigure(win, 1, weight=15)
        tk.Grid.rowconfigure(win, 1, weight=1)

        self.widgets["topbar"] = TopBar(win, self.user)
        self.widgets["topbar"].grid(row=0, column=0, columnspan=2, sticky="WE")
        self.widgets["sidebar"] = SideBar(win, self.db, self.router)
        self.widgets["sidebar"].grid(row=1, column=0, sticky="WENS")
        self.widgets["mainframe"] = MainFrame(win)
        self.widgets["mainframe"].grid(row=1, column=1, sticky="WENS")

    def __clear_browser(self):
        for item in self.master.grid_slaves():
            item.grid_forget()

    def run(self):
        self.__clear_browser()
        self.widgets["topbar"].refresh()
        self.widgets["sidebar"].refresh()
        self.router("shop")()
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


class MyCheckboxTreeview(CheckboxTreeview):
    def __init__(self, browser, content, *args, **kwargs):
        super().__init__(browser, *args, **kwargs)
        self.content = None
        self.refresh(content)

    def refresh(self, content):
        self.content = content
        self.__build_elements_by_content()

    def __build_elements_by_content(self):
        for item in self.get_children():
            self.delete(item)

        for charact, item in self.content.items():
            self.insert(
                "",
                tk.END,
                charact,
                text=item["description"],
                tags=("checked" if item["checked"] else "unchecked",),
            )
            for value, value_item in item["values"].items():
                self.insert(
                    charact,
                    tk.END,
                    value,
                    text=value_item["description"],
                    tags=("checked" if value_item["checked"] else "unchecked",),
                )

    def get_content(self):
        return self.content

    def __change_content(self, content, iid, flag):
        for key, item in content.items():
            if key == iid:
                item["checked"] = flag
            values = item.get("values")
            if values:
                self.__change_content(values, iid, flag)

    def check_ancestor(self, item):
        self.__change_content(self.content, item, True)
        super().check_ancestor(item)

    def check_descendant(self, item):
        children = self.get_children(item)
        for iid in children:
            self.__change_content(self.content, iid, True)
        super().check_descendant(item)

    def uncheck_descendant(self, item):
        children = self.get_children(item)
        for iid in children:
            self.__change_content(self.content, iid, False)
        super().uncheck_descendant(item)

    def uncheck_ancestor(self, item):
        self.__change_content(self.content, item, False)
        super().uncheck_ancestor(item)

    def tristate_parent(self, item):
        self.__change_content(self.content, item, True)
        super().tristate_parent(item)


class SideBar(tk.Frame):
    def __init__(self, browser, database, router, *args, **kwargs):
        super().__init__(browser, *args, **kwargs)
        self.master = browser
        self.db = database
        self.router = router
        self.tree = None
        self.filteractive = None
        self.__create_form()

    def __make_filter(self):
        components = dict()
        iid = 0
        for key, item in self.db.get_components().items():
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

    def __create_form(self):
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

        ttk.Label(frame1, text="Магазин\n'Телефоны даром'", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="WE", pady=20
        )

        ttk.Label(frame1, text="Фильтр товаров", font=("Arial", 12, "bold")).grid(
            row=1, column=0, sticky="WE", pady=20
        )

        self.tree = MyCheckboxTreeview(frame1, self.__make_filter(), show="tree")
        self.tree.grid(row=2, column=0, sticky="WENS")

        self.tree.bind("<Button-1>", lambda _: self.__set_filter() if self.filteractive.get() else None, True)

        self.filteractive = tk.BooleanVar(frame1)
        tk.Checkbutton(frame1, text="Применить фильтр", variable=self.filteractive, command=self.__set_filter).grid(
            row=3, column=0, sticky="W", pady=[20, 20]
        )
        ttk.Separator(frame2, orient=tk.VERTICAL).grid(
            row=1, column=1, sticky="NS", padx=0
        )

    def __set_filter(self):
        if self.filteractive.get():
            components = dict()
            for _, item in self.tree.get_content().items():
                if item["checked"]:
                    values = components.setdefault(item["key"], list())
                    for _, values_item in item["values"].items():
                        if values_item["checked"]:
                            values.append(values_item["key"])
            self.router("shopfilter")(components)
        else:
            self.router("shopfilter")(None)

    def refresh(self):
        self.tree.refresh(self.__make_filter())



class MainFrame(tk.Frame):
    def __init__(self, browser, *args, **kwargs):
        super().__init__(browser, *args, **kwargs)
        self.master = browser
        self.__create_form()

    def __create_form(self):
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.rowconfigure(self, 0, weight=1)


class ShopFrame(object):
    def __init__(self, browser, database):
        self.master = browser
        self.db = database
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

    def __refresh_table(self):
        table = self.table
        for item in table.get_children():
            table.delete(item)

        self.content = self.db.load_content(self.filter)

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

    def __create_table(self):
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

        self.vsb = tk.Scrollbar(win, orient=tk.VERTICAL, command=table.yview)
        table.configure(yscrollcommand=self.vsb.set)
        self.vsb.grid(row=0, column=1, sticky="NS")
        self.__refresh_table()

    def __clear_browser(self):
        for item in self.master.grid_slaves():
            item.grid_forget()

    def setfilter(self, filter):
        self.filter = filter
        self.run()

    def run(self):
        self.__clear_browser()
        self.__refresh_table()

        self.window.grid(sticky="WENS")
