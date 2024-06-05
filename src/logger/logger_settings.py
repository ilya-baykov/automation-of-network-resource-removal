from logging import getLogger, basicConfig, DEBUG, FileHandler
from datetime import datetime
from src.utils.json_reader import ConfigParams


def setup_logger(config_params: ConfigParams):
    logger = getLogger()
    FORMAT = '%(asctime)s : %(name)s : %(levelname)s : %(message)s'
    file_handler = FileHandler(
        f"{config_params.attached_file_path}\\Logger_{datetime.today().strftime('%d.%m.%Y')}.log")
    file_handler.setLevel(DEBUG)
    basicConfig(level=DEBUG, format=FORMAT, handlers=[file_handler])
    return logger
