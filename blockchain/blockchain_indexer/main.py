"""
********************************************************************************
main.py -- Blockchain Indexer Main Orchestrator

Batch job orchestrator that coordinates all services using multiprocessing.
Supports configurable deployment modes and graceful shutdown.

Features:
    - Multiprocessing architecture with worker pools
    - Graceful shutdown handling (SIGINT, SIGTERM)
    - Health checks before execution
    - Comprehensive metrics and reporting
    - Gap detection and fixing
    - Dual storage (database + files)

Usage:
    python main.py [--batch-size N] [--workers N] [--skip-gaps]

Developed by: Don Fox
Date: 2025-12-09
********************************************************************************
"""
import sys
import signal
import logging
import argparse
from multiprocessing import Process, Queue, Event, Manager
from typing import List

from config import (
    BATCH_SIZE,
    NUM_WORKERS,
    RUN_GAP_DETECTION,
    SHUTDOWN_TIMEOUT,
    ENABLE_DB_STORAGE,
    ENABLE_METRICS
)

from utils import (
    initialize_schema,
    initialize_connection_pool,
    close_connection_pool,
    initialize_metrics,
    print_metrics_summary,
    run_health_checks,
    get_database_stats,
    get_storage_stats,
    Timer
)

from services import (
    collect_blocks,
    find_and_queue_gaps,
    fix_gaps_from_queue,
    process_blocks_from_queue
)

logger = logging.getLogger(__name__)

# Global stop signal for graceful shutdown
stop_signal = None


def signal_handler(signum, frame):
    """Handle shutdown signals (SIGINT, SIGTERM) gracefully."""
    global stop_signal

    signal_name = 'SIGINT' if signum == signal.SIGINT else 'SIGTERM'
    logger.info(f"\n{signal_name} received, initiating graceful shutdown...")

    if stop_signal:
        stop_signal.set()


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    logger.info("Signal handlers registered")


def initialize_system():
    """Initialize system components (database, metrics, etc.)."""
    logger.info("=" * 80)
    logger.info("BLOCKCHAIN INDEXER - INITIALIZATION")
    logger.info("=" * 80)

    # Initialize database schema
    if ENABLE_DB_STORAGE:
        try:
            logger.info("Initializing database schema...")
            initialize_schema()
            initialize_connection_pool(min_conn=1, max_conn=NUM_WORKERS + 2)
            logger.info("✓ Database initialized")
        except Exception as e:
            logger.error(f"✗ Database initialization failed: {e}")
            sys.exit(1)

    # Initialize metrics
    if ENABLE_METRICS:
        logger.info("Initializing metrics...")
        initialize_metrics()
        logger.info("✓ Metrics initialized")

    logger.info("=" * 80)


def run_health_checks_startup():
    """Run health checks before starting batch job."""
    logger.info("\n" + "=" * 80)
    logger.info("RUNNING HEALTH CHECKS")
    logger.info("=" * 80)

    results = run_health_checks()

    if not all(results.values()):
        logger.error("✗ Health checks failed, aborting startup")
        logger.error(f"Results: {results}")
        sys.exit(1)

    logger.info("✓ All health checks passed")
    logger.info("=" * 80 + "\n")


def run_gap_detection_phase(task_queue: Queue):
    """Run gap detection phase if enabled."""
    if not RUN_GAP_DETECTION:
        logger.info("Gap detection disabled, skipping")
        return 0

    logger.info("\n" + "=" * 80)
    logger.info("PHASE 1: GAP DETECTION")
    logger.info("=" * 80)

    with Timer("Gap detection phase"):
        gaps_found = find_and_queue_gaps(task_queue)

    logger.info("=" * 80 + "\n")
    return gaps_found


def run_block_collection_phase(task_queue: Queue, batch_size: int, stop_signal: Event):
    """Run block collection phase with multiprocessing."""
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 2: BLOCK COLLECTION")
    logger.info("=" * 80)
    logger.info(f"Target: {batch_size} blocks")
    logger.info(f"Workers: {NUM_WORKERS}")
    logger.info("=" * 80 + "\n")

    with Timer("Block collection phase"):
        # Start collector process
        collector = Process(
            target=collect_blocks,
            args=(task_queue, batch_size, stop_signal),
            name="BlockCollector"
        )
        collector.start()

        # Wait for collector to finish
        collector.join(timeout=SHUTDOWN_TIMEOUT)

        if collector.is_alive():
            logger.warning("Collector didn't finish in time, terminating...")
            collector.terminate()
            collector.join()

    logger.info("\n" + "=" * 80)
    logger.info("Block collection phase completed")
    logger.info("=" * 80 + "\n")


def run_processing_phase(task_queue: Queue, stop_signal: Event, num_workers: int):
    """Run block processing phase with worker pool."""
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 3: BLOCK PROCESSING")
    logger.info("=" * 80)
    logger.info(f"Processing workers: {num_workers}")
    logger.info("=" * 80 + "\n")

    with Timer("Block processing phase"):
        # Start processor workers
        processors: List[Process] = []

        for i in range(num_workers):
            p = Process(
                target=process_blocks_from_queue,
                args=(task_queue, stop_signal, i),
                name=f"BlockProcessor-{i}"
            )
            p.start()
            processors.append(p)

        # Wait for all processors to finish
        for p in processors:
            p.join(timeout=SHUTDOWN_TIMEOUT)

            if p.is_alive():
                logger.warning(f"Processor {p.name} didn't finish, terminating...")
                p.terminate()
                p.join()

    logger.info("\n" + "=" * 80)
    logger.info("Block processing phase completed")
    logger.info("=" * 80 + "\n")


def print_final_statistics():
    """Print final statistics and metrics."""
    logger.info("\n" + "=" * 80)
    logger.info("FINAL STATISTICS")
    logger.info("=" * 80)

    # Database stats
    if ENABLE_DB_STORAGE:
        db_stats = get_database_stats()
        logger.info(f"\n📊 Database Statistics:")
        logger.info(f"  Total Blocks:       {db_stats['total_blocks']}")
        logger.info(f"  Total Transactions: {db_stats['total_transactions']}")
        logger.info(f"  Earliest Block:     {db_stats['earliest_block']}")
        logger.info(f"  Latest Block:       {db_stats['latest_block']}")

    # File storage stats
    from config import ENABLE_FILE_STORAGE
    if ENABLE_FILE_STORAGE:
        file_stats = get_storage_stats()
        logger.info(f"\n📁 File Storage Statistics:")
        logger.info(f"  Total Files:        {file_stats['total_files']}")
        logger.info(f"  Total Size:         {file_stats['total_size_mb']} MB")
        logger.info(f"  Earliest Block:     {file_stats['earliest_block']}")
        logger.info(f"  Latest Block:       {file_stats['latest_block']}")

    # Metrics summary
    if ENABLE_METRICS:
        print_metrics_summary()


def main(batch_size: int = None, num_workers: int = None, skip_gaps: bool = False):
    """
    Main entry point for the blockchain indexer batch job.

    Args:
        batch_size: Number of blocks to collect (default from config)
        num_workers: Number of worker processes (default from config)
        skip_gaps: Skip gap detection phase
    """
    global stop_signal

    # Use config values if not provided
    batch_size = batch_size or BATCH_SIZE
    num_workers = num_workers or NUM_WORKERS

    logger.info("\n" + "=" * 80)
    logger.info("BLOCKCHAIN INDEXER STARTING")
    logger.info("=" * 80)
    logger.info(f"Batch Size: {batch_size}")
    logger.info(f"Workers: {num_workers}")
    logger.info(f"Gap Detection: {'Enabled' if not skip_gaps else 'Disabled'}")
    logger.info("=" * 80 + "\n")

    # Setup
    setup_signal_handlers()
    initialize_system()
    run_health_checks_startup()

    # Create shared resources
    manager = Manager()
    task_queue = manager.Queue()
    stop_signal = manager.Event()

    try:
        # Phase 1: Gap Detection (optional)
        if not skip_gaps:
            gaps_found = run_gap_detection_phase(task_queue)
            logger.info(f"Gaps queued for processing: {gaps_found}")

        # Phase 2: Block Collection
        run_block_collection_phase(task_queue, batch_size, stop_signal)

        # Phase 3: Block Processing
        logger.info(f"Queue size before processing: {task_queue.qsize()}")
        run_processing_phase(task_queue, stop_signal, num_workers)

        # Final statistics
        print_final_statistics()

        logger.info("\n" + "=" * 80)
        logger.info("✓ BLOCKCHAIN INDEXER COMPLETED SUCCESSFULLY")
        logger.info("=" * 80 + "\n")

    except KeyboardInterrupt:
        logger.info("\n\nBatch job interrupted by user")
        stop_signal.set()

    except Exception as e:
        logger.error(f"\n\nFatal error: {e}", exc_info=True)
        stop_signal.set()
        sys.exit(1)

    finally:
        # Cleanup
        logger.info("Cleaning up resources...")

        if ENABLE_DB_STORAGE:
            close_connection_pool()

        logger.info("Cleanup complete")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Blockchain Indexer - Batch block processing system"
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=None,
        help=f'Number of blocks to collect (default: {BATCH_SIZE})'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=None,
        help=f'Number of worker processes (default: {NUM_WORKERS})'
    )

    parser.add_argument(
        '--skip-gaps',
        action='store_true',
        help='Skip gap detection phase'
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()

    main(
        batch_size=args.batch_size,
        num_workers=args.workers,
        skip_gaps=args.skip_gaps
    )
