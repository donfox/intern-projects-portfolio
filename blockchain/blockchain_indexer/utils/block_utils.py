"""
********************************************************************************
block_utils.py -- Block Utilities

Core utilities for fetching, parsing, and processing blockchain blocks.
Supports retry logic, validation, and flexible storage options.

Features:
    - HTTP block fetching with retry logic
    - Block data parsing and validation
    - Dual storage support (database + files)
    - Transaction extraction
    - Idempotent processing

Developed by: Don Fox
Date: 2025-12-09
********************************************************************************
"""
import requests
import logging
import time
from typing import Optional, Dict, List, Tuple
from requests.exceptions import Timeout, RequestException, ConnectionError

from config import (
    LATEST_BLOCK_URL,
    BLOCK_URL_TEMPLATE,
    API_TIMEOUT,
    BLOCK_FETCH_DELAY,
    MAX_RETRIES,
    RETRY_BACKOFF,
    ENABLE_DB_STORAGE,
    ENABLE_FILE_STORAGE
)

logger = logging.getLogger(__name__)


def fetch_block_from_api(url: str, retry_count: int = 0) -> Optional[dict]:
    """
    Fetch block data from API with retry logic.

    Args:
        url: API endpoint URL
        retry_count: Current retry attempt (for recursion)

    Returns:
        Block data as dictionary, or None if failed
    """
    try:
        response = requests.get(url, timeout=API_TIMEOUT)
        response.raise_for_status()

        block_data = response.json()
        logger.debug(f"Successfully fetched block from {url}")
        return block_data

    except Timeout:
        logger.warning(f"Timeout fetching from {url} (attempt {retry_count + 1}/{MAX_RETRIES})")

    except ConnectionError as e:
        logger.warning(f"Connection error for {url}: {e} (attempt {retry_count + 1}/{MAX_RETRIES})")

    except RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
        return None

    # Retry logic
    if retry_count < MAX_RETRIES:
        wait_time = RETRY_BACKOFF ** retry_count
        logger.info(f"Retrying in {wait_time}s...")
        time.sleep(wait_time)
        return fetch_block_from_api(url, retry_count + 1)

    logger.error(f"Failed to fetch from {url} after {MAX_RETRIES} retries")
    return None


def fetch_latest_block() -> Optional[dict]:
    """
    Fetch the latest block from the blockchain API.

    Returns:
        Latest block data or None
    """
    return fetch_block_from_api(LATEST_BLOCK_URL)


def fetch_block_by_height(block_height: int) -> Optional[dict]:
    """
    Fetch a specific block by height.

    Args:
        block_height: Block height/number

    Returns:
        Block data or None
    """
    url = BLOCK_URL_TEMPLATE.format(block_height)
    return fetch_block_from_api(url)


def parse_block_data(block_data: dict) -> Optional[Tuple[int, str, str, List[str]]]:
    """
    Parse block data and extract key fields.

    Args:
        block_data: Raw block data from API

    Returns:
        Tuple of (block_height, block_hash, timestamp, tx_hashes) or None if invalid
    """
    try:
        # Extract block height
        block_height = block_data.get('block', {}).get('header', {}).get('height')
        if block_height is None:
            logger.error("Block height missing in block data")
            return None

        # Convert to int if it's a string
        block_height = int(block_height)

        # Extract block hash
        block_hash = block_data.get('block_id', {}).get('hash')
        if not block_hash:
            logger.error(f"Block hash missing for block {block_height}")
            return None

        # Extract timestamp
        timestamp = block_data.get('block', {}).get('header', {}).get('time')
        if not timestamp:
            logger.error(f"Timestamp missing for block {block_height}")
            return None

        # Extract transaction hashes
        tx_hashes = block_data.get('block', {}).get('data', {}).get('txs', [])

        return (block_height, block_hash, timestamp, tx_hashes)

    except Exception as e:
        logger.error(f"Failed to parse block data: {e}")
        return None


def store_block(block_height: int, block_hash: str, timestamp: str,
                tx_hashes: List[str], block_data: dict) -> bool:
    """
    Store block in enabled storage backends (database and/or files).

    Args:
        block_height: Block height/number
        block_hash: Block hash
        timestamp: Block timestamp
        tx_hashes: List of transaction hashes
        block_data: Full block data (for file storage)

    Returns:
        True if stored in at least one backend, False otherwise
    """
    success = False

    # Store in database
    if ENABLE_DB_STORAGE:
        try:
            from .db_utils import insert_block, insert_transactions

            # Insert block metadata
            if insert_block(block_height, block_hash, timestamp):
                logger.debug(f"Block {block_height} stored in database")
                success = True

            # Insert transactions
            if tx_hashes:
                tx_count = insert_transactions(block_height, tx_hashes)
                logger.debug(f"{tx_count} transactions stored for block {block_height}")

        except Exception as e:
            logger.error(f"Failed to store block {block_height} in database: {e}")

    # Store in files
    if ENABLE_FILE_STORAGE:
        try:
            from .storage_utils import save_block_to_file

            if save_block_to_file(block_height, block_data):
                logger.debug(f"Block {block_height} stored as file")
                success = True

        except Exception as e:
            logger.error(f"Failed to store block {block_height} as file: {e}")

    return success


def process_block(block_data: dict) -> bool:
    """
    Process a block: parse, validate, and store.

    Args:
        block_data: Raw block data from API

    Returns:
        True if processed successfully, False otherwise
    """
    # Parse block data
    parsed = parse_block_data(block_data)
    if parsed is None:
        return False

    block_height, block_hash, timestamp, tx_hashes = parsed

    # Check if already processed (idempotency)
    if is_block_processed(block_height):
        logger.debug(f"Block {block_height} already processed, skipping")
        return False

    # Store the block
    if store_block(block_height, block_hash, timestamp, tx_hashes, block_data):
        logger.info(f"Successfully processed block {block_height}")
        return True
    else:
        logger.error(f"Failed to store block {block_height}")
        return False


def is_block_processed(block_height: int) -> bool:
    """
    Check if a block has already been processed.

    Args:
        block_height: Block height/number

    Returns:
        True if block exists in any enabled storage, False otherwise
    """
    # Check database
    if ENABLE_DB_STORAGE:
        try:
            from .db_utils import block_exists
            if block_exists(block_height):
                return True
        except Exception as e:
            logger.error(f"Error checking database for block {block_height}: {e}")

    # Check file storage
    if ENABLE_FILE_STORAGE:
        try:
            from .storage_utils import block_file_exists
            if block_file_exists(block_height):
                return True
        except Exception as e:
            logger.error(f"Error checking files for block {block_height}: {e}")

    return False


def get_all_processed_blocks() -> List[int]:
    """
    Get list of all processed block heights from all enabled storage backends.

    Returns:
        Sorted list of unique block heights
    """
    all_blocks = set()

    # Get from database
    if ENABLE_DB_STORAGE:
        try:
            from .db_utils import get_processed_blocks
            db_blocks = get_processed_blocks()
            all_blocks.update(db_blocks)
        except Exception as e:
            logger.error(f"Error getting blocks from database: {e}")

    # Get from files
    if ENABLE_FILE_STORAGE:
        try:
            from .storage_utils import get_stored_block_heights
            file_blocks = get_stored_block_heights()
            all_blocks.update(file_blocks)
        except Exception as e:
            logger.error(f"Error getting blocks from files: {e}")

    return sorted(list(all_blocks))


def detect_missing_blocks(processed_blocks: Optional[List[int]] = None) -> List[int]:
    """
    Detect gaps in the sequence of processed blocks.

    Args:
        processed_blocks: Optional list of processed blocks (fetched if not provided)

    Returns:
        List of missing block heights
    """
    if processed_blocks is None:
        processed_blocks = get_all_processed_blocks()

    if len(processed_blocks) < 2:
        logger.info("Not enough blocks to detect gaps")
        return []

    missing = []
    for i in range(1, len(processed_blocks)):
        current = processed_blocks[i]
        previous = processed_blocks[i - 1]

        if current - previous > 1:
            # Gap detected
            gap = list(range(previous + 1, current))
            missing.extend(gap)

    if missing:
        logger.info(f"Detected {len(missing)} missing blocks")

    return missing


def validate_block_data(block_data: dict) -> bool:
    """
    Validate that block data has all required fields.

    Args:
        block_data: Block data dictionary

    Returns:
        True if valid, False otherwise
    """
    required_paths = [
        ['block', 'header', 'height'],
        ['block', 'header', 'time'],
        ['block_id', 'hash']
    ]

    for path in required_paths:
        data = block_data
        for key in path:
            if not isinstance(data, dict) or key not in data:
                logger.error(f"Missing required field: {'.'.join(path)}")
                return False
            data = data[key]

    return True
