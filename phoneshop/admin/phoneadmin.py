import string

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askquestion

from core.db.loadbase import load_phone_base


class PhoneAdminPage(object):
    def __init__(self, master_window, browser):
        self.browser = browser
        self.master = master_window
        self.window = tk.Frame(self.master)
        self.table = None
        self.form = tk.Frame(self.window)
        self.params = dict()
        self.widgets = dict()
        self.content = dict()
        self.form = tk.Frame(self.window)
        self.__create_form()

    def __refresh_content(self):
        shop_db_manager = self.browser.db_managers["shop"]
        self.params["allmodels"] = shop_db_manager.get_phone_models()
        self.params["allcharacteristics"] = shop_db_manager.get_characteristics()
        self.content = shop_db_manager.load_content()

    def __on_table_click(self, event):
        item = self.table.identify("item", event.x, event.y)
        phone_id = self.table.item(item, "text")
        if phone_id:
            self.__load_data_in_form(phone_id)

    def __refresh_table(self):
        self.__refresh_content()
        table = self.table
        for item in table.get_children():
            table.delete(item)

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
        columns = ("count", "login", "roles", "exist")
        self.table = ttk.Treeview(
            win, columns=columns, show="headings", selectmode="browse"
        )
        self.table.grid(row=0, column=0, sticky="nsew")

        table = self.table
        table.heading("count", text="№ п/п", anchor="w")
        table.heading("login", text="Логин", anchor="w")
        table.heading("roles", text="Права доступа", anchor="w")
        table.heading("exist", text="Состояние", anchor="w")

        table.column("count", minwidth=0, width=50, stretch=tk.NO)
        table.column("exist", minwidth=0, width=100, stretch=tk.NO)

        table.tag_configure("group", background="#007046", foreground="white")

        vsb = tk.Scrollbar(win, orient=tk.VERTICAL, command=table.yview)
        table.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="NS")
        table.bind("<Button-1>", self.__on_table_click)
        self.__refresh_table()

    def __create_form(self):
        win = self.window
        tk.Grid.columnconfigure(win, 0, weight=1)
        tk.Grid.rowconfigure(win, 0, weight=1)
        tk.Grid.rowconfigure(win, 1, weight=2)

        self.__create_table()
        self.__create_bottom_form()

    def __validate_price(self, newval):
        valid_chars = string.digits + "."
        self.params["formchange"].set(True)

        for char in newval:
            if char not in valid_chars:
                self.params["error"].set("допускаются только цифры и точка")
                return False
        if newval.startswith("."):
            self.params["error"].set("точка не может быть в начале")
            return False

        if newval.count(".") > 1:
            self.params["error"].set("точка может быть только одна")
            return False

        self.params["error"].set("")
        return True

    def __clear_data_in_form(self):
        self.params["phone_id"].set(0)
        self.widgets["modelname"].config(
            values=(tuple(self.params["allmodels"].values()))
        )
        self.params["model_id"] = 0
        self.params["modelname"].set("")
        self.params["price"].set("")

        components = self.widgets["components"]
        for item in components.get_children():
            components.delete(item)
        self.params["characteristics"] = dict()
        self.widgets["btn-del-component"].config(state=tk.DISABLED)
        self.params["formchange"].set(False)

    def __load_data_in_form(self, phone_id):
        phone = self.content[int(phone_id)]
        self.params["phone_id"].set(int(phone_id))
        self.widgets["modelname"].config(
            values=tuple(self.params["allmodels"].values())
        )
        self.params["model_id"] = phone["modelid"]
        self.params["modelname"].set(phone["modelname"])
        self.params["price"].set(phone["price"])

        components = self.widgets["components"]
        for item in components.get_children():
            components.delete(item)
        self.params["characteristics"] = dict()
        for charact, component in phone["components"].items():
            components.insert(
                "",
                tk.END,
                values=(component["description"], component["value"]),
                text=charact,
            )
            self.params["characteristics"].update({charact: dict(component)})

        self.widgets["btn-del-component"].config(state=tk.DISABLED)
        self.params["formchange"].set(False)

    def __del_buttons_available(self, *args, **kwargs):
        if self.params["phone_id"].get():
            self.widgets["btn-del-phone"].config(state=tk.NORMAL)
            self.widgets["btn-del-model"].config(state=tk.NORMAL)
        else:
            self.widgets["btn-del-phone"].config(state=tk.DISABLED)
            self.widgets["btn-del-model"].config(state=tk.DISABLED)

    def __on_form_change(self, flag):
        if flag:
            if self.params["modelname"].get() and self.params["price"].get():
                self.widgets["btn-update"].config(state=tk.NORMAL)
                self.widgets["btn-new_phone"].config(state=tk.NORMAL)
                return
        self.widgets["btn-update"].config(state=tk.DISABLED)
        self.widgets["btn-new_phone"].config(state=tk.DISABLED)

    def __on_component_click(self, event):
        item = self.widgets["components"].identify("item", event.x, event.y)
        characteristic = self.widgets["components"].item(item, "text")
        if characteristic:
            self.widgets["btn-del-component"].config(state=tk.NORMAL)

    def __delete_component(self):
        item = self.widgets["components"].focus()
        characteristic = self.widgets["components"].item(item, "text")
        if characteristic:
            self.params["characteristics"] = {
                charact: descr
                for charact, descr in self.params["characteristics"].items()
                if descr["description"] != characteristic
            }
            selected_item = self.widgets["components"].selection()[
                0
            ]  ## get selected item
            self.widgets["components"].delete(selected_item)
            self.params["formchange"].set(True)

    def __add_component(self, win, charact, value):
        if value:
            all_charact = {
                item: key for key, item in self.params["allcharacteristics"].items()
            }
            self.params["characteristics"].update(
                {all_charact[charact]: {"description": charact, "value": value}}
            )
            self.widgets["components"].insert(
                "", tk.END, values=(charact, value), text=charact
            )
            self.params["formchange"].set(True)
            win.destroy()

    def __fill_choice_widget(self, widget, charact):
        shop_db_manager = self.browser.db_managers["shop"]
        widget.delete(0, tk.END)
        for value in shop_db_manager.get_component_values(charact):
            widget.insert(tk.END, value)

    def __open__add_component_dialog(self):
        dialog_window = tk.Toplevel(self.window)
        win = dialog_window
        width = 400
        height = 250

        win.wm_title("Выбрать компонент")
        win.resizable(False, False)
        win.tkraise(self.master)
        win.grab_set()

        tk.Grid.columnconfigure(win, 0, weight=1)
        tk.Grid.columnconfigure(win, 1, weight=1)
        trans_x = (self.master.winfo_screenwidth() - width) // 2
        trans_y = (self.master.winfo_screenheight() - height) // 2 - 50
        win.geometry("{}x{}+{}+{}".format(width, height, trans_x, trans_y))

        tk.Label(win, text="Выберите характеристику:").grid(
            row=0, column=0, sticky="w", padx=[20, 0], pady=[20, 0]
        )

        charact_text = tk.StringVar(win)
        all_characteristics = self.params["allcharacteristics"]
        charact_widget = ttk.Combobox(
            win,
            values=tuple(
                item
                for key, item in all_characteristics.items()
                if key not in self.params["characteristics"]
            ),
            textvariable=charact_text,
            state="readonly",
        )
        charact_widget.grid(row=0, column=1, sticky="we", pady=[20, 0], padx=[5, 20])

        tk.Label(win, text="Введите значение:").grid(
            row=1, column=0, sticky="w", padx=[20, 0]
        )

        value_text = tk.StringVar(win)
        value_widget = ttk.Entry(win, textvariable=value_text)
        value_widget.grid(row=1, column=1, sticky="we", padx=[5, 20])
        value_text.trace("w", lambda *args: value_text.set(value_text.get()[:24]))

        tk.Label(win, text="Или выберите из списка:").grid(
            row=2, column=0, sticky="w", padx=[20, 0]
        )

        choice_widget = tk.Listbox(win, selectmode=tk.SINGLE, height=0)
        choice_widget.grid(row=3, column=0, columnspan=2, sticky="WE", padx=20, pady=5)
        choice_widget.bind("<<ListboxSelect>>", lambda *args: value_text.set(""))
        choice_widget.bind(
            "<Double-1>",
            lambda *args: self.__add_component(
                win,
                charact_text.get(),
                (
                    ""
                    if not choice_widget.curselection()
                    else choice_widget.get(choice_widget.curselection()[0])
                ),
            ),
        )

        all_characteristics = {value: key for key, value in all_characteristics.items()}
        charact_text.trace(
            "w",
            lambda *args: self.__fill_choice_widget(
                choice_widget, all_characteristics[charact_text.get()]
            ),
        )

        tk.Button(
            win,
            text="Добавить",
            command=lambda: self.__add_component(
                win,
                charact_text.get(),
                value_text.get().strip()
                or (
                    choice_widget.get(choice_widget.curselection()[0])
                    if choice_widget.curselection()
                    else ""
                ),
            ),
        ).grid(row=10, column=0, columnspan=2, sticky="we", padx=20, pady=20)

    def __change_modelname(self, *args, **kwargs):
        if self.params["modelname"].get():
            self.params["model_id"] = {
                item: key for key, item in self.params["allmodels"].items()
            }[self.params["modelname"].get()]
        self.params["formchange"].set(True)

    def __create_bottom_form(self):
        form = self.form

        self.widgets["btn-del-phone"] = tk.Button(
            form, fg="red", text="Очистить форму", command=self.__clear_data_in_form
        )
        self.widgets["btn-del-phone"].grid(row=0, column=0, columnspan=2, sticky="WE")

        ttk.Label(form, text="Модель:").grid(row=1, column=0, sticky="w")
        ttk.Label(form, text="Цена:").grid(row=2, column=0, sticky="w")

        self.params["characteristics"] = dict()
        self.params["allmodels"] = dict()
        self.params["characteristics"] = dict()
        self.params["phone_id"] = tk.IntVar()
        self.params["model_id"] = 0
        self.params["modelname"] = tk.StringVar()
        self.params["price"] = tk.StringVar()
        self.params["error"] = tk.StringVar()
        self.params["formchange"] = tk.BooleanVar()

        self.params["phone_id"].trace("w", self.__del_buttons_available)
        self.params["modelname"].trace("w", self.__change_modelname)
        self.params["formchange"].trace(
            "w", lambda *args: self.__on_form_change(self.params["formchange"].get())
        )

        check_price = (self.form.register(self.__validate_price), "%P")

        self.widgets["modelname"] = ttk.Combobox(
            form,
            textvariable=self.params["modelname"],
            values=tuple(self.params["allmodels"].values()),
            state="readonly",
        )
        self.widgets["modelname"].grid(row=1, column=1, sticky="WE")
        self.widgets["price"] = ttk.Entry(
            form,
            textvariable=self.params["price"],
            validate="key",
            validatecommand=check_price,
        )
        self.widgets["price"].grid(row=2, column=1, sticky="WE")
        self.widgets["error"] = ttk.Label(
            form, foreground="red", textvariable=self.params["error"]
        )
        self.widgets["error"].grid(row=3, column=0, columnspan=2, sticky="WE")

        self.widgets["btn-del-phone"] = tk.Button(
            form,
            fg="red",
            text="Удалить телефон",
            state=tk.DISABLED,
            command=self.__delete_phone,
        )
        self.widgets["btn-del-phone"].grid(row=0, column=4, sticky="WE")
        self.widgets["btn-del-model"] = tk.Button(
            form,
            fg="red",
            text="Удалить все телефоны данной модели",
            state=tk.DISABLED,
            command=self.__delete_model,
        )
        self.widgets["btn-del-model"].grid(row=1, column=4, sticky="WE")

        self.widgets["btn-new-model"] = tk.Button(
            form,
            fg="red",
            text="Добавить новую модель",
            command=self.__new_model,
        )
        self.widgets["btn-new-model"].grid(row=2, column=4, sticky="WE")

        columns = ("characteristic", "value")
        self.widgets["components"] = ttk.Treeview(
            form, columns=columns, show="headings", height=4, selectmode="browse"
        )
        components = self.widgets["components"]
        components.heading("characteristic", text="Характеристика", anchor="w")
        components.heading("value", text="Значение", anchor="w")

        components.grid(row=4, column=0, columnspan=2, sticky="nsew")
        vsb = tk.Scrollbar(form, orient=tk.VERTICAL, command=components.yview)
        components.configure(yscrollcommand=vsb.set)
        vsb.grid(row=4, column=3, sticky="NS")
        components.bind("<Button-1>", self.__on_component_click)

        self.widgets["btn-del-component"] = tk.Button(
            form,
            foreground="red",
            text="Удалить характеристику",
            state=tk.DISABLED,
            command=self.__delete_component,
        )
        self.widgets["btn-del-component"].grid(
            row=5, column=0, columnspan=2, sticky="WE"
        )
        self.widgets["btn-add-component"] = tk.Button(
            form,
            foreground="red",
            text="Добавить характеристику",
            state=tk.NORMAL,
            command=self.__open__add_component_dialog,
        )
        self.widgets["btn-add-component"].grid(
            row=6, column=0, columnspan=2, sticky="WE"
        )
        self.widgets["btn-update"] = tk.Button(
            form,
            foreground="red",
            text="Сохранить изменения",
            state=tk.DISABLED,
            command=self.__save_changes_or_create,
        )
        self.widgets["btn-update"].grid(row=7, column=0, columnspan=2, sticky="WE")
        self.widgets["btn-new_phone"] = tk.Button(
            form,
            foreground="red",
            text="Создать новую запись",
            state=tk.DISABLED,
            command=self.__save_changes_or_create,
        )
        self.widgets["btn-new_phone"].grid(row=8, column=0, columnspan=2, sticky="WE")

        self.widgets["btn-load-phones"] = tk.Button(
            form,
            foreground="green",
            text="Загрузить базу телефонов",
            state=tk.NORMAL,
            command=self.__load_phone_base,
        )
        self.widgets["btn-load-phones"].grid(row=10, column=0, columnspan=2, sticky="WE")

        self.params["formchange"].set(False)
        self.__refresh_content()
        self.widgets["modelname"].config(
            values=tuple(self.params["allmodels"].values())
        )
        form.grid(row=1, column=0, sticky="WENS", pady=20, padx=20)

    def __load_phone_base(self):
        shop_db_manager = self.browser.db_managers["shop"]
        load_phone_base(shop_db_manager)
        self.__refresh_table()
        self.__clear_data_in_form()

    def __delete_phone(self):
        shop_db_manager = self.browser.db_managers["shop"]
        if (
            self.params["phone_id"].get()
            and askquestion(
                "Удаление записи",
                "Вы точно хотите удалить запись телефона {}?".format(
                    self.params["modelname"].get()
                ),
            )
            == "yes"
        ):
            shop_db_manager.delete_phone(self.params["phone_id"].get())
            self.__refresh_table()
            self.__clear_data_in_form()

    def __delete_model(self):
        shop_db_manager = self.browser.db_managers["shop"]
        if (
            self.params["model_id"]
            and askquestion(
                "Удаление записи",
                "Вы точно хотите удалить все записи телефонов {}?".format(
                    self.params["modelname"].get()
                ),
            )
            == "yes"
        ):
            shop_db_manager.delete_phones_by_model(self.params["model_id"])
            self.__refresh_table()
            self.__clear_data_in_form()

    def __add_new_model(self, win, model):
        shop_db_manager = self.browser.db_managers["shop"]
        if model:
            if shop_db_manager.new_model(model) != -1:
                self.__refresh_content()
                self.__clear_data_in_form()
                win.destroy()

    def __new_model(self):
        dialog_window = tk.Toplevel(self.window)
        win = dialog_window
        width = 400
        height = 150

        win.wm_title("Выбрать компонент")
        win.resizable(False, False)
        # auth.overrideredirect(True) # Режим работы без отдельного окна
        win.tkraise(self.master)
        win.grab_set()

        tk.Grid.columnconfigure(win, 0, weight=1)
        tk.Grid.columnconfigure(win, 1, weight=1)
        trans_x = (self.master.winfo_screenwidth() - width) // 2
        trans_y = (self.master.winfo_screenheight() - height) // 2 - 50
        win.geometry("{}x{}+{}+{}".format(width, height, trans_x, trans_y))

        tk.Label(win, text="Введите название модели:").grid(
            row=0, column=0, sticky="w", padx=[20, 0], pady=[20, 0]
        )
        model_text = tk.StringVar(win)
        model_widget = tk.Entry(win, textvariable=model_text)
        model_widget.grid(row=0, column=1, sticky="we", padx=[5, 20], pady=[20, 0])
        model_text.trace("w", lambda *args: model_text.set(model_text.get()[:24]))

        tk.Button(
            win,
            text="Добавить",
            command=lambda: self.__add_new_model(win, model_text.get().strip()),
        ).grid(row=10, column=0, columnspan=2, sticky="we", padx=20, pady=20)

    def __save_changes_or_create(self):
        shop_db_manager = self.browser.db_managers["shop"]
        phone = {
            "phone_id": self.params["phone_id"].get(),
            "model_id": self.params["model_id"],
            "modelname": self.params["modelname"].get().strip(),
            "price": float(self.params["price"].get().strip()),
            "components": self.params["characteristics"],
        }
        shop_db_manager.add_or_update_phone(phone)
        self.__refresh_table()
        self.__clear_data_in_form()

    def __clear_browser(self):
        for item in self.master.grid_slaves():
            item.grid_forget()

    def run(self):
        self.__clear_browser()
        self.__refresh_table()

        self.window.grid(sticky="WENS")
