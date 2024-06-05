from collections import namedtuple
from abc import ABC, abstractmethod
import os
from typing import List, Dict
from src.user_format_handlers.work_with_user_format import *
import shutil


class FolderContentLoader(ABC):
    """Абстрактный класс для загрузки содержимого."""

    def __init__(self, path: str, regex_pattern: str, user_date_format: str, re_compile_date_format: re.Pattern,
                 is_file: bool) -> None:
        """ Инициализатор

         :param
         regex_pattern (str) : Формат названия папок/файлов из таблицы пользователя. ('Отчет_МП_*_{ДДММГГГГ}.xlsx')
         user_date_format(str): Формат даты пользователя. (ДДММГГГГ)
         re_compile_date_format(re.Pattern): Регулярное выражение для поиска даты. (re.compile('(0[1-9]|[12]\\d|3[01])(0[1-9]|1[0-2])\\d{4}'))
         is_file (bool): True-Файл,False-Папка
         """
        self.path = path
        self.regex_pattern = regex_pattern
        self.user_date_format = user_date_format
        self.re_compile_date_format = re_compile_date_format
        self.is_file = is_file

    @abstractmethod
    def load_contents(self) -> List[str]:
        """

        :return: Список путей файлов/папок, которые подходят под пользовательский формат
        """
        pass


class RecursiveFolderContentLoader(FolderContentLoader):
    """Класс для рекурсивной загрузки содержимого папки с подпапками. Файлы и папки по формату"""

    def load_contents(self) -> List[str]:
        contents = []
        pattern_replacer = PatternReplacer(self.user_date_format, self.re_compile_date_format, self.regex_pattern)
        validator = FileNameValidator(pattern_replacer)
        for root, dirs, files in os.walk(self.path):
            if self.is_file:
                contents.extend([os.path.join(root, _file) for _file in files if
                                 validator.check_pattern(_file)])
            else:
                contents.extend([os.path.join(root, _dir) for _dir in dirs if
                                 validator.check_pattern(_dir)])
        logger.debug("Полученные папки и файлы, подходящие под формат: %s", contents)
        return contents


# Определение именованного кортежа
CleanResult = namedtuple('CleanResult', ['status', 'comment'])


class FolderCleaner:
    """Класс для очистки папки от указанных файлов."""

    def clean(self, items_to_delete: List[str]) -> Dict[str, CleanResult]:
        """
        Удаляет указанные файлы и папки.

        :param items_to_delete: Список путей к файлам/папкам, которые нужно удалить.
        :return: Словарь, где ключи - пути к файлам/папкам, значения - CleanResult, содержащие статус и комментарий.
        """
        report_dict = {}

        if not items_to_delete:
            # Если список пуст, возвращаем пустой отчёт
            report_dict = {
                "Нет файлов на удаление": CleanResult(status="Выполнено", comment="Список файлов на удаление пуст")}
            return report_dict

        for path in items_to_delete:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    report_dict[path] = CleanResult(status="Выполнено", comment="Файл удалён")
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    report_dict[path] = CleanResult(status="Выполнено", comment="Папка удалена")
                else:
                    report_dict[path] = CleanResult(status="Не выполнено", comment="Неизвестный тип или не существует")
            except FileNotFoundError:
                report_dict[path] = CleanResult(status="Не выполнено", comment="Файл или папка не найдены")
            except PermissionError:
                report_dict[path] = CleanResult(status="Не выполнено", comment="Недостаточно прав доступа")
            except OSError as e:
                if 'being used by another process' in str(e):
                    report_dict[path] = CleanResult(status="Не выполнено",
                                                    comment="Файл или папка используются другим процессом")
                elif 'path too long' in str(e).lower():
                    report_dict[path] = CleanResult(status="Не выполнено", comment="Слишком длинный путь")
                else:
                    report_dict[path] = CleanResult(status="Не выполнено", comment=f"Ошибка OSError: {e}")
            except ValueError as e:
                report_dict[path] = CleanResult(status="Не выполнено", comment=f"Ошибка скрипта: ValueError: {e}")
            except TypeError as e:
                report_dict[path] = CleanResult(status="Не выполнено", comment=f"Ошибка скрипта: TypeError: {e}")
            except Exception as e:
                report_dict[path] = CleanResult(status="Не выполнено",
                                                comment=f"Ошибка скрипта: Неизвестная ошибка: {e}")

        return report_dict


class Folder:
    """Класс, представляющий папку на файловой системе."""

    def __init__(self, path: str, content_loader: RecursiveFolderContentLoader, cleaner: FolderCleaner) -> None:
        """
        Инициализатор
        :param path: Путь к корневой папке ( из таблицы пользователя ).
        :param content_loader: Класс, который будет выполнять поиск вложенных элементов.
        :param cleaner: Класс, который будет очищать список путей.
        """
        self.path = path
        self.content_loader = content_loader
        self.cleaner = cleaner
        self.deleted_files: List[str] = []

    def load_contents(self):
        """Получает список путей файлов/папок, которые подходят под пользовательскую маску"""
        return self.content_loader.load_contents()

    def add_files_to_delete(self, files: List[str]) -> None:
        """Добавляет список путей к файлам/папкам на удаление в общий список"""
        self.deleted_files.extend(files)

    def clean(self) -> Dict[str, CleanResult]:
        """Удаляет все элементы из списка на удаление"""
        clean_status = self.cleaner.clean(self.deleted_files)
        self.deleted_files = []
        return clean_status

    def __str__(self) -> str:
        return f"{self.path}"
