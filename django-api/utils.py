"""
This module provides various utilities for the project purposes
"""

import json
from pathlib import Path

from psycopg import Cursor


class BaseDatabaseTest:
    def execute_test_query(self, cursor: Cursor) -> None:
        cursor.execute("SELECT 1;")
        row = cursor.fetchone()
        self.assertEqual(row[0], 1)


class LoggingConfig:
    path = Path("logging_config.json")

    def get(self) -> None:
        with open(self.path) as json_config:
            config_file = json.load(json_config)
        return config_file
