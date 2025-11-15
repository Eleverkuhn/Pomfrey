import os
from unittest import TestCase

import psycopg
from dotenv import load_dotenv


class TestEnvironment(TestCase):
    def test_env_variables_loaded(self) -> None:
        load_dotenv()
        postgres_root_pw = os.getenv("POSTGRES_ROOT_PW")
        postgres_user = os.getenv("POSTGRES_USER")
        postgres_pw = os.getenv("POSTGRES_PW")
        postgres_db = os.getenv("POSTGRES_DB")
        postgres_port = os.getenv("POSTGRES_PORT")

        self.assertTrue(postgres_root_pw)
        self.assertTrue(postgres_user)
        self.assertTrue(postgres_pw)
        self.assertTrue(postgres_db)
        self.assertTrue(postgres_port)


class TestPostgreSQL(TestCase):
    def test_connection(self) -> None:
        with psycopg.connect("dbname=test user=postgres") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECt 1;")
                result = cur.fetchone()
                self.assertEqual(result[0], 1)
