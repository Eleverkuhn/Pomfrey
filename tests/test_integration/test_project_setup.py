import os
from unittest import TestCase

import psycopg
from dotenv import load_dotenv


class TestEnvironment(TestCase):
    def test_env_variables_loaded(self) -> None:
        load_dotenv()
        postgres_password = os.getenv("POSTGRES_PASSWORD")
        postgres_user = os.getenv("POSTGRES_USER")
        postgres_db = os.getenv("POSTGRES_DB")
        postgres_port = os.getenv("POSTGRES_PORT")
        postgres_host = os.getenv("POSTGRES_HOST")

        self.assertTrue(postgres_password)
        self.assertTrue(postgres_user)
        self.assertTrue(postgres_db)
        self.assertTrue(postgres_port)
        self.assertTrue(postgres_host)


class TestPostgreSQL(TestCase):
    def test_connection(self) -> None:
        load_dotenv()
        conn_params = {
            "dbname": os.getenv("POSTGRES_DB"),
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "host": os.getenv("POSTGRES_HOST"),
            "port": os.getenv("POSTGRES_PORT")
        }
        with psycopg.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECt 1;")
                result = cur.fetchone()
                self.assertEqual(result[0], 1)
