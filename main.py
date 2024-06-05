import sys
from src.excel.ExcelSheet import ExcelSheet
from src.folders.FolderOperations import *
from src.folders.check_folder import checking_folder
from src.utils.exceptions import InvalidDate
from src.utils.json_reader import json_reader
from src.utils.selecting_handlers import cls_definition, selecting_date_source
from src.validators.check_Input_table import CheckInputTable
from src.user_format_handlers.DateParser import USER_SEASON_FORMAT_OPTIONS
from src.excel.ExelReporter import *
from src.email.EmailSender import *
from src.logger.logger_settings import setup_logger
from src.folders.FolderCreator import *

if __name__ == '__main__':
    current_time = datetime.datetime.now()

    config_params = json_reader('config/config.json')  # Считывание данных с json
    logger = setup_logger(config_params)  # Загрузка настроек логирования
    logger.info("Скрипт запущен")

    # Создание папок и подпапок для отчётов ( Год/Месяц )
    path_provider = PathProvider(config_params.attached_file_path, DateProvider(current_time))
    FolderCreator().create_folder(path_provider.get_year_path())
    FolderCreator().create_folder(path_provider.get_month_path())

    reporter_list = []  # Список для формирование отчёта

    exel_table = ExcelSheet(filename=config_params.table_path, min_row=2)  # Класс для работы с Exel-таблицей
    exel_rows = exel_table.get_data()  # Получение всех строк из таблицы в виде словаря

    check = CheckInputTable(exel_rows).check_validation()  # Проверка валидности таблицы

    exel_table.highlight_cells(check)  # Закрашивание ячеек ( проблемные - в красный, остальные - в белый )

    if bool(check):
        logger.info("Скрипт остановил свою работу из-за проблем в таблице ")
        sys.exit()

    for row in exel_rows:  # Обход всех строк из Exel-таблицы
        folder_path, regex_pattern, interval = row[3], row[4].strip(), row[5]
        date_modification = row[6].lower()
        task_number, process_name, analyst = row[0], row[1], row[2]

        logger.debug("Данные строки: Номер задачи: %s, Имя процесса: %s, Аналитик : %s",
                     task_number, process_name, analyst)

        logger.debug("Данные строки: Путь:%s, Пользовательский формат:%s, Получение даты:%s, Интервал :%s",
                     folder_path, regex_pattern, date_modification, interval)

        # Проверка папки ( её наличие и доступ к ней )
        checking_folder_result = checking_folder(folder_path)
        if checking_folder_result:
            reporter_list.append([task_number, process_name, analyst, folder_path, checking_folder_result,
                                  current_time.strftime("%d-%m-%Y %H:%M:%S"),
                                  current_time.strftime("%d-%m-%Y %H:%M:%S")])
            logger.error("Проблема с папкой:%s, ", checking_folder_result['Нет файлов на удаление'].comment)
            continue

        if row[7].strip().lower() == "не активен":
            continue

        # Определение типа ( файл/папка )
        is_file = (lambda mask: bool(os.path.splitext(mask)[1]) and re.match(r'^[a-zA-Z]+$',
                                                                             os.path.splitext(mask)[1][
                                                                             1:]) is not None)(regex_pattern)

        try:
            # Получение нужных форматов и их представление в datetime и re.compile()
            user_date_format, re_compile_date_format = UserDateFormatDetector.get_user_and_re_compile_date_format(
                regex_pattern)
            datetime_date_format = USER_SEASON_FORMAT_OPTIONS.get(user_date_format, None)
            logger.debug("Формат времени для модуля datetime: %s", datetime_date_format)


        except InvalidDate as e:
            logger.error("Ошибка в формате %s", e)
            continue

        # Классы для очистки и загрузки данных(файлов/папок), подходящие под пользовательский формат
        cleaner = FolderCleaner()
        content_loader = RecursiveFolderContentLoader(folder_path, regex_pattern, user_date_format,
                                                      re_compile_date_format, is_file)
        # Экземпляр класса для работы с текущей папкой
        current_folder = Folder(folder_path, content_loader=content_loader, cleaner=cleaner)
        folder_contents = current_folder.load_contents()  # Получение всех подходящих файлов/папок

        # Определение класса для обработки условия хранения
        storage_period_handler = cls_definition(storage_period=interval,
                                                date_source=selecting_date_source(date_modification),
                                                datetime_date_format=datetime_date_format,
                                                re_compile_date_format=re_compile_date_format)

        if storage_period_handler:
            # Список папок/файлов на удаление
            remove_files = storage_period_handler.process(folder_contents, current_time)
            logger.debug("Файлы на удаление: %s", remove_files)

            time_end = datetime.datetime.now()
            current_folder.add_files_to_delete(remove_files)
            report_dict = current_folder.clean()
            # Данные для формирования отчёта
            reporter_list.append([task_number, process_name, analyst, folder_path, report_dict,
                                  current_time.strftime("%d-%m-%Y %H:%M:%S"),
                                  time_end.strftime("%d-%m-%Y %H:%M:%S"),
                                  ])
            logger.debug("Данные для формирование отчёта: %s", reporter_list)

    # Экземпляр класса для формирования отчёта
    reporter = Reporter(path_provider.get_month_path())
    reporter.generate_report(reporter_list)

    try:
        email_sender = EmailSender(smtp_server="mail.center.rt.ru")
        email_sender.send_email(
            sender_email=config_params.mail_sender,
            recipient_emails=config_params.mail_recipients,
            subject=config_params.subject,
            message=config_params.message,
            attachment_path=reporter.filename
        )
    except Exception as e:
        logger.error("Ошибка отправки письма: %s", e)
