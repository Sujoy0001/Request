import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler


def configure_logging() -> None:
	level_name = os.getenv("LOG_LEVEL", "INFO").upper()
	level = getattr(logging, level_name, logging.INFO)
	logs = Path(__file__).resolve().parent.parent / ".logs"
	logs.mkdir(exist_ok=True)
	log_file = logs / "app.log"
	log_format = "%(asctime)s %(levelname)s %(name)s: %(message)s"
	formatter = logging.Formatter(log_format)

	file_handler = RotatingFileHandler(
		log_file,
		maxBytes=5 * 1024 * 1024,
		backupCount=3,
		encoding="utf-8",
	)
 
	file_handler.setFormatter(formatter)
	file_handler.setLevel(level)

	console_handler = logging.StreamHandler()
	console_handler.setFormatter(formatter)
	console_handler.setLevel(level)

	logging.basicConfig(
		level=level,
		handlers=[console_handler, file_handler],
	)
