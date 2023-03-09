from typing import Any

class DotDict(dict):
    """Расширение класса dict позволяет обращаться
        к ключам через точку
    """
    def __getattr__(self, name: str) -> Any:
        if (elem := self.get(name, None)):
            return elem
        else:
            return self.setdefault(name, self.__class__)
    
    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value
