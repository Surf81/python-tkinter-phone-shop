import string
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askquestion, showerror

from core.settings import *


class UserAdminFrame(object):
    def __init__(self, browser, database, user):
        self.master = browser
        self.db = database
        self.user = user
        self.window = tk.Frame(self.master)
        self.list = None
        self.params = dict()
        self.widgets = dict()
        self.form = tk.Frame(self.window)
        self.current_login = ""
        self.__create_form()

    def __create_form(self):
        win = self.window
        tk.Grid.columnconfigure(win, 0, weight=1)
        tk.Grid.rowconfigure(win, 0, weight=1)
        tk.Grid.rowconfigure(win, 1, weight=2)

        self.__create_list()
        self.__create_bottom_form()

    def __on_list_click(self, event):
        item = self.list.identify("item", event.x, event.y)
        login = self.list.item(item, "text")
        if login:
            self.__load_data_in_form(login)

    def __refresh_list(self):
        list = self.list
        for item in list.get_children():
            list.delete(item)

        all_users = self.db.get_user_list()
        for count, user in enumerate(all_users.values(), start=1):
            item = (
                count,
                user["login"],
                ", ".join(user["role"].values()),
                "Активный" if user["exist"] else "Удалён",
            )
            list.insert("", tk.END, values=item, text=user["login"])

    def __create_list(self):
        win = self.window
        columns = ("count", "login", "roles", "exist")
        self.list = ttk.Treeview(win, columns=columns, show="headings")
        self.list.grid(row=0, column=0, sticky="nsew")

        list = self.list
        list.heading("count", text="№ п/п", anchor="w")
        list.heading("login", text="Логин", anchor="w")
        list.heading("roles", text="Права доступа", anchor="w")
        list.heading("exist", text="Состояние", anchor="w")

        list.column("count", minwidth=0, width=50, stretch=tk.NO)
        list.column("exist", minwidth=0, width=100, stretch=tk.NO)

        self.vsb = tk.Scrollbar(win, orient=tk.VERTICAL, command=list.yview)
        list.configure(yscrollcommand=self.vsb.set)
        self.vsb.grid(row=0, column=1, sticky="NS")
        list.bind("<Button-1>", self.__on_list_click)
        self.__refresh_list()

    def __clear_list_selection(self):
        for item in self.list.selection():
            self.list.selection_remove(item)

    def __character_limit(self, entry_text, length):
        self.params["change"].set(True)
        if len(entry_text.get()) > 0:
            entry_text.set(entry_text.get()[:length])

    def __on_change_form_data(self, flag):
        self.__clear_list_selection()
        if (
            flag.get()
            and len(self.params["login"].get()) >= LOGIN_LENGTH_MIN
            and len(self.params["password"].get()) >= PASSWORD_LENGTH_MIN
            and len(self.params["access"])
        ):
            if self.params["login"].get() == self.current_login:
                self.widgets["btn-saveform"].config(state=tk.NORMAL, text="Сохранить")
            else:
                self.widgets["btn-saveform"].config(
                    state=tk.NORMAL, text="Создать нового пользователя"
                )
        else:
            self.widgets["btn-saveform"].config(state=tk.DISABLED)
        if flag.get() or not self.current_login:
            self.widgets["btn-delitem"].config(state=tk.DISABLED)
        else:
            self.widgets["btn-delitem"].config(state=tk.NORMAL)

    def __on_change_checkbox(self, flag):
        self.params["change"].set(True)

    def __validate_login(self, newval):
        valid_chars = string.ascii_letters + string.digits + "_"
        for char in newval:
            if char not in valid_chars:
                self.params["error"].set(
                    "только символы английского алфавита,\nцифры и знак '_'"
                )
                return False
        self.params["error"].set("")
        return True

    def __validate_password(self, newval):
        valid_chars = string.ascii_letters + string.digits + "_!#$%^{}[]():|"
        for char in newval:
            if char not in valid_chars:
                self.params["error"].set(
                    "только символы английского алфавита,\nцифры и символы _!#$%^{}[]():| "
                )
                return False
        self.params["error"].set("")
        return True

    def __get_available_access(self):
        access = [
            item
            for key, item in self.db.get_roles().items()
            if key not in self.params["access"]
        ]
        if access:
            self.params["availableaccess"].set(access[0])
        else:
            self.params["availableaccess"].set("")
        return access

    def __load_data_in_form(self, login):
        login = login.strip()
        if not login:
            return
        if not self.db.is_free_login(login):
            self.current_login = login

            user = self.db.get_user(login)
            self.params["login"].set(user["login"])
            self.params["password"].set(user["password"])
            self.params["fname"].set(user["firstname"])
            self.params["sname"].set(user["secondname"])
            self.params["pname"].set(user["patronymic"])
            self.params["exist"].set(user["exist"])
            self.params["access"] = dict()

            self.widgets["access"].delete(0, tk.END)

            for role in user["role"]:
                self.params["access"][role] = user["role"][role]
                self.widgets["access"].insert(tk.END, user["role"][role])
            self.widgets["availableaccess"].config(values=self.__get_available_access())
            self.widgets["btn-access-del"].config(state=tk.DISABLED)
            self.widgets["btn-delitem"].config(state=tk.NORMAL)
            self.widgets["btn-saveform"].config(state=tk.DISABLED)
            self.widgets["btn-clearform"].config(state=tk.NORMAL)

            self.params["change"].set(False)

    def __clear_data_in_form(self):
        self.current_login = ""

        for param in (
            "login",
            "password",
            "error",
            "fname",
            "sname",
            "pname",
            "availableaccess",
        ):
            self.params[param].set("")
        self.params["exist"].set(True)
        self.params["access"] = dict()

        self.widgets["access"].delete(0, tk.END)
        self.widgets["availableaccess"].config(values=self.__get_available_access())
        self.widgets["btn-access-del"].config(state=tk.DISABLED)
        self.widgets["btn-delitem"].config(state=tk.DISABLED)
        self.widgets["btn-saveform"].config(state=tk.DISABLED, text="Создать нового пользователя")

        self.__clear_list_selection()

        self.params["change"].set(False)

    def __create_bottom_form(self):
        tk.Grid.columnconfigure(self.form, 0, weight=1)
        tk.Grid.columnconfigure(self.form, 1, weight=1)
        tk.Grid.columnconfigure(self.form, 4, weight=1)

        form = self.form
        params = self.params
        widgets = self.widgets
        form.grid(row=1, column=0, sticky="WENS")
        ttk.Label(form, text="Логин:").grid(
            row=0, column=0, sticky="w", padx=[10, 5], pady=[30, 0]
        )
        ttk.Label(form, text="Пароль:").grid(
            row=1, column=0, sticky="w", padx=[10, 5], pady=[5, 0]
        )
        ttk.Label(form, text="Фамилия:").grid(
            row=3, column=0, sticky="w", padx=[10, 5], pady=[5, 0]
        )
        ttk.Label(form, text="Имя:").grid(
            row=4, column=0, sticky="w", padx=[10, 5], pady=[5, 0]
        )
        ttk.Label(form, text="Отчество:").grid(
            row=5, column=0, sticky="w", padx=[10, 5], pady=[5, 0]
        )
        ttk.Label(form, text="Права доступа:").grid(
            row=6, column=0, sticky="w", padx=[10, 5], pady=[5, 0]
        )
        ttk.Label(form, text="Пользователь активен:").grid(
            row=7, column=0, sticky="w", padx=[10, 5], pady=[5, 0]
        )

        for param in (
            "login",
            "password",
            "error",
            "fname",
            "sname",
            "pname",
            "availableaccess",
        ):
            params[param] = tk.StringVar()
        params["exist"] = tk.BooleanVar()
        params["change"] = tk.BooleanVar()
        params["access"] = dict()

        params["login"].trace(
            "w", lambda *args: self.__character_limit(self.params["login"], LOGIN_LENGTH_MAX)
        )
        params["password"].trace(
            "w", lambda *args: self.__character_limit(self.params["password"], PASSWORD_LENGTH_MAX)
        )
        params["fname"].trace(
            "w", lambda *args: self.__character_limit(self.params["fname"], 50)
        )
        params["sname"].trace(
            "w", lambda *args: self.__character_limit(self.params["sname"], 50)
        )
        params["pname"].trace(
            "w", lambda *args: self.__character_limit(self.params["pname"], 50)
        )
        params["change"].trace(
            "w", lambda *args: self.__on_change_form_data(self.params["change"])
        )
        params["exist"].trace(
            "w", lambda *args: self.__on_change_checkbox(self.params["exist"])
        )

        tk.Label(
            form, text="", height=2, textvariable=self.params["error"], fg="red"
        ).grid(row=2, column=0, columnspan=2, sticky="we", padx=10, pady=[5, 0])

        self.check_login = (self.master.register(self.__validate_login), "%P")
        self.check_password = (self.master.register(self.__validate_password), "%P")

        widgets["login"] = ttk.Entry(
            form,
            textvariable=params["login"],
            width=LOGIN_LENGTH_MAX,
            validate="key",
            validatecommand=self.check_login,
        )
        widgets["password"] = ttk.Entry(
            form,
            textvariable=params["password"],
            width=PASSWORD_LENGTH_MAX,
            validate="key",
            validatecommand=self.check_password,
        )
        widgets["fname"] = ttk.Entry(form, textvariable=params["fname"], width=50)
        widgets["sname"] = ttk.Entry(form, textvariable=params["sname"], width=50)
        widgets["pname"] = ttk.Entry(form, textvariable=params["pname"], width=50)
        widgets["access"] = tk.Listbox(form, selectmode=tk.SINGLE, width=0, height=0)
        widgets["exist"] = tk.Checkbutton(
            form, variable=params["exist"], onvalue=1, offvalue=0
        )
        widgets["btn-access-del"] = tk.Button(
            form, text="Del", fg="red", state=tk.DISABLED, command=self.__del_access
        )
        widgets["btn-access-add"] = tk.Button(
            form, text="Add", fg="red", command=self.__add_access
        )
        widgets["availableaccess"] = ttk.Combobox(
            form,
            values=self.__get_available_access(),
            state=tk.READABLE,
            textvariable=params["availableaccess"],
        )

        widgets["btn-clearform"] = tk.Button(
            form, text="Очистить поля", fg="red", command=self.__clear_data_in_form
        )
        widgets["btn-saveform"] = tk.Button(
            form,
            text="Создать нового пользователя",
            fg="red",
            state=tk.DISABLED,
            command=self.__create_new_user_or_update,
        )
        widgets["btn-delitem"] = tk.Button(
            form,
            text="Удалить запись",
            fg="red",
            state=tk.DISABLED,
            command=self.__del_item_from_db,
        )

        widgets["login"].grid(row=0, column=1, sticky="we", pady=[30, 0])
        widgets["password"].grid(row=1, column=1, sticky="we", pady=[5, 0])
        widgets["fname"].grid(row=3, column=1, sticky="we", pady=[5, 0])
        widgets["sname"].grid(row=4, column=1, sticky="we", pady=[5, 0])
        widgets["pname"].grid(row=5, column=1, sticky="we", pady=[5, 0])
        widgets["access"].grid(row=6, column=1, sticky="we", pady=[5, 0])
        widgets["btn-access-del"].grid(row=6, column=2, sticky="we", pady=[5, 0])
        widgets["btn-access-add"].grid(row=6, column=3, sticky="we", pady=[5, 0])
        widgets["availableaccess"].grid(row=6, column=4, sticky="we", pady=[5, 0])
        widgets["exist"].grid(row=7, column=1, sticky="w", pady=[5, 0])
        widgets["btn-clearform"].grid(row=8, column=0, sticky="we", pady=[5, 0])
        widgets["btn-saveform"].grid(row=8, column=1, sticky="we", pady=[5, 0])
        widgets["btn-delitem"].grid(
            row=8, column=2, columnspan=3, sticky="we", pady=[5, 0]
        )

        self.widgets["access"].bind("<<ListboxSelect>>", self.__on_select_listbox)
        self.__clear_data_in_form()

    def __on_select_listbox(self, event):
        if event.widget.curselection() and len(self.params["access"]) > 1:
            self.widgets["btn-access-del"].config(state=tk.NORMAL)
        else:
            self.widgets["btn-access-del"].config(state=tk.DISABLED)

    def __add_access(self):
        if self.params["availableaccess"].get():
            self.widgets["access"].insert(tk.END, self.params["availableaccess"].get())
            self.params["access"].update(
                {
                    key: item
                    for key, item in self.db.get_roles().items()
                    if item == self.params["availableaccess"].get()
                }
            )
            self.widgets["availableaccess"].config(values=self.__get_available_access())
            self.params["change"].set(True)

    def __del_access(self):
        if (cursel := self.widgets["access"].curselection()) and len(
            self.params["access"]
        ) > 1:
            access = self.widgets["access"].get(cursel[0])

            if (
                self.current_login == self.user.user["login"]
                or self.params["login"].get() == self.user.user["login"]
            ) and access == self.user.user["role_descriptor"]:
                showerror(
                    "Удаление невозможно",
                    "Удалаямая запись в настоящее время является активной!",
                )
                return

            self.widgets["access"].delete(cursel[0])
            self.params["access"] = {
                key: item
                for key, item in self.params["access"].items()
                if item != access
            }
            self.widgets["availableaccess"].config(values=self.__get_available_access())
            self.widgets["btn-access-del"].config(state=tk.DISABLED)
            self.params["change"].set(True)

    def __del_item_from_db(self):
        if self.current_login and self.current_login == self.params["login"].get():
            if self.current_login == self.user.user["login"]:
                showerror(
                    "Удаление невозможно",
                    "Удалаямая запись в настоящее время является активной!",
                )
            elif (
                askquestion(
                    "Запрос на удаление",
                    "Действительно ходите удалить запись пользователя {}?".format(
                        self.current_login
                    ),
                )
                == "yes"
            ):
                if self.db.delete_user(self.current_login):
                    self.__refresh_list()
                    self.__clear_data_in_form()
                else:
                    showerror("Ошибка удаления", "Удаление прошло не удачно")

    def __create_new_user_or_update(self):
        params = self.params
        if not(params["login"].get() and params["password"].get()):
            return
        userdata = {
            "login": params["login"].get(),
            "password": params["password"].get(),
            "firstname": params["fname"].get().strip(),
            "secondname": params["sname"].get().strip(),
            "patronymic": params["pname"].get().strip(),
            "exist": params["exist"].get(),
            "roles": list(),
        }
        
        for role in params["access"].keys():
            userdata["roles"].append(role)

        if self.db.is_free_login(userdata["login"]):
            self.db.new_user(userdata)
        else:
            self.db.update_user(userdata)
        self.__refresh_list()
        self.__clear_data_in_form()


    def __clear_browser(self):
        for item in self.master.grid_slaves():
            item.grid_forget()

    def run(self):
        self.__clear_browser()
        self.__refresh_list()
        self.__clear_data_in_form()

        self.window.grid(sticky="WENS")
