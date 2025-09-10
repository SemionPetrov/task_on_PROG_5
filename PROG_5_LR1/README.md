## Лабораторная работа 1. Реализация удалённого импорта
1. ### Цель работы
    Реализовать механизм удалённого импорта модулей в Python с использованием пользовательских загрузчиков (importlib.abc, importlib.util). Продемонстрировать возможность импорта модуля по HTTP-ссылке, размещённого на локальном или удалённом сервере.
2. ### Подготовка окружения
    1. #### Структура проекта
           PythonProject/
           ├── activation_script.py
           ├── rootserver/
           │   └── myremotemodule.py
    3. #### Код модуля myremotemodule.py:
       
           def myfoo():
               author = "Semion Petrov"
               print(f"{author}'s module is imported")

4. ### Запуск HTTP-сервера
    1. #### Команда запуска
       
           cd rootserver
           python3 -m http.server 8000
    Ожидаемый результат:
    
        • Сервер запущен на http://localhost:8000
        • В браузере по адресу http://localhost:8000 виден файл myremotemodule.py

5. ### Реализация механизма удалённого импорта
    1. #### Содержимое activation_script.py:
      
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
                    raise ImportError("Ошибка подключения")
            
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
                        raise ImportError(f"Ошибка: {e}")
            
            sys.path_hooks.append(url_hook)
            print("URL-хук добавлен в sys.path_hooks")

6. ### Активация механизма и тест импорта
    1. #### Запуск скрипта
              python3 -i activation_script.py
    3. #### Добавление URL в sys.path
              sys.path.append("http://localhost:8000")
    4. Импорт и вызов функции
       
           import myremotemodule
           myremotemodule.myfoo()
7. ### Вывод
   На данном этапе реализован механизм удалённого импорта модулей через HTTP. Удалось успешно импортировать модуль myremotemodule.py, размещённый на локальном HTTP-сервере, с использованием кастомных url_hook, URLFinder и URLLoader. Механизм корректно перехватывает попытку импорта и загружает модуль по сети.
   

