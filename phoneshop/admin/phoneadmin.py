import tkinter as tk
from tkinter import ttk

class CharactAdminFrame(object):
    def __init__(self, browser, database):
        self.master = browser
        self.db = database
        self.window = tk.Frame(self.master)
        self.__create_form()

    def __create_form(self):
        ttk.Label(self.window, text="проверка2").grid()

    def __clear_browser(self):
        for item in self.master.grid_slaves():
            item.grid_forget()

    def run(self):
        self.__clear_browser()
        self.window.grid(sticky="WENS")


class PhoneAdminFrame(object):
    def __init__(self, browser, database):
        self.master = browser
        self.db = database
        self.window = tk.Frame(self.master)
        self.__create_form()

    def __create_form(self):
        ttk.Label(self.window, text="проверка3").grid()

    def __clear_browser(self):
        for item in self.master.grid_slaves():
            item.grid_forget()

    def run(self):
        self.__clear_browser()
        self.window.grid(sticky="WENS")
