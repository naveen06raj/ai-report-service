
import logging
import os
from datetime import datetime
from pathlib import Path
from uuid import UUID

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# ============================================================
# Compatible Cursor
# ============================================================

class CompatibleCursor:
    """Wrapper around a MySQL cursor for repository compatibility."""

    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, sql, parameters=None):
        if parameters is None:
            self._cursor.execute(sql)
        else:
            converted_parameters = tuple(
                str(value) if isinstance(value, UUID) else value
                for value in parameters
            )

            self._cursor.execute(sql, converted_parameters)

        return self

    def fetchone(self):
        return self._convert(self._cursor.fetchone())

    def fetchall(self):
        return [
            self._convert(row)
            for row in self._cursor.fetchall()
        ]

    def _convert(self, row):
        if row is None:
            return None

        names = [
            column[0]
            for column in (self._cursor.description or [])
        ]

        values = list(row)

        for index, name in enumerate(names):
            value = values[index]

            if (
                name == "conversation_id"
                and isinstance(value, (str, bytes))
            ):
                try:
                    if isinstance(value, bytes):
                        value = value.decode()

                    values[index] = UUID(value)

                except (ValueError, AttributeError):
                    pass

            elif (
                name in {
                    "created_at",
                    "updated_at",
                    "last_message_at",
                }
                and isinstance(value, str)
            ):
                try:
                    values[index] = datetime.fromisoformat(value)
                except ValueError:
                    pass

        return tuple(values)

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def description(self):
        return self._cursor.description

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._cursor.close()
        return False


# ============================================================
# Compatible Connection
# ============================================================

class CompatibleConnection:
    """
    Wraps a MySQL connection.

    If SSH tunneling is enabled, the tunnel remains active
    until this connection is closed.
    """

    def __init__(self, connection, ssh_tunnel=None):
        self._connection = connection
        self._ssh_tunnel = ssh_tunnel
        self._closed = False

    def cursor(self):
        return CompatibleCursor(
            self._connection.cursor()
        )

    def commit(self):
        return self._connection.commit()

    def rollback(self):
        return self._connection.rollback()

    def close(self):
        if self._closed:
            return

        self._closed = True

        try:
            self._connection.close()
        finally:
            if self._ssh_tunnel is not None:
                try:
                    if self._ssh_tunnel.is_active:
                        self._ssh_tunnel.stop()
                except Exception:
                    logger.exception(
                        "Failed to stop SSH tunnel"
                    )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is not None:
                self.rollback()
        finally:
            self.close()

        return False


# ============================================================
# Database Mode — MySQL Only
# ============================================================

def get_database_mode():
    """
    The application supports MySQL only.

    DATABASE_MODE may be omitted because MySQL is the default.
    If supplied, it must be set to 'mysql'.
    """

    mode = os.getenv(
        "DATABASE_MODE",
        "mysql",
    ).strip().lower()

    if mode != "mysql":
        raise ValueError(
            "Only MySQL is supported. "
            "Set DATABASE_MODE=mysql in your environment."
        )

    return "mysql"


# ============================================================
# Required Environment Variables
# ============================================================

def _get_required_database_variables():
    required = [
        "DB_HOST",
        "DB_USER",
        "DB_PASSWORD",
        "DB_NAME",
    ]

    missing = [
        name
        for name in required
        if not os.getenv(name)
    ]

    if missing:
        raise RuntimeError(
            "Missing database environment variables: "
            + ", ".join(missing)
        )


# ============================================================
# Direct MySQL Connection
# ============================================================

def _get_direct_mysql_connection():
    import pymysql

    connection = pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        charset="utf8mb4",
        connect_timeout=10,
        read_timeout=30,
        write_timeout=30,
        autocommit=False,
    )

    logger.info("Direct MySQL connection established")

    return CompatibleConnection(connection)


# ============================================================
# MySQL Connection Through SSH Tunnel
# ============================================================

def _get_ssh_mysql_connection():
    """
    Connect to private AWS RDS through an SSH bastion.

    Required environment variables:
        SSH_HOST
        SSH_USER
        SSH_PRIVATE_KEY

    The SSH private key must be available to the running
    application and must not be committed to Git.
    """

    import pymysql

    try:
        from sshtunnel import SSHTunnelForwarder
    except ImportError as exc:
        raise RuntimeError(
            "SSH tunneling requires sshtunnel. "
            "Install it with: python -m pip install sshtunnel"
        ) from exc

    ssh_host = os.getenv("SSH_HOST")
    ssh_user = os.getenv("SSH_USER")
    ssh_private_key = os.getenv("SSH_PRIVATE_KEY")

    missing = []

    if not ssh_host:
        missing.append("SSH_HOST")

    if not ssh_user:
        missing.append("SSH_USER")

    if not ssh_private_key:
        missing.append("SSH_PRIVATE_KEY")

    if missing:
        raise RuntimeError(
            "Missing SSH environment variables: "
            + ", ".join(missing)
        )

    key_path = Path(
        ssh_private_key
    ).expanduser()

    if not key_path.is_absolute():
        key_path = Path.cwd() / key_path

    if not key_path.is_file():
        raise FileNotFoundError(
            f"SSH private key not found: {key_path}"
        )

    ssh_port = int(os.getenv("SSH_PORT", "22"))
    db_port = int(os.getenv("DB_PORT", "3306"))

    tunnel = None

    try:
        logger.info(
            "Starting SSH tunnel through %s:%s",
            ssh_host,
            ssh_port,
        )

        tunnel = SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_user,
            ssh_pkey=str(key_path),
            remote_bind_address=(
                os.environ["DB_HOST"],
                db_port,
            ),
            # Select an available local port.
            local_bind_address=("127.0.0.1", 0),
        )

        tunnel.start()

        logger.info(
            "SSH tunnel established on local port %s",
            tunnel.local_bind_port,
        )

        connection = pymysql.connect(
            host="127.0.0.1",
            port=tunnel.local_bind_port,
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            charset="utf8mb4",
            connect_timeout=10,
            read_timeout=30,
            write_timeout=30,
            autocommit=False,
        )

        logger.info(
            "MySQL connection established through SSH tunnel"
        )

        return CompatibleConnection(
            connection,
            ssh_tunnel=tunnel,
        )

    except Exception:
        if tunnel is not None:
            try:
                tunnel.stop()
            except Exception:
                logger.exception(
                    "Failed to stop SSH tunnel after connection error"
                )

        raise


# ============================================================
# MySQL Connection Selector
# ============================================================

def _get_mysql_connection():
    """
    MYSQL_USE_SSH_TUNNEL=true:
        Connect through an SSH bastion.

    MYSQL_USE_SSH_TUNNEL=false:
        Connect directly to MySQL.
    """

    _get_required_database_variables()

    use_ssh = os.getenv(
        "MYSQL_USE_SSH_TUNNEL",
        "false",
    ).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    if use_ssh:
        return _get_ssh_mysql_connection()

    return _get_direct_mysql_connection()


# ============================================================
# Public Database Connection
# ============================================================

def get_database_connection():
    """Create and return a MySQL connection."""

    get_database_mode()

    return _get_mysql_connection()


# ============================================================
# Database Connection Test
# ============================================================

def test_database_connection():
    """Return True if a MySQL connection test succeeds."""

    connection = None

    try:
        connection = get_database_connection()

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

            return (
                result is not None
                and result[0] == 1
            )

    except Exception:
        logger.exception(
            "MySQL database connection test failed"
        )
        return False

    finally:
        if connection is not None:
            connection.close()
