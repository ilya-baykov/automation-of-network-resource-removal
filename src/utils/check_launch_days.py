from enum import Enum
from typing import List
from datetime import datetime, timedelta

from src.utils.exceptions import IncorrectDate
from logging import getLogger

logger = getLogger(__name__)


class DatetimeFormats:
    WEEKDAYS = "%A"
    CALENDAR_DAYS = "%d.%m.%Y"


class WeekdaysFormats(Enum):
    пн = 0
    вт = 1
    ср = 2
    чт = 3
    пт = 4
    сб = 5
    вс = 6


class LaunchDayCheck:
    TODAY_DATE = datetime.today()

    def __init__(self, launch_days: str):
        """Инициализирует дни запуска из таблицы настроечного файла"""
        self.user_launch_days: List[str] = launch_days.strip().split(",")

    @classmethod
    def reformat_user_calendar_day(cls, day: str) -> datetime.date:
        """Преобразует день в формат datetime."""

        if len(day) == 2 and day.isdigit():  # ДД
            return datetime(year=cls.TODAY_DATE.year, month=cls.TODAY_DATE.month, day=int(day)).date()

        elif len(day) == 2 and day.isalpha():  # Пн,Вт,...Вс:
            day = next((week_day for week_day in WeekdaysFormats if day.lower() == week_day.name), None)
            return (cls.TODAY_DATE + timedelta(days=(int(day.value) - cls.TODAY_DATE.weekday()) % 7)).date()

        elif len(day) == 5 and day[2] == ".":  # ДД.ММ
            return datetime(year=cls.TODAY_DATE.year, month=int(day[4:6]), day=int(day[:2])).date()

        elif len(day) == 10 and day[2] == "." and day[5] == ".":  # ДД.ММ.ГГГГ
            return datetime.strptime(day, DatetimeFormats.CALENDAR_DAYS).date()
        else:
            raise IncorrectDate

    def verdict(self) -> bool:
        """Сравнивает пользовательские даты с сегодняшним днём"""
        for day in self.user_launch_days:
            try:
                if LaunchDayCheck.reformat_user_calendar_day(day) == LaunchDayCheck.TODAY_DATE.date():
                    return True
            except Exception as e:
                logger.error(f"Ошибка при работе со столбцом 'Интервалы запуска' {e}")
                return False
        return False
