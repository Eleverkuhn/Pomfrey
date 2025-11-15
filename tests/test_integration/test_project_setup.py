from unittest import TestCase

import psycopg

from config import Settings


class BaseSetupTest(TestCase):
    def setUp(self) -> None:
        self.settings = Settings()


class TestEnvironment(BaseSetupTest):
    def test_env_variables_loaded(self) -> None:
        self.assertTrue(self.settings.postgres_password)
        self.assertTrue(self.settings.postgres_user)
        self.assertTrue(self.settings.postgres_db)
        self.assertTrue(self.settings.postgres_port)
        self.assertTrue(self.settings.postgres_host)


class TestPostgreSQL(BaseSetupTest):
    def test_connection(self) -> None:
        conn_params = {
            "dbname": self.settings.postgres_db,
            "user": self.settings.postgres_user,
            "password": self.settings.postgres_password,
            "host": self.settings.postgres_host,
            "port": self.settings.postgres_port
        }
        with psycopg.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECt 1;")
                result = cur.fetchone()
                self.assertEqual(result[0], 1)
