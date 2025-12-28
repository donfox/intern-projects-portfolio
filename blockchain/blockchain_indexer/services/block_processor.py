"""
********************************************************************************
block_processor.py -- Block Processor Service

Processes blocks from the task queue and stores them.
Handles both new blocks from collector and gap blocks from fixer.

Features:
    - Processes blocks from shared queue
    - Supports multiple worker processes
    - Idempotent processing (skips duplicates)
    - Metrics tracking

Developed by: Don Fox
Date: 2025-12-09
********************************************************************************
"""
import logging
from multiprocessing import Queue
import queue

import sys
sys.path.append('..')

from utils import (
    process_block,
    fetch_block_by_height,
    record_block_processed,
    record_block_failed,
    Timer
)

logger = logging.getLogger(__name__)


def process_blocks_from_queue(task_queue: Queue, stop_signal, worker_id: int = 0) -> int:
    """
    Process blocks from the shared task queue.

    Args:
        task_queue: Shared queue containing messages:
                    - ('block', block_data) for new blocks
                    - ('gap', block_height) for missing blocks
        stop_signal: Multiprocessing Event for graceful shutdown
        worker_id: Worker identifier for logging

    Returns:
        Number of blocks successfully processed
    """
    logger.info(f"Block processor worker #{worker_id} started")

    processed_count = 0

    while not stop_signal.is_set():
        try:
            # Get task from queue (timeout to check stop_signal periodically)
            try:
                message = task_queue.get(timeout=1)
            except queue.Empty:
                # Check if there are more tasks coming
                continue

            msg_type, data = message

            if msg_type == 'block':
                # Process block data directly
                block_data = data

                if process_block(block_data):
                    processed_count += 1
                    record_block_processed()

                    block_height = block_data.get('block', {}).get('header', {}).get('height')
                    logger.info(f"Worker #{worker_id}: Processed block {block_height}")
                else:
                    logger.debug(f"Worker #{worker_id}: Block already processed or failed")

            elif msg_type == 'gap':
                # Fetch and process gap block by height
                block_height = data

                logger.info(f"Worker #{worker_id}: Fetching gap block {block_height}")

                block_data = fetch_block_by_height(block_height)

                if block_data is None:
                    logger.error(f"Worker #{worker_id}: Failed to fetch gap block {block_height}")
                    record_block_failed()
                    continue

                if process_block(block_data):
                    processed_count += 1
                    record_block_processed()
                    logger.info(f"Worker #{worker_id}: Processed gap block {block_height}")
                else:
                    logger.debug(f"Worker #{worker_id}: Gap block {block_height} already processed")

            elif msg_type == 'stop':
                # Stop signal received
                logger.info(f"Worker #{worker_id}: Stop signal received")
                break

            else:
                logger.warning(f"Worker #{worker_id}: Unknown message type: {msg_type}")

        except KeyboardInterrupt:
            logger.info(f"Worker #{worker_id}: Interrupted by user")
            break

        except Exception as e:
            logger.error(f"Worker #{worker_id}: Error processing block: {e}")
            record_block_failed()

    logger.info(f"Block processor worker #{worker_id} finished: {processed_count} blocks processed")
    return processed_count


def run_processor_standalone():
    """
    Run block processor as standalone process (without multiprocessing).
    Useful for testing.
    """
    from multiprocessing import Queue, Event
    from utils import fetch_latest_block

    logger.info("Running block processor in standalone mode")

    task_queue = Queue()
    stop_signal = Event()

    # Add some test blocks to queue
    logger.info("Fetching test blocks...")
    for i in range(5):
        block_data = fetch_latest_block()
        if block_data:
            task_queue.put(('block', block_data))

    # Process them
    processed = process_blocks_from_queue(task_queue, stop_signal, worker_id=0)
    logger.info(f"Processed {processed} blocks")


if __name__ == '__main__':
    # Allow running as standalone script for testing
    run_processor_standalone()
