from src.utils.StoragePeriodFunction import *
from src.utils.DateSource import *


def cls_definition(storage_period: str, date_source, datetime_date_format: str, re_compile_date_format) -> Union[
    None, StoragePeriodFunction]:
    """
    Возвращает класс, соответствующий указанному периоду хранения.

    Args:
        storage_period str: Интервал хранения (1 Год ), (2 Месяца ) и т.д
    Returns:
        Union[None, StoragePeriodFunction]: Класс, соответствующий периоду хранения, или None, если такого нет.
    """
    offset, period = storage_period.split()
    current_cls = {
        "г": CurrentYearWithOffset,  # Год
        "м": CurrentMonthWithOffset,  # Месяц
        "д": CurrentDayWithOffset  # День
    }.get(period[0].lower(), None)
    return current_cls(offset=int(offset), date_source=date_source,
                       datetime_date_format=datetime_date_format, re_compile_date_format=re_compile_date_format)


def selecting_date_source(date_modification: str):
    return {
        "дата создания": DateCreation,
        "дата изменения": DateChange,
        "дата из имени": DateFromName,

    }.get(date_modification.lower().strip(), None)
