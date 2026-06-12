import os
import shutil
from src.core.logger import get_logger

logger = get_logger(__name__)

class FileManager:
    def move(self, source: str, destination: str):
        os.makedirs(destination, exist_ok=True)

        filename = os.path.basename(source)
        dest_path = os.path.join(destination, filename)

        if os.path.exists(dest_path):
            logger.warning(f"Arquivo já existe no destino. Sobrescrevendo: {dest_path}")
            os.remove(dest_path)

        shutil.move(source, dest_path)
        logger.info(f"Arquivo movido para: {dest_path}")