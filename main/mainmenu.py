import tkinter as tk
from tkinter import ttk

class MainMenu(object):
    def __init__(self, master, router, rule):
        self.master = master
        self.router = router
        self.rule = rule
        self.mainmenu = tk.Menu(master)
        self.create_menu()
    
    @staticmethod
    def __clear_menu(master):
        for el in master.winfo_children():
            el.destroy()


    def create_menu(self):
        self.__clear_menu(self.mainmenu)
        self.mainmenu.add_command(label="Магазин", command=self.router("shop"))
        
        if self.rule.is_allow("adminmenu"):
            self.mainmenu.add_command(label="Меню администратора", command=self.router(""))

        self.authoriazation = tk.Menu(self.mainmenu, tearoff=0)
        self.mainmenu.add_cascade(label="Вход / регистрация", menu=self.authoriazation)
        
        if self.rule.is_allow("logon"):
            self.authoriazation.add_command(label="Войти / Зарегистрироваться", command=self.router("auth"))
        if self.rule.is_allow("changeuser"):
            self.authoriazation.add_command(label="Сменить пользователя", command=self.router("changeuser"))
        self.authoriazation.add_command(label="Выход", command=self.router("quit"))

    def menu(self):
        return self.mainmenu
    
    refresh = create_menu

