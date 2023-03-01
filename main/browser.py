import tkinter as tk
from tkinter import ttk
from main.mainmenu import MainMenu
from main.router import Router

from main.settingloader import PhoneShopSettings
from main.settings import SETTINGS_FILE
from phoneshop.auth.authdialog import AuthDialog
from phoneshop.shop.shopframe import Shop



class Browser(object):
    def __init__(self, database, user, rule, *args, **kwargs):
        self.db = database
        self.user = user
        self.rule = rule
        self.window = tk.Tk()
        self.settings = None
        self.router = None
        self.menu = None
        self.pages = dict()
        self.__create_pages()
        self.__base_init()
        self.__init()
        self.window.mainloop()


    def __clear_window(self, master):
        for el in master.winfo_children():
            el.destroy()


    def __create_pages(self):
        self.pages["logon"] = AuthDialog(self.window, self.user)
        self.pages["shop"] = Shop(self.window, self.db)


    def __base_init(self):
        # self.__clear_window(self.window)
        self.__load_settings()
        self.__create_router()
        self.__create_virtual_events()
        self.__create_environment()


    def __init(self):
        self.__create_menu()

    refresh = __init

    def __load_settings(self):
        if not self.settings:
            self.settings = PhoneShopSettings(SETTINGS_FILE)

    def __create_router(self):
        if not self.router:
            self.router = Router()
            self.router.register_rout("refresh", self.refresh)
            self.router.register_rout("shop", self.pages["shop"].run, history=True)
            self.router.register_rout("logon", self.pages["logon"].logon_dialog)
            self.router.register_rout("changeuser", self.pages["logon"].logon_dialog)
            self.router.register_rout("quit", self.window.destroy)

    def __create_menu(self):
        if not self.menu:
            self.menu = MainMenu(self.window, self.router, self.rule)
            # self.window.add_menu(self.menu.menu())
            self.window.config(menu=self.menu.menu())
        else:
            self.menu.refresh()


    def __create_virtual_events(self):
        self.window.event_add("<<UserChange>>", "None")
        self.window.bind("<<UserChange>>", self.router.refresh_event,"%d")


    def __create_environment(self):
        self.window.title(self.settings.title)
        self.window.minsize(width=800, height=600)

        tk.Grid.columnconfigure(self.window, 0, weight=1)
        tk.Grid.rowconfigure(self.window, 0, weight=1)

        width = min(self.settings.screen.scale.width, self.window.winfo_screenwidth())
        height = min(self.settings.screen.scale.height, self.window.winfo_screenheight())

        if (self.settings.screen.position.translate_x < 0
           or self.settings.screen.position.translate_x + width > self.window.winfo_screenwidth()):
            trans_x = (self.window.winfo_screenwidth() - width) // 2 
        else:
            trans_x = self.settings.screen.position.translate_x
            
        if (self.settings.screen.position.translate_y < 0
           or self.settings.screen.position.translate_y + height > self.window.winfo_screenheight()):
            trans_y = (self.window.winfo_screenheight() - height) // 2 
        else:
            trans_y = self.settings.screen.position.translate_y
        self.window.geometry("{}x{}+{}+{}".format(width, height, trans_x, trans_y))
        # self.deiconify()

