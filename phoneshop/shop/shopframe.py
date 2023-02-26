import tkinter as tk
from tkinter import ttk


class PhoneItem(tk.Frame):
    def __init__(self, browser, *args, **kwargs):
        super().__init__(browser, *args,
                         bd=4, 
                         relief=tk.GROOVE, 
                         **kwargs)
        self.__create_form()
    
    def __create_form(self):
        ttk.Label(self, text="Название:", font="Arial 12 bold").grid(row=0, column=0, padx=[10, 5], pady=[10, 0], sticky="W")
        ttk.Label(self, text="ОЗУ:", font='Arial 12 normal').grid(row=1, column=0, padx=[10, 5], sticky="W")
        ttk.Label(self, text="Хранилище:", font='Arial 12 normal').grid(row=2, column=0, padx=[10, 5], sticky="W")
        ttk.Label(self, text="Процессор:", font='Arial 12 normal').grid(row=3, column=0, padx=[10, 5], sticky="W")
        ttk.Label(self, text="Цена:", font='Arial 12 bold').grid(row=4, column=0, padx=[10, 5], pady=[0, 10], sticky="W")

        title = ttk.Label(self, text="IPhone 13", font="Arial 12 bold")
        ram = ttk.Label(self, text="8 Gb", font="Arial 12 normal")
        storage = ttk.Label(self, text="128 Gb", font="Arial 12 normal")
        proc = ttk.Label(self, text="Coalcome", font="Arial 12 normal")
        price = ttk.Label(self, text="25000", font="Arial 12 bold")

        title.grid(row=0, column=1, padx=[5, 10], pady=[10, 0], sticky="W")
        ram.grid(row=1, column=1, padx=[5, 10], sticky="W")
        storage.grid(row=2, column=1, padx=[5, 10], sticky="W")
        proc.grid(row=3, column=1, padx=[5, 10], sticky="W")
        price.grid(row=4, column=1, padx=[5, 10], pady=[0, 10], sticky="W")



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
    def __init__(self, browser, *args, **kwargs):
        super().__init__(browser, *args, **kwargs)

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
        for row in range(15):
            PhoneItem(self.frame).grid(row=row, column=0, sticky="WE", padx=20)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))



class ShopFrame(tk.Frame):
    def __init__(self, browser, *args, **kwargs):
        super().__init__(browser, *args,
                         bd=4, 
                         relief=tk.GROOVE, 
                         **kwargs)
        self.__create_form()
    
    def __create_form(self):
        tk.Grid.columnconfigure(self, 0, weight=1, minsize=200)
        tk.Grid.columnconfigure(self, 1, weight=15)
        tk.Grid.rowconfigure(self, 1, weight=1)

        TopBar(self).grid(row=0, column=0, columnspan=2, sticky="WE")
        SideBar(self).grid(row=1, column=0, sticky="WENS")
        MainFrame(self).grid(row=1, column=1, sticky="WENS")




    def run(self):
        self.grid(sticky="WENS")
