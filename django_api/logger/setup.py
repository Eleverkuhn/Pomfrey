import json, logging
from logging import Logger
from pathlib import Path


class LoggingConfig:
    path = Path("logger/logging_config.json")
    logger_name = "pomfrey"

    @property
    def logger(self) -> Logger:
        return logging.getLogger(self.logger_name)

    def load(self) -> None:
        with open(self.path) as json_config:
            config_file = json.load(json_config)
        return config_file

    def get_logger(self) -> Logger:  # FIX: remove this
        logger = logging.getLogger(self.logger_name)
        return logger


class OnlyInfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.INFO
