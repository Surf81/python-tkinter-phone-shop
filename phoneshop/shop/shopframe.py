import tkinter as tk
from tkinter import ttk

from phoneshop.db.db import DB


class PhoneItem(tk.Frame):
    def __init__(self, browser, content: dict, *args, **kwargs):
        super().__init__(browser, *args,
                         bd=4, 
                         relief=tk.GROOVE, 
                         **kwargs)
        self.content = content
        self.field = dict()


        self.__create_form()
    
    def __create_form(self):

        self.field["nomination"] = ttk.Label(self, text=self.content["nomination"], font="Arial 12 bold")
        self.field["price"] = ttk.Label(self, text=self.content["price"], font="Arial 12 bold")

        ttk.Label(self, text="Название:", font="Arial 12 bold").grid(row=0, column=0, padx=[10, 5], pady=[10, 0], sticky="W")
        self.field["nomination"].grid(row=0, column=1, padx=[5, 10], pady=[10, 0], sticky="W")

        row = 1
        for item, (descr, value) in self.content["components"].items():
            self.field[item] = ttk.Label(self, text=value, font="Arial 12")
            ttk.Label(self, text=descr, font='Arial 12 normal').grid(row=row, column=0, padx=[10, 5], sticky="W")
            self.field[item].grid(row=row, column=1, padx=[5, 10], sticky="W")
            row += 1

        ttk.Label(self, text="Цена:", font='Arial 12 bold').grid(row=row, column=0, padx=[10, 5], pady=[0, 10], sticky="W")
        self.field["price"].grid(row=row, column=1, padx=[5, 10], pady=[0, 10], sticky="W")



class TopBar(tk.Frame):
    def __init__(self, browser, *args, **kwargs):
        super().__init__(browser, *args, **kwargs)
        self.__create_form()
    
    def __create_form(self):
        tk.Grid.columnconfigure(self, 0, weight=1)

        ttk.Label(self, text="Корзина", font="Arial 15 bold").grid(row=0, column=0, padx=5, pady=5, sticky="E")
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=1, column=0, pady=[20, 0], sticky="WE")


class SideBar(tk.Frame):
    def __init__(self, browser, *args, **kwargs):
        super().__init__(browser, *args, **kwargs)
        self.__create_form()
    
    def __create_form(self):
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.rowconfigure(self, 0, weight=1)

        frame1 = tk.Frame(self)
        frame1.grid(row=0, column=0, sticky='NS')
        frame2 = tk.Frame(self)
        frame2.grid(row=0, column=1, sticky='NS')

        # tk.Grid.columnconfigure(frame1, 0, weight=1)
        # tk.Grid.rowconfigure(frame1, 0, weight=1)
        tk.Grid.columnconfigure(frame2, 0, weight=1)
        tk.Grid.rowconfigure(frame2, 0, weight=1)

        ttk.Label(frame1, text="Фильтры", font="Arial 15 bold").grid(row=0, column=0, padx=5, pady=5)
        ttk.Separator(frame2, orient=tk.VERTICAL).grid(row=0, column=1, sticky='NS', padx=[10, 0])


class MainFrame(tk.Frame):
    def __init__(self, browser, content, *args, **kwargs):
        super().__init__(browser, *args, **kwargs)
        self.content = content

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.frame = tk.Frame(self.canvas, background="#ffffff")
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw",
                                  tags="self.frame")
        self.frame.bind("<Configure>", self.onFrameConfigure)

        self.__create_form()
    
    def __create_form(self):
        tk.Grid.columnconfigure(self.frame, 0, weight=1, minsize=400)

        row = 0
        for _, item in self.content.items():
            PhoneItem(self.frame, item).grid(row=row, column=0, sticky="WE", padx=20)
            row += 1

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))



class ShopFrame(tk.Frame):
    def __init__(self, browser, database: DB, *args, **kwargs):
        super().__init__(browser, *args,
                         bd=4, 
                         relief=tk.GROOVE, 
                         **kwargs)
        self.db = database
        self.content = dict()
        self.refresh_content()

        self.__create_form()


    def refresh_content(self):
        self.content = self.db.load_content()


    def __create_form(self):
        tk.Grid.columnconfigure(self, 0, weight=1, minsize=200)
        tk.Grid.columnconfigure(self, 1, weight=15)
        tk.Grid.rowconfigure(self, 1, weight=1)

        TopBar(self).grid(row=0, column=0, columnspan=2, sticky="WE")
        SideBar(self).grid(row=1, column=0, sticky="WENS")
        MainFrame(self, self.content).grid(row=1, column=1, sticky="WENS")




    def run(self):
        self.grid(sticky="WENS")
