import tkinter as tk
from tkinter import ttk

class MainMenu(object):
    def __init__(self, master, router):
        self.master = master
        self.menu = tk.Menu(master)

        self.menu.add_command(label="Магазин", command=router("shop"))
        self.menu.add_command(label="Меню администратора", command=router(""))

        self.authoriazation = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Вход / регистрация", menu=self.authoriazation)
        
        self.authoriazation.add_command(label="Войти / Зарегистрироваться", command=router("login"))
        self.authoriazation.add_command(label="Сменить пользователя", command=router("changeuser"))
        self.authoriazation.add_command(label="Выход", command=router("quit"))


    def create_menu(self):
        return self.menu



class PhoneShop(tk.Tk):
    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings
        self.__setup()


    def add_menu(self, menu):
        self.config(menu=menu)


    def __setup(self):
        self.title(self.settings.title)
        self.minsize(width=800, height=600)

        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.rowconfigure(self, 0, weight=1)

        width = min(self.settings.screen.scale.width, self.winfo_screenwidth())
        height = min(self.settings.screen.scale.height, self.winfo_screenheight())

        if (self.settings.screen.position.translate_x < 0
           or self.settings.screen.position.translate_x + width > self.winfo_screenwidth()):
            trans_x = (self.winfo_screenwidth() - width) // 2 
        else:
            trans_x = self.settings.screen.position.translate_x
            
        if (self.settings.screen.position.translate_y < 0
           or self.settings.screen.position.translate_y + height > self.winfo_screenheight()):
            trans_y = (self.winfo_screenheight() - height) // 2 
        else:
            trans_y = self.settings.screen.position.translate_y
        self.geometry("{}x{}+{}+{}".format(width, height, trans_x, trans_y))
        # self.deiconify()


    def run(self):
        self.mainloop()
