import string
import tkinter as tk
from tkinter import ttk
from tkinter import font

from core.settings import *


class AuthForm:
    WIDTH = 400
    HEIGHT = 190

    def __init__(self, master_window, browser):
        self.master = master_window
        self.browser = browser
        self.dialog_window = None
        self.user = browser.user
        self.params = dict()
        self.widgets = dict()

    def __widgets_append(self, widgetname, widget, grid):
        self.widgets[widgetname] = {
            "widget": widget,
            "grid": grid,
        }

    @staticmethod
    def __character_limit(entry_text, length):
        if len(entry_text.get()) > 0:
            entry_text.set(entry_text.get()[:length])

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

    def run(self):
        self.dialog_window = tk.Toplevel(self.master)
        win = self.dialog_window

        win.wm_title("Авторизация")
        win.resizable(False, False)
        # auth.overrideredirect(True) # Режим работы без отдельного окна
        win.tkraise(self.master)
        win.grab_set()

        tk.Grid.columnconfigure(win, 0, weight=1)
        tk.Grid.columnconfigure(win, 1, weight=1)

        for param in (
            "login",
            "password",
            "error",
            "select",
            "fname",
            "sname",
            "pname",
        ):
            self.params[param] = tk.StringVar()

        # Контроль длины введенных строк
        self.params["login"].trace(
            "w",
            lambda *args: self.__character_limit(
                self.params["login"], LOGIN_LENGTH_MAX
            ),
        )
        self.params["password"].trace(
            "w",
            lambda *args: self.__character_limit(
                self.params["password"], PASSWORD_LENGTH_MAX
            ),
        )
        self.params["fname"].trace(
            "w", lambda *args: self.__character_limit(self.params["fname"], 50)
        )
        self.params["sname"].trace(
            "w", lambda *args: self.__character_limit(self.params["sname"], 50)
        )
        self.params["pname"].trace(
            "w", lambda *args: self.__character_limit(self.params["pname"], 50)
        )

        self.check_login = (win.register(self.__validate_login), "%P")
        self.check_password = (win.register(self.__validate_password), "%P")

        self.__logon_dialog()

    def __set_window_size(self, width, height):
        self.__destroy_widgets()

        trans_x = (self.master.winfo_screenwidth() - width) // 2
        trans_y = (self.master.winfo_screenheight() - height) // 2 - 50
        self.dialog_window.geometry(
            "{}x{}+{}+{}".format(width, height, trans_x, trans_y)
        )

    def __destroy_widgets(self):
        for widget in self.widgets.values():
            widget["widget"].destroy()
        self.widgets = dict()

    def __show_widgets(self):
        for widget in self.widgets.values():
            widget["widget"].grid(**widget["grid"])

    def __add_login_password(self):
        win = self.dialog_window
        bold_font = font.Font(weight="bold")

        error = self.params["error"].get()

        self.__widgets_append(
            "lbl1",
            tk.Label(win, text="Логин*:", font=bold_font),
            dict(row=0, column=0, padx=[40, 10], pady=[30, 0], sticky="W"),
        )
        self.__widgets_append(
            "login",
            tk.Entry(
                win,
                width=LOGIN_LENGTH_MAX,
                textvariable=self.params["login"],
                validate="key",
                validatecommand=self.check_login,
            ),
            dict(row=0, column=1, padx=[10, 40], pady=[30, 0], sticky="WE"),
        )
        self.__widgets_append(
            "lbl2",
            tk.Label(win, text="Пароль*:", font=bold_font),
            dict(row=1, column=0, padx=[40, 10], pady=[10, 0], sticky="W"),
        )
        self.__widgets_append(
            "password",
            tk.Entry(
                win,
                show="*",
                width=PASSWORD_LENGTH_MAX,
                textvariable=self.params["password"],
                validate="key",
                validatecommand=self.check_password,
            ),
            dict(row=1, column=1, padx=[10, 40], pady=[10, 0], sticky="WE"),
        )
        self.__widgets_append(
            "error",
            tk.Label(win, fg="red", textvariable=self.params["error"], height=2),
            dict(row=2, column=0, columnspan=2, padx=40),
        )
        self.widgets["login"]["widget"].focus_set()
        self.params["error"].set(error)

    def __logon_dialog(self):
        win = self.dialog_window
        self.__set_window_size(self.WIDTH, self.HEIGHT)
        self.__add_login_password()

        self.__widgets_append(
            "btn_logon",
            ttk.Button(win, text="Войти / Зарегистрироваться", command=self.__logon),
            dict(row=10, column=0, columnspan=2, pady=[10, 30]),
        )

        self.__show_widgets()

    def __logon_with_role_dialog(self):
        win = self.dialog_window
        self.__set_window_size(self.WIDTH, self.HEIGHT)

        login = self.params["login"].get()
        password = self.params["password"].get()
        roles = self.user.logon(login, password)
        roles = {item["description"]: item for _, item in roles.items()}

        # Добро пожаловать

        name = list(roles.values())[0].get("secondname", "") or list(roles.values())[
            0
        ].get("login", "")

        self.__widgets_append(
            "lbl1",
            tk.Label(win, text="Добро пожаловать, {}!".format(name), fg="red"),
            dict(row=0, column=0, padx=[40, 10], pady=[30, 20], sticky="W"),
        )
        self.__widgets_append(
            "lbl3",
            tk.Label(win, text="Уровень доступа:"),
            dict(row=3, column=0, padx=[40, 10], pady=[10, 0], sticky="W"),
        )
        self.__widgets_append(
            "select",
            ttk.Combobox(
                win, values=list(roles.keys()), textvariable=self.params["select"]
            ),
            dict(row=3, column=1, padx=[10, 40], pady=[10, 0], sticky="WE"),
        )
        self.__widgets_append(
            "btn_logon",
            ttk.Button(
                win,
                text="Войти",
                command=lambda: self.__logon_with_role(
                    roles[self.params["select"].get()]
                ),
                state=tk.DISABLED,
            ),
            dict(row=12, column=0, columnspan=2, pady=[30, 30]),
        )
        self.widgets["select"]["widget"].bind(
            "<<ComboboxSelected>>",
            lambda event: self.widgets["btn_logon"]["widget"].config(state=tk.NORMAL),
        )

        self.__show_widgets()

    def __logon_or_register_dialog(self):
        win = self.dialog_window

        self.params["error"].set("комбинация логин/пароль не обнаружена")

        self.__set_window_size(self.WIDTH, self.HEIGHT + 100)
        self.__add_login_password()

        self.__widgets_append(
            "lbl3",
            tk.Label(win, text="Фамилия:"),
            dict(row=3, column=0, padx=[40, 10], pady=[10, 0], sticky="W"),
        )
        self.__widgets_append(
            "fname",
            tk.Entry(win, textvariable=self.params["fname"]),
            dict(row=3, column=1, padx=[10, 40], pady=[10, 0], sticky="WE"),
        )
        self.__widgets_append(
            "lbl4",
            tk.Label(win, text="Имя:"),
            dict(row=4, column=0, padx=[40, 10], pady=[10, 0], sticky="W"),
        )
        self.__widgets_append(
            "sname",
            tk.Entry(win, textvariable=self.params["sname"]),
            dict(row=4, column=1, padx=[10, 40], pady=[10, 0], sticky="WE"),
        )
        self.__widgets_append(
            "lbl5",
            tk.Label(win, text="Отчество:"),
            dict(row=5, column=0, padx=[40, 10], pady=[10, 0], sticky="W"),
        )
        self.__widgets_append(
            "pname",
            tk.Entry(win, textvariable=self.params["pname"]),
            dict(row=5, column=1, padx=[10, 40], pady=[10, 0], sticky="WE"),
        )
        self.__widgets_append(
            "btn_logon",
            ttk.Button(win, text="Войти", command=self.__logon),
            dict(row=10, column=0, padx=[40, 5], pady=[20, 30], sticky="E"),
        )
        self.__widgets_append(
            "btn_reg",
            ttk.Button(win, text="Зарегистрироваться", command=self.__create_user),
            dict(row=10, column=1, padx=[5, 40], pady=[20, 30], sticky="W"),
        )

        self.__show_widgets()

    def __logon(self):
        win = self.dialog_window
        login = self.params["login"].get()
        password = self.params["password"].get()

        if not (login and password):
            self.params["error"].set("логин и пароль должны быть заполнены")
            self.__logon_dialog()
            return

        roles = self.user.logon(login, password)

        if roles:
            if len(roles) == 1:
                self.user.set_role(list(roles.values())[0])
                self.master.event_generate("<<UserChange>>")
                win.destroy()
            else:
                self.__logon_with_role_dialog()
        else:
            if not self.user.is_free_login(login):
                self.params["error"].set("пароль не верный или пользователь заблокирован")
                self.__logon_dialog()
            else:
                self.__logon_or_register_dialog()

    def __logon_with_role(self, role):
        self.user.set_role(role)
        self.master.event_generate("<<UserChange>>")
        self.dialog_window.destroy()

    def __create_user(self):
        login = self.params["login"].get().strip()
        password = self.params["password"].get().strip()

        if not (login and password):
            self.params["error"].set("логин и пароль должны быть заполнены")
            self.__logon_dialog()
            return
        if len(login) < LOGIN_LENGTH_MIN or len(password) < PASSWORD_LENGTH_MIN:
            self.params["error"].set(
                "логин и пароль должны быть не менее {} знаков".format(
                    PASSWORD_LENGTH_MIN
                    if PASSWORD_LENGTH_MIN == LOGIN_LENGTH_MIN
                    else f"{LOGIN_LENGTH_MIN} и {PASSWORD_LENGTH_MIN}"
                )
            )
            return
        if not self.user.is_free_login(login):
            self.__logon()
            return

        roles = self.user.new_user(
            {
                "login": login,
                "password": password,
                "firstname": self.params["fname"].get().strip(),
                "secondname": self.params["sname"].get().strip(),
                "patronymic": self.params["pname"].get().strip(),
            }
        )
        role = list(roles.values())[0]
        self.user.set_role(role)
        self.master.event_generate("<<UserChange>>")
        self.dialog_window.destroy()
