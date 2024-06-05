from abc import ABC, abstractmethod
from typing import Union
from src.user_format_handlers.DateParser import DateParser
from src.folders.FolderTimes import FolderCreationTime
import os
import datetime


@abstractmethod
class DateSource(ABC):
    """
    Абстрактный базовый класс для определения источника даты из пути.

    Параметры:
    - path (str): Путь к файлу или папке.
    """

    def __init__(self, path: str):
        self.path = path

    @abstractmethod
    def get_folder_date(self, datetime_date_format, re_compile_date_format):
        pass


class DateFromName(DateSource):
    """
    Класс для извлечения даты из имени файла или папки.
    """

    def get_folder_date(self, datetime_date_format, re_compile_date_format):
        """
        Извлекает дату из имени файла или папки.

        Параметры:
        - datetime_date_format: Формат даты для datetime.
        - re_compile_date_format: Компилированный формат даты для регулярного выражения.

        Возвращает:
        - Union[datetime.datetime, None]: Дата в формате datetime.datetime или None.
        """
        file_name = os.path.basename(self.path)
        date_parser = DateParser()
        return date_parser.get_folder_date(datetime_date_format, re_compile_date_format, file_name)


class DateCreation(DateSource):
    """
    Класс для получения времени создания папки.
    """

    def get_folder_date(self, _datetime_date_format, _re_compile_date_format) -> Union[datetime.datetime, None]:
        """
        Получает время создания папки, используя метод из FolderCreationTime.

        Returns:
            Union[datetime.datetime, None]: Время создания в формате datetime.datetime
            или None, если время создания не может быть определено.
        """
        folder_creation_time = FolderCreationTime(self.path)
        return folder_creation_time.get_creation_time()


class DateChange(DateSource):
    """
    Класс для получения времени последней модификации папки.
    """

    def get_folder_date(self, _datetime_date_format, _re_compile_date_format):
        """
        Получает время последней модификации папки, используя метод из FolderCreationTime.

        Returns:
            Union[datetime.datetime, None]: Время модификации в формате datetime.datetime
            или None, если время модификации не может быть определено.
        """
        folder_creation_time = FolderCreationTime(self.path)
        return folder_creation_time.get_modification_time()
