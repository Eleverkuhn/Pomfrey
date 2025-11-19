"""
This module provides various utilities for the project purposes
"""

from django.test import TestCase
from psycopg import Cursor


class BaseDatabaseTest:
    def execute_test_query(self, cursor: Cursor) -> None:
        cursor.execute("SELECT 1;")
        row = cursor.fetchone()
        self.assertEqual(row[0], 1)


class BaseLoginTest(TestCase):
    def setUp(self) -> None:
        self.data = {
            "email": "test@example.com",
            "password": "ComplicatedP@sSw0rd",
        }


class BaseRegistryTest(BaseLoginTest):
    def setUp(self) -> None:
        super().setUp()
        self.data.update({"confirm_password": self.data.get("password")})
