import tkinter as tk
from tkinter import ttk

class MainMenu(object):
    def __init__(self, master, router, rule):
        self.master = master
        self.router = router
        self.rule = rule
        self.mainmenu = tk.Menu(master)
        self.create_menu()
    

    def create_menu(self):
        self.mainmenu.delete(0, 2)            
        self.mainmenu.add_command(label="Магазин", command=self.router("shop"))


        if self.rule.is_allow("adminmenu"):
            self.mainmenu.add_command(label="Меню администратора", command=self.router(""))

        authoriazation = tk.Menu(self.mainmenu, tearoff=0)
        if self.rule.is_allow("logon"):
            authoriazation.add_command(label="Войти / Зарегистрироваться", command=self.router("logon"))
        if self.rule.is_allow("changeuser"):
            authoriazation.add_command(label="Сменить пользователя", command=self.router("changeuser"))
        authoriazation.add_separator()
        authoriazation.add_command(label="Выход", command=self.router("quit"))
        self.mainmenu.add_cascade(label="Вход / регистрация", menu=authoriazation)


    def menu(self):
        return self.mainmenu
    
    refresh = create_menu

