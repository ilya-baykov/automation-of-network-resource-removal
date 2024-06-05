import json
from typing import NamedTuple, Dict, List
from logging import getLogger

logger = getLogger(__name__)


class ConfigParams(NamedTuple):
    table_path: str
    attached_file_path: str
    subject: str
    message: str
    mail_recipients: List[str]
    mail_sender: str


def json_reader(config_file: str) -> ConfigParams:
    """Считывает config.json и возвоащает нужнные параметры"""
    try:
        with open(config_file, "r", encoding="utf-8") as json_file:
            config: Dict[str, str] = json.load(json_file)
            config['mail_recipients'] = config.pop('mail_recipient')
            logger.debug("Json-файл считан %s", ConfigParams(**config))
            return ConfigParams(**config)
    except Exception as e:
        logger.error("Ошибка чтения json-файла: %s", e)
