import os
import logging
from datetime import datetime

# Création du dossier logs s'il n'existe pas
os.makedirs("logs", exist_ok=True)

logger_config = logging.getLogger()
logger_config.setLevel(logging.INFO)

log_filename = (
    f"logs/snow_ingestion_{datetime.now().strftime('%Y%m%d')}.log"
)

file_handler = logging.FileHandler(
    log_filename,
    mode="a",
    encoding="utf-8"
)

console_handler = logging.StreamHandler()

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger_config.addHandler(file_handler)
logger_config.addHandler(console_handler)