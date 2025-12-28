"""
********************************************************************************
block_collector.py -- Block Collector Service

Continuously fetches the latest blocks from the blockchain API and processes them.
Designed to run as an independent process in multiprocessing setup.

Features:
    - Fetches latest blocks at configured intervals
    - Deduplication (skips already processed blocks)
    - Shared queue for batch processing
    - Metrics tracking

Developed by: Don Fox
Date: 2025-12-09
********************************************************************************
"""
import time
import logging
from multiprocessing import Queue
from typing import Optional

import sys
sys.path.append('..')

from config import BLOCK_FETCH_DELAY, BATCH_SIZE
from utils import (
    fetch_latest_block,
    process_block,
    record_block_fetched,
    record_block_failed,
    Timer
)

logger = logging.getLogger(__name__)


def collect_blocks(task_queue: Queue, target_count: int, stop_signal) -> int:
    """
    Collect latest blocks and add to processing queue.

    Args:
        task_queue: Shared queue for blocks to process
        target_count: Number of unique blocks to collect
        stop_signal: Multiprocessing Event for graceful shutdown

    Returns:
        Number of blocks collected
    """
    logger.info(f"Block collector started (target: {target_count} blocks)")

    collected_count = 0
    consecutive_duplicates = 0
    max_duplicates = 10  # Stop after this many consecutive duplicates

    prev_block_height = None

    with Timer("Block collection"):
        while collected_count < target_count and not stop_signal.is_set():
            try:
                # Fetch latest block
                block_data = fetch_latest_block()

                if block_data is None:
                    logger.warning("Failed to fetch latest block, retrying...")
                    record_block_failed()
                    time.sleep(BLOCK_FETCH_DELAY * 2)  # Wait longer on failure
                    continue

                record_block_fetched()

                # Extract block height for deduplication
                block_height = block_data.get('block', {}).get('header', {}).get('height')

                if block_height is None:
                    logger.error("Block height missing, skipping")
                    continue

                block_height = int(block_height)

                # Skip if same as previous (blockchain hasn't progressed)
                if block_height == prev_block_height:
                    consecutive_duplicates += 1
                    logger.debug(f"Block {block_height} already seen, waiting for new block...")

                    # Stop if too many duplicates (blockchain not progressing)
                    if consecutive_duplicates >= max_duplicates:
                        logger.warning(
                            f"Blockchain not progressing after {max_duplicates} attempts, stopping collection"
                        )
                        break

                    time.sleep(BLOCK_FETCH_DELAY)
                    continue

                # New block found
                consecutive_duplicates = 0
                prev_block_height = block_height

                # Add to processing queue
                task_queue.put(('block', block_data))
                collected_count += 1

                logger.info(f"Collected block {block_height} ({collected_count}/{target_count})")

                # Delay before next fetch
                time.sleep(BLOCK_FETCH_DELAY)

            except KeyboardInterrupt:
                logger.info("Block collector interrupted by user")
                break

            except Exception as e:
                logger.error(f"Unexpected error in block collector: {e}")
                time.sleep(BLOCK_FETCH_DELAY)

    logger.info(f"Block collector finished: {collected_count} blocks collected")
    return collected_count


def run_collector_standalone(batch_size: Optional[int] = None):
    """
    Run block collector as standalone process (without multiprocessing).
    Useful for testing.

    Args:
        batch_size: Number of blocks to collect (default from config)
    """
    from multiprocessing import Queue, Event

    batch_size = batch_size or BATCH_SIZE
    task_queue = Queue()
    stop_signal = Event()

    logger.info("Running block collector in standalone mode")

    try:
        collected = collect_blocks(task_queue, batch_size, stop_signal)
        logger.info(f"Collected {collected} blocks")

        # Process all blocks in queue
        processed = 0
        while not task_queue.empty():
            msg_type, block_data = task_queue.get()
            if msg_type == 'block':
                if process_block(block_data):
                    processed += 1

        logger.info(f"Processed {processed} blocks")

    except KeyboardInterrupt:
        logger.info("Standalone collector interrupted")
        stop_signal.set()


if __name__ == '__main__':
    # Allow running as standalone script for testing
    run_collector_standalone()
