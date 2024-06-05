from src.utils.StoragePeriodFunction import *
from src.utils.DateSource import *
from src.user_format_handlers.date_formats import DATE_FORMATS
import pytest
from datetime import datetime


@pytest.mark.parametrize(
    "folder_contents, offset,current_date, date_source,datetime_date_format, verdict",
    [
        (["2023-05-11", "2023-06-11", "2024-03-01", "2024-04-12", "2024-05-12", "2023-05-12", "2024-03-27",
          "2024-03-28"],
         0, datetime(2024, 5, 27), DateFromName, "%Y-%m-%d",
         ["2023-05-11", "2023-06-11", "2024-03-01", "2024-04-12", "2024-05-12", "2023-05-12", "2024-03-27",
          "2024-03-28"]),

        (["2023-05-12", "2023-12-31", "2024-03-28", "2024-04-26", "2024-04-27", "2024-04-28", "2024-05-26",
          "2024-05-30", "2024-05-27"],
         1, datetime(2024, 5, 27), DateFromName, "%Y-%m-%d",
         ["2023-05-12", "2023-12-31", "2024-03-28", "2024-04-26", "2024-04-27", "2024-04-28", "2024-05-26", ]),

        (["2023-05-12", "2023-12-31", "2024-03-28", "2024-04-26", "2024-04-27", "2024-04-28", "2024-05-25",
          "2024-05-30", "2024-05-26"],
         2, datetime(2024, 5, 27), DateFromName, "%Y-%m-%d",
         ["2023-05-12", "2023-12-31", "2024-03-28", "2024-04-26", "2024-04-27", "2024-04-28", "2024-05-25"])

    ]

)
def test_current_day_with_offset(folder_contents, offset, current_date, date_source, datetime_date_format, verdict):
    result: List[str] = []
    re_compile_date_format = DATE_FORMATS.get(datetime_date_format)
    for elem_path in folder_contents:
        folder_date = date_source(elem_path).get_folder_date(datetime_date_format, re_compile_date_format)
        if (current_date - folder_date).days >= offset:
            result.append(elem_path)
    assert verdict == result


@pytest.mark.parametrize(
    "folder_contents, offset,current_date, date_source,datetime_date_format, verdict",
    [
        (["2023-05-12", "2023-12-31", "2024-03-28", "2024-04-26", "2024-04-27", "2024-04-28", "2024-05-20",
          "2024-05-30"],
         0, datetime(2024, 5, 27), DateFromName, "%Y-%m-%d",
         ["2023-05-12", "2023-12-31", "2024-03-28", "2024-04-26", "2024-04-27", "2024-04-28", "2024-05-20",
          "2024-05-30"]),

        (["2023-05-12", "2023-12-31", "2024-03-28", "2024-04-26", "2024-04-27", "2024-04-28", "2024-05-20",
          "2024-05-30"],
         1, datetime(2024, 5, 27), DateFromName, "%Y-%m-%d",
         ["2023-05-12", "2023-12-31", "2024-03-28", "2024-04-26", "2024-04-27"]),

        (["2023-05-11", "2023-06-11", "2024-03-01", "2024-04-12", "2024-05-12", "2023-05-12", "2024-03-27",
          "2024-03-28"],
         2, datetime(2024, 5, 27), DateFromName, "%Y-%m-%d",
         ["2023-05-11", "2023-06-11", "2024-03-01", "2023-05-12", "2024-03-27"]),

    ]

)
def test_current_month_with_offset(folder_contents, offset, current_date, date_source, datetime_date_format, verdict):
    result: List[str] = []
    re_compile_date_format = DATE_FORMATS.get(datetime_date_format)
    for elem_path in folder_contents:
        folder_date = date_source(elem_path).get_folder_date(datetime_date_format, re_compile_date_format)
        time_delta = relativedelta(current_date, folder_date)
        months_difference = time_delta.years * 12 + time_delta.months
        if months_difference >= offset:
            result.append(elem_path)

    assert verdict == result


@pytest.mark.parametrize(
    "folder_contents, offset,current_date, date_source,datetime_date_format, verdict",
    [
        (["2023-05-11", "2023-06-11", "2024-03-01", "2024-04-12", "2024-05-12", "2023-05-12", "2024-03-27",
          "2024-03-28"],
         0, datetime(2024, 5, 27), DateFromName, "%Y-%m-%d",
         ["2023-05-11", "2023-06-11", "2024-03-01", "2024-04-12", "2024-05-12", "2023-05-12", "2024-03-27",
          "2024-03-28"]),

        (["2023-05-12", "2023-12-31", "2024-03-28", "2024-04-26", "2024-04-27", "2024-04-28", "2024-05-26",
          "2024-05-30", "2024-05-27"],
         1, datetime(2024, 5, 27), DateFromName, "%Y-%m-%d",
         (["2023-05-12"])),

        (["2022-05-12", "2022-12-31", "2023-03-28", "2023-04-26", "2025-04-27", "2021-04-28", "2022-05-25",
          "2022-05-30", "2022-05-26", "2022-05-27", "2022-05-28"],
         2, datetime(2024, 5, 27), DateFromName, "%Y-%m-%d",
         ["2022-05-12", "2021-04-28", "2022-05-25",
          "2022-05-26", "2022-05-27"])

    ]

)
def test_current_year_with_offset(folder_contents, offset, current_date, date_source, datetime_date_format, verdict):
    result: List[str] = []
    re_compile_date_format = DATE_FORMATS.get(datetime_date_format)
    for elem_path in folder_contents:
        folder_date = date_source(elem_path).get_folder_date(datetime_date_format, re_compile_date_format)
        delete_after_date = folder_date.replace(year=folder_date.year + offset)

        if current_date >= delete_after_date:
            result.append(elem_path)
    assert verdict == result
