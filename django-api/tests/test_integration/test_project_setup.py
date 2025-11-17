import requests
from unittest import TestCase

import psycopg

from config import settings
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
