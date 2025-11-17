import requests
from unittest import TestCase

import psycopg

from config import settings
from logger.setup import LoggingConfig
from utils import BaseDatabaseTest


class TestProjectSetup(TestCase, BaseDatabaseTest):
    def test_env_variables_loaded(self) -> None:
        self.assertTrue(settings.postgres_password)
        self.assertTrue(settings.postgres_user)
        self.assertTrue(settings.postgres_db)
        self.assertTrue(settings.postgres_port)
        self.assertTrue(settings.postgres_host)

    def test_connection_to_postgres(self) -> None:
        conn_params = {
            "dbname": settings.postgres_db,
            "user": settings.postgres_user,
            "password": settings.postgres_password,
            "host": settings.postgres_host,
            "port": settings.postgres_port
        }
        with psycopg.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                self.execute_test_query(cur)

    def test_connection_to_django_container(self) -> None:
        url = "http://localhost:8000/"
        try:
            response = requests.get(url, timeout=5)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.RequestException as exc:
            self.fail(f"Django server not reachable: {exc}")


class TestLoggingConfig(TestCase):
    def setUp(self) -> None:
        self.logger_config = LoggingConfig()
        self.logger = self.logger_config.get_logger()
        self.test_log_message = "test"

    def test_logger_config_file_is_loaded(self) -> None:
        config = self.logger_config.load()
        self.assertTrue(config)

    def test_logger_outputs_info_messages_to_logs_info(self) -> None:
        self.logger.info(self.test_log_message)
        self._find_log_message("logs/info.log")

    def test_logger_outputs_warning_messages_to_logs_warning(self) -> None:
        self.logger.warning(self.test_log_message)
        self._find_log_message("logs/warnings.log")

    def test_logger_outputs_debug_messages_to_console(self) -> None:
        with self.assertLogs(self.logger, level="DEBUG") as cm:
            self.logger.debug(self.test_log_message)
        self._find_log_message_in_source(cm.output)

    def _find_log_message(self, log_file: str) -> None:
        self._read_log_file(log_file)

    def _read_log_file(self, path: str) -> None:
        with open(path) as log_file:
            self._find_log_message_in_source(log_file)

    def _find_log_message_in_source(self, source) -> None:
        self.assertTrue(any(self.test_log_message in msg for msg in source))
