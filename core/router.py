from functools import wraps
from typing import *


class Router(object):
    """Регистрация команд приложений"""

    def __init__(self):
        self.routers = dict()
        self.history = None

    def __call__(self, label) -> Callable:
        if self.routers.get(label):
            return self.__call_function_control(label)

    def __call_function_control(self, label) -> Callable:
        """Оборачивает функцию в обертку, которая срабатывает при вызове этой функции
        для ведения истории вызовов (запоминания последней открытой страницы)
        """

        @wraps(self.routers[label].get("command"))
        def wrapper(*args, **kwargs):
            router = self.routers[label]
            if router["history"]:
                self.history = label
            return router["command"](*args, **kwargs)

        return wrapper

    def register_rout(
        self, label: str, command: Callable, history: bool = False
    ) -> None:
        """Регистрация команды в роутере
        Args:
            label (str): метка команды
            command (Callable): вызываемый объект
            history (bool, optional): Если True, команда будет регистрироваться при вызове
        """
        router = self.routers.setdefault(label, dict())
        router["command"] = command
        router["history"] = history

    def call_history(self):
        """Вызов последней команды из истории"""
        if self.history:
            self.__call__(self.history)()


class PageRunner(object):
    """Стартер для запуска приложений"""

    def __init__(self):
        self.page = None

    def set_page(self, page):
        self.page = page

    def launch(self, command: str) -> Callable:
        """Возвращает функцию, способную вызвать команду с указанным именем
        у обекта, который позднее будет указан с помощью set_page"""

        def launcher(*args, **kwargs):
            if self.page:
                func = getattr(self.page, command)
                return func(*args, **kwargs)

        return launcher
