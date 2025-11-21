import json, logging
from abc import ABC, abstractmethod
from logging import Logger
from pathlib import Path
from typing import override


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


class ProjectLogging(ABC):
    def __init__(self, *args) -> None:
        self.logger = LoggingConfig().logger
        self.context = self._build_context(*args)

    @property
    @abstractmethod
    def message(self) -> str:
        pass

    def create_log(self) -> None:
        self.logger.info(self.message)

    def _build_context(self, *args) -> str:
        context = " ".join(map(str, args))
        return context


class RegistryLogging(ProjectLogging):
    @property
    @override
    def message(self) -> str:
        message = f"User {self.context} has been successfully created"
        return message


class LoginLogging(ProjectLogging):
    @property
    @override
    def message(self) -> str:
        message = f"User {self.context} has been successfully logged in"
        return message


class OrderLogging(ProjectLogging):
    @property
    @override
    def message(self) -> str:
        message = f"New order {self.context} has been successfully created"
        return message
