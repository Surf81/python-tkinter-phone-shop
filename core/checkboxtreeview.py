import tkinter as tk
from tkinter import ttk
from typing import Any

from core.settings import STATIC_ROOT


# Данный класс повзаимствован
# https://stackoverflow.com/questions/5104330/how-to-create-a-tree-view-with-checkboxes-in-python
class CheckboxTreeview(ttk.Treeview):
    """
    Treeview widget with checkboxes left of each item.
    The checkboxes are done via the image attribute of the item, so to keep
    the checkbox, you cannot add an image to the item.
    """

    def __init__(self, master=None, **kw):
        ttk.Treeview.__init__(self, master, **kw)
        # checkboxes are implemented with pictures
        self.im_checked = tk.PhotoImage(file=STATIC_ROOT / "img/checked.png")
        self.im_unchecked = tk.PhotoImage(file=STATIC_ROOT / "img/unchecked.png")
        self.im_tristate = tk.PhotoImage(file=STATIC_ROOT / "img/tristate.png")
        self.tag_configure("unchecked", image=self.im_unchecked)
        self.tag_configure("tristate", image=self.im_tristate)
        self.tag_configure("checked", image=self.im_checked)
        # check / uncheck boxes on click
        self.bind("<Button-1>", self.box_click, True)

    def insert(self, parent, index, iid=None, **kw):
        """same method as for standard treeview but add the tag 'unchecked'
        automatically if no tag among ('checked', 'unchecked', 'tristate')
        is given"""
        if not "tags" in kw:
            kw["tags"] = ("unchecked",)
        elif not (
            "unchecked" in kw["tags"]
            or "checked" in kw["tags"]
            or "tristate" in kw["tags"]
        ):
            kw["tags"] = ("unchecked",)
        ttk.Treeview.insert(self, parent, index, iid, **kw)

    def check_descendant(self, item):
        """check the boxes of item's descendants"""
        children = self.get_children(item)
        for iid in children:
            self.item(iid, tags=("checked",))
            self.check_descendant(iid)

    def check_ancestor(self, item):
        """check the box of item and change the state of the boxes of item's
        ancestors accordingly"""
        self.item(item, tags=("checked",))
        parent = self.parent(item)
        if parent:
            children = self.get_children(parent)
            b = ["checked" in self.item(c, "tags") for c in children]
            if False in b:
                # at least one box is not checked and item's box is checked
                self.tristate_parent(parent)
            else:
                # all boxes of the children are checked
                self.check_ancestor(parent)

    def tristate_parent(self, item):
        """put the box of item in tristate and change the state of the boxes of
        item's ancestors accordingly"""
        self.item(item, tags=("tristate",))
        parent = self.parent(item)
        if parent:
            self.tristate_parent(parent)

    def uncheck_descendant(self, item):
        """uncheck the boxes of item's descendant"""
        children = self.get_children(item)
        for iid in children:
            self.item(iid, tags=("unchecked",))
            self.uncheck_descendant(iid)

    def uncheck_ancestor(self, item):
        """uncheck the box of item and change the state of the boxes of item's
        ancestors accordingly"""
        self.item(item, tags=("unchecked",))
        parent = self.parent(item)
        if parent:
            children = self.get_children(parent)
            b = ["unchecked" in self.item(c, "tags") for c in children]
            if False in b:
                # at least one box is checked and item's box is unchecked
                self.tristate_parent(parent)
            else:
                # no box is checked
                self.uncheck_ancestor(parent)

    def box_click(self, event):
        """check or uncheck box when clicked"""
        x, y, widget = event.x, event.y, event.widget
        elem = widget.identify("element", x, y)
        if "image" in elem:
            # a box was clicked
            item = self.identify_row(y)
            tags = self.item(item, "tags")
            if ("unchecked" in tags) or ("tristate" in tags):
                self.check_ancestor(item)
                self.check_descendant(item)
            else:
                self.uncheck_descendant(item)
                self.uncheck_ancestor(item)


class MyCheckboxTreeview(CheckboxTreeview):
    """Класс расширяет возможности CheckboxTreeview путем
    объединения визуальной составляющей объекта
    с объектом данных, хранящим текущее состояние полей
    """

    def __init__(self, browser, content, *args, **kwargs):
        super().__init__(browser, *args, **kwargs)
        self.content = None
        self.refresh(content)

    def refresh(self, content: dict) -> None:
        """Обновление объекта данных и обновление дерева
        Args:
            content (dict):
        """
        self.content = content
        self.__build_elements_by_content()

    def __build_elements_by_content(self) -> None:
        """Загрузка Формирование дерева данных"""
        for item in self.get_children():
            self.delete(item)

        for charact, item in self.content.items():
            self.insert(
                "",
                tk.END,
                charact,
                text=item["description"],
                tags=("checked" if item["checked"] else "unchecked",),
            )
            for value, value_item in item["values"].items():
                self.insert(
                    charact,
                    tk.END,
                    value,
                    text=value_item["description"],
                    tags=("checked" if value_item["checked"] else "unchecked",),
                )

    def get_content(self) -> dict:
        """Возвращает информационный объект, соответствующий текущему состоянию дерева
        Returns:
            dict:
        """
        return self.content

    def __change_content(self, content: dict, iid: Any, flag: bool) -> None:
        """Рекурсивный метод поиск необходимого элемента дерева и присвоения ему нового значения
        Args:
            content (dict): справочник, в котором осуществляется поиск
            iid (_type_): искомый ключ справочника, совпадающий с iid элемента дерева
            flag (bool): yj==новое значение
        """
        for key, item in content.items():
            if key == iid:
                item["checked"] = flag
            values = item.get("values")
            if values:
                self.__change_content(values, iid, flag)

    # Переопределение поведения родительского класса
    def check_ancestor(self, item) -> None:
        self.__change_content(self.content, item, True)
        super().check_ancestor(item)

    def check_descendant(self, item) -> None:
        children = self.get_children(item)
        for iid in children:
            self.__change_content(self.content, iid, True)
        super().check_descendant(item)

    def uncheck_descendant(self, item) -> None:
        children = self.get_children(item)
        for iid in children:
            self.__change_content(self.content, iid, False)
        super().uncheck_descendant(item)

    def uncheck_ancestor(self, item) -> None:
        self.__change_content(self.content, item, False)
        super().uncheck_ancestor(item)

    def tristate_parent(self, item) -> None:
        self.__change_content(self.content, item, True)
        super().tristate_parent(item)
