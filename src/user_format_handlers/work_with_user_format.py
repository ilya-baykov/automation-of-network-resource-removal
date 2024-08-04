from typing import Optional, Tuple
from src.user_format_handlers.date_formats import USER_DATE_FORMAT_TO_RE_COMPILE
import re
from logging import getLogger

logger = getLogger(__name__)


class UserDateFormatDetector:
    """
    Определяет формат даты пользователя и компилирует его на основе заданного регулярного выражения.
    """

    @staticmethod
    def get_user_and_re_compile_date_format(regex_pattern: str) -> Tuple[Optional[str], Optional[re.Pattern]]:
        """
        Определяет шаблон даты пользователя и его скомпилированный вариант на основе переданного регулярного выражения.

        Args:
            regex_pattern (str): Регулярное выражение, используемое для поиска шаблона даты. Пример: 'Отчет_МП_*_{ДДММГГГГ}.xlsx'

        Returns:
            Tuple[Optional[str], Optional[re.Pattern]]: Кортеж, содержащий шаблон даты пользователя на русском и его скомпилированный вариант.
            Если совпадений не найдено, возвращает (None, None).
        """
        date_pattern_ru, date_pattern_re_compile = None, None
        for key, pattern in USER_DATE_FORMAT_TO_RE_COMPILE.items():
            if key in regex_pattern:
                date_pattern_ru, date_pattern_re_compile = key, pattern
                break
        logger.debug("Формат даты пользователя: %s", date_pattern_ru)
        logger.debug("Регулярное выражение для пользовательского формата: %s", date_pattern_re_compile)
        return date_pattern_ru, date_pattern_re_compile


class PatternReplacer:
    """
    Заменяет заполнители и формат даты на соответствующие регулярные выражения.
    """

    def __init__(self, user_date_format: str, re_date_format: re.Pattern, pattern: str):
        """
        Инициализая
        :param user_date_format: 'ДДММГГГГ'
        :param re_date_format: re.compile('(0[1-9]|[12]\\d|3[01])(0[1-9]|1[0-2])\\d{4}')
        :param pattern: 'Отчет_МП_*_{ДДММГГГГ}.xlsx')
        """
        self.user_date_format = user_date_format
        self.re_date_format = re_date_format
        self.regex_pattern = self.replace_pattern(pattern)
        logger.debug("Патерн с замененными заполнителями и форматом даты : %s", self.regex_pattern)

    def replace_pattern(self, pattern: str) -> str:
        """
        Заменяет символы-заполнители и формат даты на регулярные выражения.

        Args:
            pattern (str): Шаблон, определенный пользователем, с заполнителями.

        Returns:
            str: Шаблон с замененными заполнителями и форматом даты.
        """

        # Удаляем фигурные скобки
        pattern = pattern.replace("{", "").replace("}", "")

        # Экранируем все специальные символы в шаблоне
        pattern = re.escape(pattern)

        # Заменяем экранированную звёздочку на нужное выражение
        # pattern = pattern.replace(r'\*', '[^_]+') # прошлый вариант
        pattern = pattern.replace(r'\*', '.+')

        # Заменяем экранированный формат даты на нужное регулярное выражение
        if self.user_date_format and self.re_date_format.pattern:
            return pattern.replace(re.escape(self.user_date_format), self.re_date_format.pattern)
        else:
            return pattern


class FileNameValidator:
    """
    Проверяет правильность имен файлов на основе заданных пользователем шаблонов.
    """

    def __init__(self, pattern_replacer: PatternReplacer):
        """
        Инициализация
        :param pattern_replacer: Объект класса PatternReplacer
        """
        self.pattern_replacer = pattern_replacer

    def check_pattern(self, file_name: str) -> bool:
        """
        Проверяет правильность имени файла по шаблону.

        Args:
            file_name (str): Имя файла для проверки.
            pattern (str): Шаблон, определенный пользователем, с заполнителями.

        Returns:
            bool: True, если имя файла соответствует шаблону, False в противном случае.
        """
        regex_pattern = self.pattern_replacer.regex_pattern
        return bool(re.fullmatch(regex_pattern, file_name))
