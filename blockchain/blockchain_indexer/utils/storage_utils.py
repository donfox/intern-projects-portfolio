"""
********************************************************************************
storage_utils.py -- File Storage Utilities

Provides file-based storage for blockchain blocks as JSON files.
Supports both pretty-printed and minified JSON formats.

Features:
    - Atomic file writes (write to temp, then rename)
    - Automatic directory creation
    - Duplicate detection
    - Batch operations
    - Compression support (optional)

Developed by: Don Fox
Date: 2025-12-09
********************************************************************************
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from config import DATA_DIR, ADD_JSON_EXTENSION, PRETTY_PRINT_JSON

logger = logging.getLogger(__name__)


def get_block_file_path(block_height: int) -> Path:
    """
    Get the file path for a block.

    Args:
        block_height: Block height/number

    Returns:
        Path object for the block file
    """
    extension = ".json" if ADD_JSON_EXTENSION else ""
    return DATA_DIR / f"{block_height}{extension}"


def save_block_to_file(block_height: int, block_data: dict) -> bool:
    """
    Save a block to a JSON file.

    Args:
        block_height: Block height/number
        block_data: Block data dictionary

    Returns:
        True if saved successfully, False otherwise
    """
    file_path = get_block_file_path(block_height)

    # Check if file already exists
    if file_path.exists():
        logger.debug(f"Block file {block_height} already exists, skipping")
        return False

    try:
        # Write to temporary file first (atomic write)
        temp_path = file_path.with_suffix('.tmp')

        with temp_path.open('w') as f:
            if PRETTY_PRINT_JSON:
                json.dump(block_data, f, indent=2)
            else:
                json.dump(block_data, f)

        # Rename to final location (atomic operation)
        temp_path.rename(file_path)

        logger.debug(f"Saved block {block_height} to {file_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to save block {block_height} to file: {e}")

        # Clean up temp file if it exists
        if temp_path.exists():
            temp_path.unlink()

        return False


def load_block_from_file(block_height: int) -> Optional[dict]:
    """
    Load a block from a JSON file.

    Args:
        block_height: Block height/number

    Returns:
        Block data dictionary or None if not found
    """
    file_path = get_block_file_path(block_height)

    if not file_path.exists():
        logger.debug(f"Block file {block_height} not found")
        return None

    try:
        with file_path.open('r') as f:
            block_data = json.load(f)
        return block_data

    except Exception as e:
        logger.error(f"Failed to load block {block_height} from file: {e}")
        return None


def block_file_exists(block_height: int) -> bool:
    """
    Check if a block file exists.

    Args:
        block_height: Block height/number

    Returns:
        True if file exists, False otherwise
    """
    return get_block_file_path(block_height).exists()


def get_stored_block_heights() -> List[int]:
    """
    Get list of all block heights stored as files.

    Returns:
        Sorted list of block heights
    """
    block_heights = []

    try:
        pattern = "*.json" if ADD_JSON_EXTENSION else "*"

        for file_path in DATA_DIR.glob(pattern):
            # Extract block height from filename
            try:
                # Remove extension if present
                filename = file_path.stem
                block_height = int(filename)
                block_heights.append(block_height)
            except ValueError:
                # Skip non-numeric filenames
                logger.warning(f"Skipping non-numeric file: {file_path.name}")
                continue

        return sorted(block_heights)

    except Exception as e:
        logger.error(f"Failed to get stored block heights: {e}")
        return []


def delete_block_file(block_height: int) -> bool:
    """
    Delete a block file.

    Args:
        block_height: Block height/number

    Returns:
        True if deleted, False otherwise
    """
    file_path = get_block_file_path(block_height)

    if not file_path.exists():
        logger.debug(f"Block file {block_height} does not exist")
        return False

    try:
        file_path.unlink()
        logger.info(f"Deleted block file {block_height}")
        return True

    except Exception as e:
        logger.error(f"Failed to delete block file {block_height}: {e}")
        return False


def batch_save_blocks(blocks: List[tuple]) -> int:
    """
    Save multiple blocks to files.

    Args:
        blocks: List of (block_height, block_data) tuples

    Returns:
        Number of blocks successfully saved
    """
    saved_count = 0

    for block_height, block_data in blocks:
        if save_block_to_file(block_height, block_data):
            saved_count += 1

    logger.info(f"Batch saved {saved_count}/{len(blocks)} blocks to files")
    return saved_count


def get_storage_stats() -> dict:
    """
    Get file storage statistics.

    Returns:
        Dictionary with storage stats
    """
    stats = {
        'total_files': 0,
        'total_size_mb': 0.0,
        'earliest_block': None,
        'latest_block': None
    }

    try:
        block_heights = get_stored_block_heights()

        if block_heights:
            stats['total_files'] = len(block_heights)
            stats['earliest_block'] = block_heights[0]
            stats['latest_block'] = block_heights[-1]

            # Calculate total size
            total_size = sum(
                get_block_file_path(height).stat().st_size
                for height in block_heights
            )
            stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)

    except Exception as e:
        logger.error(f"Failed to get storage stats: {e}")

    return stats


def verify_file_integrity(block_height: int) -> bool:
    """
    Verify that a block file is valid JSON and contains expected fields.

    Args:
        block_height: Block height/number

    Returns:
        True if file is valid, False otherwise
    """
    block_data = load_block_from_file(block_height)

    if block_data is None:
        return False

    # Check for required fields
    required_fields = ['block', 'block_id']

    for field in required_fields:
        if field not in block_data:
            logger.error(f"Block {block_height} missing required field: {field}")
            return False

    # Verify block height matches
    stored_height = block_data.get('block', {}).get('header', {}).get('height')

    if stored_height != str(block_height) and stored_height != block_height:
        logger.error(
            f"Block height mismatch: file={block_height}, data={stored_height}"
        )
        return False

    return True


def cleanup_corrupted_files() -> int:
    """
    Scan all block files and delete corrupted ones.

    Returns:
        Number of corrupted files deleted
    """
    deleted_count = 0
    block_heights = get_stored_block_heights()

    logger.info(f"Scanning {len(block_heights)} block files for corruption...")

    for block_height in block_heights:
        if not verify_file_integrity(block_height):
            logger.warning(f"Corrupted file detected: block {block_height}")
            if delete_block_file(block_height):
                deleted_count += 1

    logger.info(f"Deleted {deleted_count} corrupted files")
    return deleted_count
