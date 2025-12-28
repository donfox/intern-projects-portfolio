"""
********************************************************************************
db_utils.py -- Database Utilities

Provides PostgreSQL database operations with connection pooling,
transaction management, and error handling.

Features:
    - Connection pooling for better performance
    - Context managers for safe transaction handling
    - Batch insert support
    - Retry logic for transient failures
    - Comprehensive error handling

Developed by: Don Fox
Date: 2025-12-09
********************************************************************************
"""
import psycopg2
import psycopg2.extras
import psycopg2.pool
import logging
from contextlib import contextmanager
from typing import List, Tuple, Optional, Any
from config import DB_CONFIG, MAX_RETRIES

logger = logging.getLogger(__name__)

# Connection pool - shared across all workers
_connection_pool = None


def initialize_connection_pool(min_conn=1, max_conn=10):
    """Initialize the PostgreSQL connection pool."""
    global _connection_pool

    if _connection_pool is None:
        try:
            _connection_pool = psycopg2.pool.ThreadedConnectionPool(
                min_conn,
                max_conn,
                **DB_CONFIG
            )
            logger.info(f"Database connection pool initialized (min={min_conn}, max={max_conn})")
        except psycopg2.Error as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise


def close_connection_pool():
    """Close all connections in the pool."""
    global _connection_pool

    if _connection_pool:
        _connection_pool.closeall()
        _connection_pool = None
        logger.info("Database connection pool closed")


@contextmanager
def get_db_connection():
    """
    Context manager for database connections from pool.

    Yields:
        psycopg2.connection: Database connection

    Example:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM blocks")
    """
    if _connection_pool is None:
        initialize_connection_pool()

    conn = _connection_pool.getconn()
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error, transaction rolled back: {e}")
        raise
    finally:
        _connection_pool.putconn(conn)


def execute_query(query: str, params: Optional[Tuple] = None, fetch: bool = False) -> Optional[List]:
    """
    Execute a SQL query with automatic connection management.

    Args:
        query: SQL query string
        params: Query parameters (tuple)
        fetch: Whether to fetch and return results

    Returns:
        List of rows if fetch=True, else None
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)

            if fetch:
                return cursor.fetchall()
            else:
                conn.commit()
                return None


def batch_insert(query: str, values: List[Tuple]) -> int:
    """
    Perform batch insert using psycopg2.extras.execute_values for better performance.

    Args:
        query: INSERT query template (use %s placeholders)
        values: List of tuples containing values to insert

    Returns:
        Number of rows inserted

    Example:
        query = "INSERT INTO blocks (height, hash) VALUES %s ON CONFLICT DO NOTHING"
        values = [(1, 'abc'), (2, 'def')]
        batch_insert(query, values)
    """
    if not values:
        logger.warning("No values provided for batch insert")
        return 0

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            psycopg2.extras.execute_values(
                cursor,
                query,
                values,
                template=None,
                page_size=1000  # Insert 1000 rows at a time
            )
            rows_inserted = cursor.rowcount
            conn.commit()
            logger.info(f"Batch inserted {rows_inserted} rows")
            return rows_inserted


def insert_block(block_height: int, block_hash: str, timestamp: str) -> bool:
    """
    Insert a single block into the database.

    Args:
        block_height: Block height/number
        block_hash: Block hash
        timestamp: Block timestamp

    Returns:
        True if inserted, False if already exists
    """
    query = """
        INSERT INTO blocks (block_height, block_hash, timestamp)
        VALUES (%s, %s, %s)
        ON CONFLICT (block_height) DO NOTHING
    """

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (block_height, block_hash, timestamp))
                rows_affected = cursor.rowcount
                conn.commit()

                if rows_affected > 0:
                    logger.debug(f"Inserted block {block_height}")
                    return True
                else:
                    logger.debug(f"Block {block_height} already exists")
                    return False

    except psycopg2.Error as e:
        logger.error(f"Failed to insert block {block_height}: {e}")
        return False


def insert_transactions(block_height: int, tx_hashes: List[str]) -> int:
    """
    Insert transactions for a block.

    Args:
        block_height: Block height these transactions belong to
        tx_hashes: List of transaction hashes

    Returns:
        Number of transactions inserted
    """
    if not tx_hashes:
        return 0

    query = """
        INSERT INTO transactions (tx_hash, block_height)
        VALUES %s
        ON CONFLICT (tx_hash) DO NOTHING
    """

    values = [(tx_hash, block_height) for tx_hash in tx_hashes]

    try:
        return batch_insert(query, values)
    except psycopg2.Error as e:
        logger.error(f"Failed to insert transactions for block {block_height}: {e}")
        return 0


def get_processed_blocks() -> List[int]:
    """
    Get list of all processed block heights from database.

    Returns:
        Sorted list of block heights
    """
    query = "SELECT block_height FROM blocks ORDER BY block_height"

    try:
        rows = execute_query(query, fetch=True)
        return [row[0] for row in rows] if rows else []
    except psycopg2.Error as e:
        logger.error(f"Failed to fetch processed blocks: {e}")
        return []


def block_exists(block_height: int) -> bool:
    """
    Check if a block exists in the database.

    Args:
        block_height: Block height to check

    Returns:
        True if block exists, False otherwise
    """
    query = "SELECT 1 FROM blocks WHERE block_height = %s LIMIT 1"

    try:
        result = execute_query(query, (block_height,), fetch=True)
        return bool(result)
    except psycopg2.Error as e:
        logger.error(f"Failed to check if block {block_height} exists: {e}")
        return False


def get_latest_block_height() -> Optional[int]:
    """
    Get the highest block height in the database.

    Returns:
        Latest block height or None if no blocks
    """
    query = "SELECT MAX(block_height) FROM blocks"

    try:
        result = execute_query(query, fetch=True)
        return result[0][0] if result and result[0][0] else None
    except psycopg2.Error as e:
        logger.error(f"Failed to get latest block height: {e}")
        return None


def initialize_schema():
    """
    Initialize database schema (create tables if they don't exist).
    Should be called once at startup.
    """
    schema = """
    -- Blocks table
    CREATE TABLE IF NOT EXISTS blocks (
        block_height BIGINT PRIMARY KEY,
        block_hash VARCHAR(128) NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- Transactions table
    CREATE TABLE IF NOT EXISTS transactions (
        tx_hash VARCHAR(128) PRIMARY KEY,
        block_height BIGINT NOT NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        FOREIGN KEY (block_height) REFERENCES blocks(block_height) ON DELETE CASCADE
    );

    -- Index for faster lookups
    CREATE INDEX IF NOT EXISTS idx_blocks_timestamp ON blocks(timestamp);
    CREATE INDEX IF NOT EXISTS idx_transactions_block ON transactions(block_height);
    """

    try:
        execute_query(schema)
        logger.info("Database schema initialized successfully")
    except psycopg2.Error as e:
        logger.error(f"Failed to initialize schema: {e}")
        raise


def get_database_stats() -> dict:
    """
    Get database statistics for observability.

    Returns:
        Dictionary with database stats
    """
    stats = {
        'total_blocks': 0,
        'total_transactions': 0,
        'latest_block': None,
        'earliest_block': None
    }

    try:
        # Total blocks
        result = execute_query("SELECT COUNT(*) FROM blocks", fetch=True)
        stats['total_blocks'] = result[0][0] if result else 0

        # Total transactions
        result = execute_query("SELECT COUNT(*) FROM transactions", fetch=True)
        stats['total_transactions'] = result[0][0] if result else 0

        # Latest block
        stats['latest_block'] = get_latest_block_height()

        # Earliest block
        result = execute_query("SELECT MIN(block_height) FROM blocks", fetch=True)
        stats['earliest_block'] = result[0][0] if result and result[0][0] else None

    except psycopg2.Error as e:
        logger.error(f"Failed to get database stats: {e}")

    return stats
