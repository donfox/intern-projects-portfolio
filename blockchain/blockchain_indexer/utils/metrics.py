"""
********************************************************************************
metrics.py -- Observability & Metrics

Provides metrics collection, health checks, and performance monitoring
for the blockchain indexer.

Features:
    - Process-safe metrics using multiprocessing Manager
    - Performance tracking (blocks/sec, requests/sec)
    - Health checks for database and API
    - Summary reports

Developed by: Don Fox
Date: 2025-12-09
********************************************************************************
"""
import time
import logging
from typing import Dict
from datetime import datetime
from multiprocessing import Manager
from config import ENABLE_METRICS

logger = logging.getLogger(__name__)

# Shared metrics dictionary (process-safe)
_metrics_manager = None
_metrics = None


def initialize_metrics():
    """Initialize shared metrics dictionary for multiprocessing."""
    global _metrics_manager, _metrics

    if _metrics_manager is None:
        _metrics_manager = Manager()
        _metrics = _metrics_manager.dict({
            'blocks_fetched': 0,
            'blocks_processed': 0,
            'blocks_failed': 0,
            'gaps_detected': 0,
            'gaps_fixed': 0,
            'api_requests': 0,
            'api_failures': 0,
            'db_writes': 0,
            'db_failures': 0,
            'file_writes': 0,
            'file_failures': 0,
            'start_time': time.time(),
            'total_processing_time': 0.0
        })
        logger.info("Metrics initialized")


def get_metrics() -> Dict:
    """Get current metrics snapshot."""
    if _metrics is None:
        initialize_metrics()
    return dict(_metrics)


def increment_metric(metric_name: str, value: int = 1):
    """
    Increment a metric counter.

    Args:
        metric_name: Name of the metric
        value: Amount to increment by (default 1)
    """
    if not ENABLE_METRICS:
        return

    if _metrics is None:
        initialize_metrics()

    if metric_name in _metrics:
        _metrics[metric_name] = _metrics[metric_name] + value
    else:
        logger.warning(f"Unknown metric: {metric_name}")


def set_metric(metric_name: str, value):
    """
    Set a metric to a specific value.

    Args:
        metric_name: Name of the metric
        value: Value to set
    """
    if not ENABLE_METRICS:
        return

    if _metrics is None:
        initialize_metrics()

    _metrics[metric_name] = value


def record_block_fetched():
    """Record that a block was fetched from API."""
    increment_metric('blocks_fetched')
    increment_metric('api_requests')


def record_block_processed():
    """Record that a block was successfully processed."""
    increment_metric('blocks_processed')


def record_block_failed():
    """Record that a block processing failed."""
    increment_metric('blocks_failed')


def record_gap_detected(count: int = 1):
    """Record gap(s) detected."""
    increment_metric('gaps_detected', count)


def record_gap_fixed():
    """Record that a gap was fixed."""
    increment_metric('gaps_fixed')


def record_api_failure():
    """Record API request failure."""
    increment_metric('api_failures')


def record_db_write():
    """Record database write."""
    increment_metric('db_writes')


def record_db_failure():
    """Record database write failure."""
    increment_metric('db_failures')


def record_file_write():
    """Record file write."""
    increment_metric('file_writes')


def record_file_failure():
    """Record file write failure."""
    increment_metric('file_failures')


def get_performance_stats() -> Dict:
    """
    Calculate performance statistics.

    Returns:
        Dictionary with performance metrics
    """
    metrics = get_metrics()
    elapsed_time = time.time() - metrics.get('start_time', time.time())

    stats = {
        'elapsed_time_seconds': round(elapsed_time, 2),
        'blocks_per_second': 0.0,
        'api_success_rate': 0.0,
        'db_success_rate': 0.0,
        'file_success_rate': 0.0
    }

    # Blocks per second
    if elapsed_time > 0:
        stats['blocks_per_second'] = round(
            metrics.get('blocks_processed', 0) / elapsed_time, 2
        )

    # API success rate
    total_api = metrics.get('api_requests', 0)
    if total_api > 0:
        failed_api = metrics.get('api_failures', 0)
        stats['api_success_rate'] = round(
            ((total_api - failed_api) / total_api) * 100, 2
        )

    # DB success rate
    total_db = metrics.get('db_writes', 0)
    if total_db > 0:
        failed_db = metrics.get('db_failures', 0)
        stats['db_success_rate'] = round(
            ((total_db - failed_db) / total_db) * 100, 2
        )

    # File success rate
    total_file = metrics.get('file_writes', 0)
    if total_file > 0:
        failed_file = metrics.get('file_failures', 0)
        stats['file_success_rate'] = round(
            ((total_file - failed_file) / total_file) * 100, 2
        )

    return stats


def print_metrics_summary():
    """Print a formatted summary of metrics."""
    if not ENABLE_METRICS:
        return

    metrics = get_metrics()
    perf = get_performance_stats()

    print("\n" + "=" * 80)
    print("BLOCKCHAIN INDEXER - METRICS SUMMARY")
    print("=" * 80)

    print(f"\n📊 Processing Statistics:")
    print(f"  Blocks Fetched:     {metrics.get('blocks_fetched', 0)}")
    print(f"  Blocks Processed:   {metrics.get('blocks_processed', 0)}")
    print(f"  Blocks Failed:      {metrics.get('blocks_failed', 0)}")
    print(f"  Gaps Detected:      {metrics.get('gaps_detected', 0)}")
    print(f"  Gaps Fixed:         {metrics.get('gaps_fixed', 0)}")

    print(f"\n🌐 API Statistics:")
    print(f"  Total Requests:     {metrics.get('api_requests', 0)}")
    print(f"  Failed Requests:    {metrics.get('api_failures', 0)}")
    print(f"  Success Rate:       {perf['api_success_rate']}%")

    print(f"\n💾 Storage Statistics:")
    print(f"  Database Writes:    {metrics.get('db_writes', 0)}")
    print(f"  Database Failures:  {metrics.get('db_failures', 0)}")
    print(f"  File Writes:        {metrics.get('file_writes', 0)}")
    print(f"  File Failures:      {metrics.get('file_failures', 0)}")

    print(f"\n⚡ Performance:")
    print(f"  Elapsed Time:       {perf['elapsed_time_seconds']}s")
    print(f"  Blocks/Second:      {perf['blocks_per_second']}")

    print("=" * 80 + "\n")


def check_database_health() -> bool:
    """
    Check if database is accessible.

    Returns:
        True if healthy, False otherwise
    """
    try:
        from .db_utils import get_db_connection

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

        logger.info("✓ Database health check passed")
        return True

    except Exception as e:
        logger.error(f"✗ Database health check failed: {e}")
        return False


def check_api_health() -> bool:
    """
    Check if blockchain API is accessible.

    Returns:
        True if healthy, False otherwise
    """
    try:
        import requests
        from config import LATEST_BLOCK_URL, API_TIMEOUT

        response = requests.get(LATEST_BLOCK_URL, timeout=API_TIMEOUT)
        response.raise_for_status()

        logger.info("✓ API health check passed")
        return True

    except Exception as e:
        logger.error(f"✗ API health check failed: {e}")
        return False


def run_health_checks() -> Dict[str, bool]:
    """
    Run all health checks.

    Returns:
        Dictionary with health check results
    """
    logger.info("Running health checks...")

    results = {
        'database': check_database_health(),
        'api': check_api_health()
    }

    all_healthy = all(results.values())

    if all_healthy:
        logger.info("✓ All health checks passed")
    else:
        logger.warning("✗ Some health checks failed")

    return results


class Timer:
    """Context manager for timing code blocks."""

    def __init__(self, name: str = "operation"):
        self.name = name
        self.start_time = None
        self.elapsed = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        self.elapsed = time.time() - self.start_time
        logger.debug(f"{self.name} took {self.elapsed:.2f}s")


def reset_metrics():
    """Reset all metrics to initial state."""
    if _metrics is not None:
        _metrics.clear()
        initialize_metrics()
        logger.info("Metrics reset")
