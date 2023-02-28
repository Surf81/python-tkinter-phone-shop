import tkinter as tk
from tkinter import ttk


class AuthDialog():
    WIDTH = 400
    HEIGHT = 170

    def __init__(self, master, user):
        self.master = master
        self.user = user


    @staticmethod
    def __character_limit(entry_text, length):
        if len(entry_text.get()) > 0:
            entry_text.set(entry_text.get()[:length])


    def open_dialog(self):
        def log_with_role(role):
            self.user.set_role(role)
            self.master.event_generate("<<UserChange>>")
            auth.destroy()


        def logon():
            roles = self.user.logon(login_text.get(), password_text.get())

            if roles:
                login_widget.config(state=tk.DISABLED)
                password_widget.config(state=tk.DISABLED)
                btn_logon.grid_forget()
                if len(roles) == 1:
                    self.user.set_role(roles.values()[0])
                    self.master.event_generate("<<UserChange>>")
                    auth.destroy()
                else:
                    auth.geometry("{}x{}".format(self.WIDTH, self.HEIGHT+30))
                    roles = {item["description"]: item for _, item in roles.items()}

                    tk.Label(auth, text="Войти с ролью: ").grid(row=3, column=0, padx=[40,10], pady=[10,0], sticky="W")
                    select_text = tk.StringVar()
                    select_widget = ttk.Combobox(auth, values=list(roles.keys()), textvariable=select_text)
                    select_widget.grid(row=3, column=1, padx=[10,40], pady=[10,0], sticky="WE")
                    select_widget.bind("<<ComboboxSelected>>", lambda event: btn_select.config(state=tk.NORMAL))

                    btn_select = ttk.Button(auth, text="Войти с ролью", command=lambda: log_with_role(roles[select_text.get()]), state=tk.DISABLED)
                    btn_select.grid(row=11, column=0, columnspan=2, pady=[10, 30])


            if not roles:
                error_widget.config(text="комбинация Логин/пароль не обнаружена")


        auth = tk.Toplevel(self.master)
        auth.wm_title("Авторизация")

        tk.Grid.columnconfigure(auth, 0, weight=1)
        tk.Grid.columnconfigure(auth, 1, weight=1)

        trans_x = (self.master.winfo_screenwidth() - self.WIDTH) // 2 
        trans_y = (self.master.winfo_screenheight() - self.HEIGHT) // 2 - 200 
        auth.geometry("{}x{}+{}+{}".format(self.WIDTH, self.HEIGHT, trans_x, trans_y))
        
        tk.Label(auth, text="Логин: ").grid(row=0, column=0, padx=[40,10], pady=[30,0], sticky="W")
        login_text = tk.StringVar()
        login_widget = tk.Entry(auth, width=16, textvariable=login_text)
        login_widget.grid(row=0, column=1, padx=[10,40], pady=[30,0], sticky="WE")
        
        tk.Label(auth, text="Пароль: ").grid(row=1, column=0, padx=[40,10], pady=[10,0], sticky="W")
        password_text = tk.StringVar()
        password_widget = tk.Entry(auth, show="*", width=16, textvariable=password_text)
        password_widget.grid(row=1, column=1, padx=[10,40], pady=[10,0], sticky="WE")
        
        error_widget = tk.Label(auth, fg="red")
        error_widget.grid(row=2, column=0, columnspan=2, padx=40)

        btn_logon = ttk.Button(auth, text="Войти / Зарегистрироваться", command=logon)
        btn_logon.grid(row=10, column=0, columnspan=2, pady=[10, 30])

        login_text.trace("w", lambda *args: self.__character_limit(login_text, 16))
        password_text.trace("w", lambda *args: self.__character_limit(password_text, 16))

        login_widget.focus_set()
