"""
********************************************************************************
gap_fixer.py -- Gap Fixer Service

Fetches missing blocks by height and processes them to fill gaps.
Works in conjunction with gap_detector.

Features:
    - Fetches specific blocks by height
    - Processes blocks from shared queue
    - Parallel processing support
    - Metrics tracking

Developed by: Don Fox
Date: 2025-12-09
********************************************************************************
"""
import logging
from multiprocessing import Queue
from typing import Optional

import sys
sys.path.append('..')

from config import BLOCK_FETCH_DELAY
from utils import (
    fetch_block_by_height,
    process_block,
    record_gap_fixed,
    record_block_failed,
    Timer
)

logger = logging.getLogger(__name__)


def fix_gaps_from_queue(task_queue: Queue, stop_signal, worker_id: int = 0) -> int:
    """
    Process gap blocks from the task queue.

    Args:
        task_queue: Shared queue containing ('gap', block_height) messages
        stop_signal: Multiprocessing Event for graceful shutdown
        worker_id: Worker identifier for logging

    Returns:
        Number of gaps fixed
    """
    logger.info(f"Gap fixer worker #{worker_id} started")

    fixed_count = 0

    while not stop_signal.is_set():
        try:
            # Get task from queue (with timeout to check stop_signal)
            if task_queue.empty():
                logger.debug(f"Worker #{worker_id}: Queue empty, finishing")
                break

            msg_type, block_height = task_queue.get(timeout=1)

            if msg_type != 'gap':
                logger.warning(f"Worker #{worker_id}: Unexpected message type: {msg_type}")
                continue

            logger.info(f"Worker #{worker_id}: Fetching missing block {block_height}")

            # Fetch block by height
            block_data = fetch_block_by_height(block_height)

            if block_data is None:
                logger.error(f"Worker #{worker_id}: Failed to fetch block {block_height}")
                record_block_failed()
                continue

            # Process the block
            if process_block(block_data):
                fixed_count += 1
                record_gap_fixed()
                logger.info(f"Worker #{worker_id}: Fixed gap at block {block_height}")
            else:
                logger.warning(f"Worker #{worker_id}: Block {block_height} already processed or failed")

        except KeyboardInterrupt:
            logger.info(f"Worker #{worker_id}: Interrupted by user")
            break

        except Exception as e:
            logger.error(f"Worker #{worker_id}: Error processing gap: {e}")

    logger.info(f"Gap fixer worker #{worker_id} finished: {fixed_count} gaps fixed")
    return fixed_count


def fix_specific_gaps(block_heights: list) -> int:
    """
    Fix specific gaps given a list of block heights.
    Useful for standalone execution.

    Args:
        block_heights: List of block heights to fetch

    Returns:
        Number of blocks successfully fetched and processed
    """
    logger.info(f"Fixing {len(block_heights)} specific gaps...")

    fixed_count = 0

    with Timer(f"Fixing {len(block_heights)} gaps"):
        for block_height in block_heights:
            try:
                logger.info(f"Fetching block {block_height}")

                block_data = fetch_block_by_height(block_height)

                if block_data is None:
                    logger.error(f"Failed to fetch block {block_height}")
                    record_block_failed()
                    continue

                if process_block(block_data):
                    fixed_count += 1
                    record_gap_fixed()
                    logger.info(f"✓ Fixed gap at block {block_height}")
                else:
                    logger.warning(f"Block {block_height} already exists or processing failed")

            except Exception as e:
                logger.error(f"Error fixing block {block_height}: {e}")

    logger.info(f"Fixed {fixed_count}/{len(block_heights)} gaps")
    return fixed_count


def run_gap_fixer_standalone(gaps: Optional[list] = None):
    """
    Run gap fixer as standalone process (without multiprocessing).
    Useful for testing.

    Args:
        gaps: Optional list of block heights to fix (otherwise detect automatically)
    """
    from utils import detect_missing_blocks, get_all_processed_blocks

    logger.info("Running gap fixer in standalone mode")

    if gaps is None:
        # Auto-detect gaps
        logger.info("Auto-detecting gaps...")
        processed = get_all_processed_blocks()
        gaps = detect_missing_blocks(processed)

        if not gaps:
            logger.info("No gaps detected")
            return

        logger.info(f"Detected {len(gaps)} gaps")

    # Fix the gaps
    fixed = fix_specific_gaps(gaps)
    logger.info(f"Fixed {fixed} gaps")


if __name__ == '__main__':
    # Allow running as standalone script for testing
    import sys

    # Check for command-line arguments (block heights to fix)
    if len(sys.argv) > 1:
        # Parse block heights from command line
        try:
            gaps_to_fix = [int(arg) for arg in sys.argv[1:]]
            run_gap_fixer_standalone(gaps=gaps_to_fix)
        except ValueError:
            logger.error("Invalid block heights provided. Usage: python gap_fixer.py [block1] [block2] ...")
    else:
        # Auto-detect gaps
        run_gap_fixer_standalone()
