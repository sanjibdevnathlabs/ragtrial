"""
Database configuration classes.

Contains configuration for SQLite, MySQL, and PostgreSQL databases
with master-slave architecture support.
"""


class SQLiteWriteConfig:
    """SQLite write (master) database configuration"""
    path: str = "storage/metadata.db"
    debug: bool = False


class SQLiteReadConfig:
    """SQLite read (slave) database configuration"""
    path: str = "storage/metadata.db"
    debug: bool = False


class SQLiteConfig:
    """SQLite database configuration with read-write split"""
    write: SQLiteWriteConfig = None
    read: SQLiteReadConfig = None


class MySQLWriteConfig:
    """MySQL write (master) database configuration"""
    host: str = "localhost"
    port: int = 3306
    database: str = "ragtrial"
    username: str = "ragtrial_user"
    password: str = ""
    charset: str = "utf8mb4"
    pool_size: int = 5
    max_overflow: int = 10
    debug: bool = False


class MySQLReadConfig:
    """MySQL read (slave) database configuration"""
    host: str = "localhost"
    port: int = 3306
    database: str = "ragtrial"
    username: str = "ragtrial_readonly"
    password: str = ""
    charset: str = "utf8mb4"
    pool_size: int = 10
    max_overflow: int = 20
    debug: bool = False


class MySQLConfig:
    """MySQL database configuration with read-write split"""
    write: MySQLWriteConfig = None
    read: MySQLReadConfig = None


class PostgreSQLWriteConfig:
    """PostgreSQL write (master) database configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "ragtrial"
    username: str = "ragtrial_user"
    password: str = ""
    schema: str = "public"
    pool_size: int = 5
    max_overflow: int = 10
    debug: bool = False


class PostgreSQLReadConfig:
    """PostgreSQL read (slave) database configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "ragtrial"
    username: str = "ragtrial_readonly"
    password: str = ""
    schema: str = "public"
    pool_size: int = 10
    max_overflow: int = 20
    debug: bool = False


class PostgreSQLConfig:
    """PostgreSQL database configuration with read-write split"""
    write: PostgreSQLWriteConfig = None
    read: PostgreSQLReadConfig = None


class DatabaseConfig:
    """
    Database configuration with master-slave architecture support.
    
    Supports three database drivers: sqlite, mysql, postgresql.
    Each driver has separate read (slave) and write (master) configurations.
    """
    driver: str = "sqlite"
    pool_pre_ping: bool = True
    pool_recycle: int = 3600
    connect_timeout: int = 10
    sqlite: SQLiteConfig = None
    mysql: MySQLConfig = None
    postgresql: PostgreSQLConfig = None

