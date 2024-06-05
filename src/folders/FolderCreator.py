import os
import datetime
from logging import getLogger

logger = getLogger(__name__)


class DateProvider:
    """
    Предоставляет текущую информацию о дате, такую как год и месяц на русском языке.

    Атрибуты:
        MONTH_NAMES (dict): Сопоставление номеров месяцев с их русскими названиями.
        current_time (datetime.datetime): Текущая дата и время, используемые для определения года и месяца.
    """

    MONTH_NAMES = {
        1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
        5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
        9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
    }

    def __init__(self, current_time=None | datetime.datetime):
        self.current_time = current_time or datetime.datetime.now()

    @property
    def current_year(self):
        return str(self.current_time.year)

    @property
    def current_month(self):
        return self.MONTH_NAMES.get(self.current_time.month)


class FolderCreator:
    """
    Создает папки, если они не существуют.
    """

    @staticmethod
    def create_folder(path: str) -> None:
        """
        Создает папку по указанному пути, если она не существует.

        Параметры:
            path (str): Путь к папке, которую нужно создать.
        """
        if not os.path.exists(path):
            os.makedirs(path)
            logger.info("Создана новая папка: %s", path)


class PathProvider:
    """
    Предоставляет пути к папкам на основе базового пути и текущей даты.

    Атрибуты:
        base_path (str): Базовый путь, к которому добавляются год и месяц.
        date_provider (DateProvider): Экземпляр DateProvider для получения текущей даты.
    """

    def __init__(self, base_path: str, date_provider: DateProvider):
        self.base_path = base_path
        self.date_provider = date_provider

    def get_year_path(self) -> str:
        return os.path.join(self.base_path, self.date_provider.current_year)

    def get_month_path(self) -> str:
        return os.path.join(self.get_year_path(), self.date_provider.current_month)
