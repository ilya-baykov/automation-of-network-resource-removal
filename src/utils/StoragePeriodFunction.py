from logging import getLogger
from abc import ABC, abstractmethod
from dateutil.relativedelta import relativedelta
from typing import List, Union
import datetime

logger = getLogger(__name__)


class StoragePeriodFunction(ABC):
    """Абстрактный базовый класс для функций обработки периодов хранения."""

    def __init__(self, date_source, offset: int, datetime_date_format: str, re_compile_date_format):
        """
        Инициализирует экземпляр класса StoragePeriodFunction.

        Args:
            offset (int): Смещение периода.
            date_format (Union[int, str]): Формат даты, который будет использоваться для разбора даты.

        Raises:
            InvalidDate: Если указанный формат даты недопустим.
        """
        self.date_source = date_source
        self.offset = offset
        self.datetime_date_format = datetime_date_format
        self.re_compile_date_format = re_compile_date_format

    @abstractmethod
    def process(self, folder_contents: List[str], current_date: datetime):
        """
               Абстрактный метод обработки периода хранения.

               Args:
                   folder_contents (List[str]): Содержимое папки.
                   date_modification (bool): Флаг - Нужно ли смотреть на дату изменения
                   current_date (datetime): Текущая дата.


               Raises:
                   NotImplementedError: Если метод не реализован в подклассе.
               """
        pass


class CurrentMonthWithOffset(StoragePeriodFunction):
    """Класс для обработки периода текущего месяца с учетом смещения."""

    def process(self, folder_contents: List[str], current_date: datetime) -> List[str]:
        """ Обрабатывает папки на основе текущего месяца с учетом смещения. """
        result: List[str] = []
        for elem_path in folder_contents:
            try:
                folder_date = self.date_source(elem_path).get_folder_date(self.datetime_date_format,
                                                                          self.re_compile_date_format)
                time_delta = relativedelta(current_date, folder_date)
                months_difference = time_delta.years * 12 + time_delta.months
                logger.debug("Дата из папки/файла: %s", folder_date)
                logger.debug("Разница в месяцах: %s", months_difference)
                if months_difference >= self.offset: result.append(elem_path)
            except Exception as e:
                logger.error("Ошибка: %s", e)
        return result


class CurrentDayWithOffset(StoragePeriodFunction):
    """Класс для обработки периода текущего дня с учетом смещения."""

    def process(self, folder_contents: List[str], current_date: datetime) -> List[str]:
        """ Обрабатывает папки на основе текущего дня с учетом смещения."""
        result: List[str] = []
        for elem_path in folder_contents:
            try:
                folder_date = self.date_source(elem_path).get_folder_date(self.datetime_date_format,
                                                                          self.re_compile_date_format)
                logger.debug("Дата из папки/файла: %s", folder_date)
                logger.debug("Разница в днях: %s", (current_date - folder_date).days)
                if (current_date - folder_date).days >= self.offset:
                    result.append(elem_path)
            except Exception as e:
                logger.error("Ошибка : %s", e)
        return result


class CurrentYearWithOffset(StoragePeriodFunction):
    """Класс для обработки периода текущего года с учетом смещения."""

    def process(self, folder_contents: List[str], current_date: datetime) -> List[str]:
        """ Обрабатывает папки на основе текущего года с учетом смещения."""
        result: List[str] = []
        for elem_path in folder_contents:
            try:
                folder_date = self.date_source(elem_path).get_folder_date(self.datetime_date_format,
                                                                          self.re_compile_date_format)
                delete_after_date = folder_date.replace(year=folder_date.year + self.offset)

                logger.debug("Дата из папки/файла: %s", folder_date)
                logger.debug("Дата папки/файла + смещение: %s", delete_after_date)

                if current_date >= delete_after_date:
                    result.append(elem_path)

            except Exception as e:
                logger.error("Ошибка: %s", e)
        return result
