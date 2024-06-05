from datetime import datetime
from typing import Union
import re
from src.user_format_handlers.date_formats import MONTH_NAMES, USER_SEASON_FORMAT_OPTIONS
from logging import getLogger

logger = getLogger(__name__)


class DateParser:
    @staticmethod
    def parse(elem: str) -> str | None:
        """
        Парсит дату из строки, используя регулярные выражения для различных форматов.

        Args:
            elem (str): Имя файла, содержащее дату.

        Returns:
            Union[datetime, None]: Объект datetime, представляющий дату, или None, если дата не найдена или не распарсена.
        """

        return USER_SEASON_FORMAT_OPTIONS.get(elem)

    @staticmethod
    def get_folder_date(date_format: str, date_regex_pattern, elem: str) -> datetime | None:
        """
        Извлекает дату из строки на основе заданного формата даты или названия месяца.

        Параметры:
        - date_format (str): Формат даты для извлечения. Если это "%B", метод будет искать название месяца в элементе.
        - date_regex_pattern (str): Шаблон регулярного выражения для извлечения даты.
        - elem (str): Строка, из которой нужно извлечь дату.

        Возвращает:
        - datetime | None: Извлеченная дата в виде объекта datetime при успешном выполнении или None в случае неудачи.

        Детали:
        - Если date_format равно "%B", метод будет искать название месяца на русском языке в элементе, конвертировать его в номер месяца
          и создавать объект datetime, представляющий первый день этого месяца.
        - Если date_format не равно "%B", метод будет использовать предоставленный шаблон регулярного выражения для поиска строки с датой
          в элементе и попытается преобразовать её в объект datetime, используя указанный формат даты.
        - Если парсинг не удаётся или название месяца не найдено в MONTH_NAMES, метод возвращает None.
        """
        if date_format == "%B":
            # Используем регулярное выражение для извлечения названия месяца
            match = re.search(r'\b([А-Яа-я]+)\b', elem)
            if match:
                month_name = match.group(1)
                month_number = MONTH_NAMES.get(month_name, False)
                if month_number:
                    current_year = datetime.now().year
                    return datetime(current_year, month_number, 1)
        else:
            match = re.search(date_regex_pattern, elem)
            if match:
                matched_date_str = match.group()
                try:
                    return datetime.strptime(matched_date_str, date_format)
                except ValueError as e:
                    logger.error("Ошибка: %s", e)
                    return None
