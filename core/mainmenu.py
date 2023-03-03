import tkinter as tk
from tkinter import ttk

class MainMenu(object):
    def __init__(self, master, router, access):
        self.master = master
        self.router = router
        self.access = access
        self.mainmenu = tk.Menu(master)
        self.create_menu()
    

    def create_menu(self):
        self.mainmenu.delete(0, tk.END)            
        self.mainmenu.add_command(label="Магазин", command=self.router("shop"))

        if self.access.is_allow("adminmenu"):
            self.mainmenu.add_command(label="Меню администратора", command=self.router("admin"))

        authoriazation = tk.Menu(self.mainmenu, tearoff=0)
        if self.access.is_allow("logon"):
            authoriazation.add_command(label="Войти / Зарегистрироваться", command=self.router("logon"))
        if self.access.is_allow("changeuser"):
            authoriazation.add_command(label="Сменить пользователя", command=self.router("changeuser"))
        authoriazation.add_separator()
        authoriazation.add_command(label="Выход", command=self.router("quit"))
        self.mainmenu.add_cascade(label="Вход / регистрация", menu=authoriazation)


    def menu(self):
        return self.mainmenu
    
    refresh = create_menu
