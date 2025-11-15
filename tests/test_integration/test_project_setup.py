import requests
from unittest import TestCase

import psycopg
# from django.test import TestCase
# from django.urls import reverse

from config import Settings


class TestProjectSetup(TestCase):
    def setUp(self) -> None:
        self.settings = Settings()

    def test_env_variables_loaded(self) -> None:
        self.assertTrue(self.settings.postgres_password)
        self.assertTrue(self.settings.postgres_user)
        self.assertTrue(self.settings.postgres_db)
        self.assertTrue(self.settings.postgres_port)
        self.assertTrue(self.settings.postgres_host)

    def test_connection_to_postgres(self) -> None:
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

    def test_connection_to_django_container(self) -> None:
        url = "http://localhost:8000/"
        try:
            response = requests.get(url, timeout=5)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.RequestException as exc:
            self.fail(f"Django server not reachable: {exc}")
