import os
import platform
import datetime
from typing import Union


class FolderCreationTime:
    """Класс для получения времени создания и модификации папки."""

    def __init__(self, path: str) -> None:
        """
        Инициализирует объект FolderCreationTime.

        Args:
            path (str): Путь к папке.
        """
        self.path = path

    def get_creation_time(self) -> Union[datetime.datetime, None]:
        """
        Получает время создания папки.

        Returns:
            Union[datetime.datetime, None]: Время создания в формате datetime.datetime
            или None, если время создания не может быть определено.
        """
        if platform.system() == 'Windows':
            creation_time = os.path.getctime(self.path)
        else:
            stat = os.stat(self.path)
            try:
                creation_time = stat.st_birthtime
            except AttributeError:
                creation_time = stat.st_ctime
        print (self.path)
        print (datetime.datetime.fromtimestamp(creation_time))
        return datetime.datetime.fromtimestamp(creation_time)

    def get_modification_time(self) -> Union[datetime.datetime, None]:
        """
        Получает время последней модификации папки.

        Returns:
            Union[datetime.datetime, None]: Время модификации в формате datetime.datetime
            или None, если время модификации не может быть определено.
        """
        try:
            modification_time = os.path.getmtime(self.path)
            return datetime.datetime.fromtimestamp(modification_time)
        except FileNotFoundError:
            return None
