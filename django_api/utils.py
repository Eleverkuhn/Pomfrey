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


class BaseRegistryTest(TestCase):
    def setUp(self) -> None:
        self.data = {
            "email": "test@example.com",
            "password": "test",
            "confirm_password": "test"
        }
