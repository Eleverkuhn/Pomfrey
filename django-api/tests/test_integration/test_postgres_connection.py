from django.test import TestCase
from django.db import connection, connections
from django.db.utils import OperationalError

from utils import BaseDatabaseTest


class DatabaseTestCase(TestCase, BaseDatabaseTest):
    def test_database_connection(self) -> None:
        try:
            connections['default'].cursor()
        except OperationalError:
            self.fail("Database connection failed!")

    def test_SQL_query_is_executed(self) -> None:
        cursor = connection.cursor()
        self.execute_test_query(cursor)
