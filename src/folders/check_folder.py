import os
from typing import Dict
from src.folders.FolderOperations import CleanResult


def checking_folder(folder_path: str) -> Dict[str, CleanResult] | None:
    # Проверьте, существует ли папка и является ли она директорией
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        # Проверьте, есть ли доступ на запись и выполнение
        if os.access(folder_path, os.W_OK) and os.access(folder_path, os.X_OK):
            return None
        else:
            return {
                "Нет файлов на удаление": CleanResult(status="Не выполнено", comment="Нет доступа для удаления файлов")}
    else:
        return {
            "Нет файлов на удаление": CleanResult(status="Не выполнено", comment="Не удалось подключиться к папке")}
