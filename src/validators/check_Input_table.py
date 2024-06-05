import re
from typing import List, Dict, Tuple
from abc import ABC, abstractmethod
from src.user_format_handlers.date_formats import USER_DATE_FORMAT_TO_RE_COMPILE
from logging import getLogger

logger = getLogger(__name__)


class Validator(ABC):
    """ Абстрактный базовый класс для всех валидаторов. """

    @abstractmethod
    def validate(self, value: str) -> bool:
        """
        Метод для валидации значения.

        :param value: Значение для валидации.
        :return: True, если значение валидно, иначе False.
        """
        pass


class FolderPathValidator(Validator):
    """Валидатор для проверки пути к папке."""

    def validate(self, value: str) -> bool:
        regex_pattern_path_1 = r"[A-Za-z]:\\(?:[^\\/:*?'<>|\r\n]+\\)*[^\\/:*?'<>|\r\n]*"
        regex_pattern_path_2 = r"\\\\[A-Za-z0-9._-]+\\(?:[^\\/:*?'<>|\r\n]+\\)*[^\\/:*?'<>|\r\n]*"
        try:
            path_pattern_1 = re.compile(regex_pattern_path_1)
            path_pattern_2 = re.compile(regex_pattern_path_2)
            return bool(path_pattern_1.match(value) or path_pattern_2.match(value))
        except Exception as e:
            logger.error("Ошибка при проверки валидации пути к папке %s", e)
            return False


class UserFormatMaskValidator(Validator):
    """ Валидатор для проверки маски формата пользователя. """

    def validate(self, value: str) -> bool:
        try:
            if "*" in value:
                pattern = re.compile(r'^\*$|^\*\.[a-zA-Z0-9]+$')
                # Проверка, соответствует ли значение шаблону
                if pattern.match(value):
                    return True

            if "{" in value and "}" in value and len(value) > 2:
                match = re.search(r'{(.*?)}', value)
                if match:
                    # Проверка, существует ли шаблон в словаре USER_DATE_FORMAT_TO_RE_COMPILE
                    return bool(USER_DATE_FORMAT_TO_RE_COMPILE.get(match.group(1), False))
            return bool(USER_DATE_FORMAT_TO_RE_COMPILE.get(value, False))
        except Exception as e:
            logger.error("Ошибка при проверки валидации маски имени %s", e)
            return False


class IntervalValidator(Validator):
    """ Валидатор для проверки интервала. """

    def validate(self, value: str) -> bool:
        try:
            offset, period = value.split()
            return offset.isdigit() and period[0].lower() in "гмд"
        except Exception as e:
            logger.error("Ошибка при проверки валидации интервала %s", e)
            return False


class DateModificationValidator(Validator):
    """ Валидатор для проверки источника даты папки/файла. """

    def validate(self, value: str) -> bool:
        try:
            return value.lower().strip() in ["дата создания", "дата изменения", "дата из имени"]
        except Exception as e:
            logger.error("Ошибка при проверки валидации источника даты папки/файла %s", e)
            return False


class ActiveValidator(Validator):
    """ Валидатор для проверки статуса активности. """

    def validate(self, value: str) -> bool:
        try:
            return value.lower().strip() in ["активен", "не активен"]
        except Exception as e:
            logger.error("Ошибка при проверки валидации активности файла %s", e)
            return False


class CheckNonEmptyString(Validator):
    """Простая проверка не пустых строк"""

    def validate(self, value: str) -> bool:
        return bool(value)


class CheckInputTable:
    """ Класс для проверки валидации строк таблицы. """

    def __init__(self, table_rows: List[Tuple[str, str, str, str, str, str, str, str]]):
        """
        Инициализирует объект CheckInputTable.

        :param table_rows: Список строк таблицы, каждая строка - кортеж из 8 элементов.
        """
        self.table_rows = table_rows

    def check_validation(self) -> Dict[int, List[int]]:
        """
        Проверяет каждую строку таблицы на соответствие правилам валидации.

        :return: Словарь, где ключи - номера строк (начиная с 2), а значения - списки номеров колонок с ошибками.
        """
        problematic_rows = {}

        for row_number, row in enumerate(self.table_rows, start=2):
            if row[4] == "*" and row[6].lower() == "дата из имени":
                problematic_rows.setdefault(row_number, []).extend([5, 7])
            validators_and_values = {
                1: (CheckNonEmptyString(), row[0]),
                2: (CheckNonEmptyString(), row[1]),
                3: (CheckNonEmptyString(), row[2]),
                4: (FolderPathValidator(), row[3]),
                5: (UserFormatMaskValidator(), row[4]),
                6: (IntervalValidator(), row[5]),
                7: (DateModificationValidator(), row[6]),
                8: (ActiveValidator(), row[7])
            }

            for column_number, (validator, value) in validators_and_values.items():
                if not validator.validate(value):
                    problematic_rows.setdefault(row_number, []).append(column_number)
        logger.debug("Проверка таблицы. Проблемные ячейки: %s", problematic_rows)
        return problematic_rows
