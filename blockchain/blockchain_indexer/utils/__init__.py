"""
utils package - Blockchain Indexer Utilities

Exposes all utility functions for easy importing.
"""

# Database utilities
from .db_utils import (
    initialize_connection_pool,
    close_connection_pool,
    get_db_connection,
    execute_query,
    batch_insert,
    insert_block,
    insert_transactions,
    get_processed_blocks,
    block_exists,
    get_latest_block_height,
    initialize_schema,
    get_database_stats
)

# Storage utilities
from .storage_utils import (
    get_block_file_path,
    save_block_to_file,
    load_block_from_file,
    block_file_exists,
    get_stored_block_heights,
    delete_block_file,
    batch_save_blocks,
    get_storage_stats,
    verify_file_integrity,
    cleanup_corrupted_files
)

# Block utilities
from .block_utils import (
    fetch_block_from_api,
    fetch_latest_block,
    fetch_block_by_height,
    parse_block_data,
    store_block,
    process_block,
    is_block_processed,
    get_all_processed_blocks,
    detect_missing_blocks,
    validate_block_data
)

# Metrics utilities
from .metrics import (
    initialize_metrics,
    get_metrics,
    increment_metric,
    set_metric,
    record_block_fetched,
    record_block_processed,
    record_block_failed,
    record_gap_detected,
    record_gap_fixed,
    record_api_failure,
    record_db_write,
    record_db_failure,
    record_file_write,
    record_file_failure,
    get_performance_stats,
    print_metrics_summary,
    check_database_health,
    check_api_health,
    run_health_checks,
    Timer,
    reset_metrics
)

__all__ = [
    # Database
    'initialize_connection_pool',
    'close_connection_pool',
    'get_db_connection',
    'execute_query',
    'batch_insert',
    'insert_block',
    'insert_transactions',
    'get_processed_blocks',
    'block_exists',
    'get_latest_block_height',
    'initialize_schema',
    'get_database_stats',
    # Storage
    'get_block_file_path',
    'save_block_to_file',
    'load_block_from_file',
    'block_file_exists',
    'get_stored_block_heights',
    'delete_block_file',
    'batch_save_blocks',
    'get_storage_stats',
    'verify_file_integrity',
    'cleanup_corrupted_files',
    # Block
    'fetch_block_from_api',
    'fetch_latest_block',
    'fetch_block_by_height',
    'parse_block_data',
    'store_block',
    'process_block',
    'is_block_processed',
    'get_all_processed_blocks',
    'detect_missing_blocks',
    'validate_block_data',
    # Metrics
    'initialize_metrics',
    'get_metrics',
    'increment_metric',
    'set_metric',
    'record_block_fetched',
    'record_block_processed',
    'record_block_failed',
    'record_gap_detected',
    'record_gap_fixed',
    'record_api_failure',
    'record_db_write',
    'record_db_failure',
    'record_file_write',
    'record_file_failure',
    'get_performance_stats',
    'print_metrics_summary',
    'check_database_health',
    'check_api_health',
    'run_health_checks',
    'Timer',
    'reset_metrics'
]
