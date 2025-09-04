import sys
import re
from urllib.request import urlopen
from importlib.abc import PathEntryFinder
from importlib.util import spec_from_loader


class URLFinder(PathEntryFinder):
    def __init__(self, url, available):
        self.url = url
        self.available = available

    def find_spec(self, name, target=None):
        if name in self.available:
            origin = f"{self.url}/{name}.py"
            loader = URLLoader()
            return spec_from_loader(name, loader, origin=origin)
        return None


def url_hook(some_str):
    if not some_str.startswith(("http://", "https://")):
        raise ImportError("Не URL")

    try:
        with urlopen(some_str) as page:
            data = page.read().decode("utf-8")
        filenames = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*\.py", data)
        modnames = {name[:-3] for name in filenames}
        return URLFinder(some_str, modnames)
    except Exception:
        raise ImportError("Не удалось подключиться к URL")


class URLLoader:
    def create_module(self, target):
        return None
    def exec_module(self, module):
        try:
            with urlopen(module.__spec__.origin) as page:
                source = page.read()
            code = compile(source, module.__spec__.origin, mode="exec")
            exec(code, module.__dict__)
        except Exception as e:
            raise ImportError(f"Ошибка при выполнении модуля: {e}")



sys.path_hooks.append(url_hook)
print("URL-хук добавлен в sys.path_hooks")