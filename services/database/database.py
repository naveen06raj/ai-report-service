import logging
import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import register_uuid
from psycopg2.extensions import connection as PostgreSQLConnection


load_dotenv()

# Register Python UUID <-> PostgreSQL UUID support
register_uuid()

logger = logging.getLogger(__name__)


def get_database_connection() -> PostgreSQLConnection:
    """
    Create a PostgreSQL connection using environment variables.

    Required environment variables:
        DB_NAME
        DB_USER
        DB_PASSWORD
        DB_HOST
        DB_PORT
    """

    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")

    missing_variables = []

    if not db_name:
        missing_variables.append("DB_NAME")

    if not db_user:
        missing_variables.append("DB_USER")

    if not db_password:
        missing_variables.append("DB_PASSWORD")

    if not db_host:
        missing_variables.append("DB_HOST")

    if missing_variables:
        raise RuntimeError(
            "Missing database environment variables: "
            + ", ".join(missing_variables)
        )

    try:
        connection = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            connect_timeout=10,
        )

        logger.info(
            "PostgreSQL connection established successfully"
        )

        return connection

    except Exception:
        logger.exception(
            "Failed to connect to PostgreSQL"
        )
        raise


def test_database_connection() -> bool:
    """
    Test PostgreSQL connectivity using SELECT 1.
    """

    connection = None

    try:
        connection = get_database_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

        if result and result[0] == 1:
            logger.info(
                "PostgreSQL SELECT 1 test successful"
            )
            return True

        logger.error(
            "Unexpected SELECT 1 result: %s",
            result,
        )

        return False

    except Exception:
        logger.exception(
            "PostgreSQL SELECT 1 test failed"
        )
        return False

    finally:
        if connection:
            connection.close()

            logger.info(
                "PostgreSQL test connection closed"
            )