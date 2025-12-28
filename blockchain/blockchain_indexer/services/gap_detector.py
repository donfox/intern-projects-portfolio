"""
********************************************************************************
gap_detector.py -- Gap Detector Service

Detects gaps (missing blocks) in the sequence of processed blocks.
Adds missing block numbers to the task queue for gap_fixer to process.

Features:
    - Scans all processed blocks for sequence gaps
    - Respects MAX_GAPS_TO_FIX limit
    - Can run as independent process
    - Metrics tracking

Developed by: Don Fox
Date: 2025-12-09
********************************************************************************
"""
import logging
from multiprocessing import Queue
from typing import List

import sys
sys.path.append('..')

from config import MAX_GAPS_TO_FIX
from utils import (
    get_all_processed_blocks,
    detect_missing_blocks,
    record_gap_detected,
    Timer
)

logger = logging.getLogger(__name__)


def find_and_queue_gaps(task_queue: Queue) -> int:
    """
    Find missing blocks and add them to the task queue.

    Args:
        task_queue: Shared queue for gap block numbers

    Returns:
        Number of gaps detected and queued
    """
    logger.info("Scanning for gaps in processed blocks...")

    with Timer("Gap detection"):
        # Get all processed blocks
        processed_blocks = get_all_processed_blocks()

        if len(processed_blocks) < 2:
            logger.info("Not enough blocks to detect gaps")
            return 0

        logger.info(f"Checking {len(processed_blocks)} blocks for gaps...")
        logger.info(f"Block range: {processed_blocks[0]} to {processed_blocks[-1]}")

        # Detect gaps
        missing_blocks = detect_missing_blocks(processed_blocks)

        if not missing_blocks:
            logger.info("✓ No gaps detected - all blocks sequential")
            return 0

        # Apply limit
        gaps_to_fix = missing_blocks[:MAX_GAPS_TO_FIX]
        total_gaps = len(missing_blocks)

        if total_gaps > MAX_GAPS_TO_FIX:
            logger.warning(
                f"Detected {total_gaps} gaps, but limiting to {MAX_GAPS_TO_FIX} "
                f"(adjust MAX_GAPS_TO_FIX to process more)"
            )
        else:
            logger.info(f"Detected {total_gaps} gaps to fix")

        # Queue gaps for fixing
        for block_height in gaps_to_fix:
            task_queue.put(('gap', block_height))

        record_gap_detected(len(gaps_to_fix))

        # Log gap ranges for visibility
        log_gap_ranges(gaps_to_fix)

        logger.info(f"Queued {len(gaps_to_fix)} missing blocks for retrieval")
        return len(gaps_to_fix)


def log_gap_ranges(missing_blocks: List[int], max_ranges: int = 10):
    """
    Log gap ranges in a readable format.

    Args:
        missing_blocks: List of missing block heights
        max_ranges: Maximum number of ranges to log
    """
    if not missing_blocks:
        return

    ranges = []
    range_start = missing_blocks[0]
    range_end = missing_blocks[0]

    for i in range(1, len(missing_blocks)):
        if missing_blocks[i] == range_end + 1:
            # Continuous range
            range_end = missing_blocks[i]
        else:
            # Gap in sequence, save current range
            if range_start == range_end:
                ranges.append(str(range_start))
            else:
                ranges.append(f"{range_start}-{range_end}")

            range_start = missing_blocks[i]
            range_end = missing_blocks[i]

    # Add final range
    if range_start == range_end:
        ranges.append(str(range_start))
    else:
        ranges.append(f"{range_start}-{range_end}")

    # Log ranges (limit output)
    if len(ranges) <= max_ranges:
        logger.info(f"Gap ranges: {', '.join(ranges)}")
    else:
        displayed = ', '.join(ranges[:max_ranges])
        logger.info(f"Gap ranges (first {max_ranges}): {displayed} ... and {len(ranges) - max_ranges} more")


def run_gap_detection_standalone():
    """
    Run gap detection as standalone process (without multiprocessing).
    Useful for testing.
    """
    from multiprocessing import Queue

    task_queue = Queue()

    logger.info("Running gap detection in standalone mode")

    gaps_found = find_and_queue_gaps(task_queue)
    logger.info(f"Found {gaps_found} gaps")

    # Display queued gaps
    if gaps_found > 0:
        gaps = []
        while not task_queue.empty():
            msg_type, block_height = task_queue.get()
            if msg_type == 'gap':
                gaps.append(block_height)

        logger.info(f"Missing blocks: {gaps[:20]}{'...' if len(gaps) > 20 else ''}")


if __name__ == '__main__':
    # Allow running as standalone script for testing
    run_gap_detection_standalone()
