"""
********************************************************************************
config.py -- Blockchain Indexer Configuration

Centralized configuration for the blockchain indexer system.
Supports batch processing with flexible storage options (database and/or files).

Features:
    - Environment variable support with sensible defaults
    - Database configuration (PostgreSQL)
    - Blockchain API endpoints
    - Processing parameters (batch size, workers, timeouts)
    - Storage options (dual storage: DB + files)
    - Logging configuration

Developed by: Don Fox
Date: 2025-12-09
********************************************************************************
"""
import os
import logging
from pathlib import Path

# ============================================================================
# PROJECT PATHS
# ============================================================================
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data" / "blocks"

# Create directories if they don't exist
LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOGS_DIR / "blockchain_indexer.log"),
        logging.StreamHandler()  # Also log to console
    ]
)

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DB_CONFIG = {
    "database": os.getenv("DB_NAME", "blockchain"),
    "user": os.getenv("DB_USER", "donfox1"),
    "password": os.getenv("DB_PASSWORD", "xofnod"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432"))
}

# ============================================================================
# BLOCKCHAIN API CONFIGURATION
# ============================================================================
# Primary API endpoint for latest blocks
LATEST_BLOCK_URL = os.getenv(
    "LATEST_BLOCK_URL",
    "https://migaloo-api.polkachu.com/cosmos/base/tendermint/v1beta1/blocks/latest"
)

# Template for fetching specific block by height
BLOCK_URL_TEMPLATE = os.getenv(
    "BLOCK_URL_TEMPLATE",
    "https://migaloo-api.polkachu.com/cosmos/base/tendermint/v1beta1/blocks/{}"
)

# API request timeout in seconds
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "12"))

# ============================================================================
# BATCH PROCESSING CONFIGURATION
# ============================================================================
# Number of blocks to fetch per batch job
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))

# Number of worker processes for concurrent block fetching
NUM_WORKERS = int(os.getenv("NUM_WORKERS", "4"))

# Delay between block fetch attempts (seconds)
BLOCK_FETCH_DELAY = float(os.getenv("BLOCK_FETCH_DELAY", "0.5"))

# Maximum retries for failed block fetches
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Retry backoff multiplier (exponential backoff)
RETRY_BACKOFF = float(os.getenv("RETRY_BACKOFF", "2.0"))

# ============================================================================
# STORAGE CONFIGURATION
# ============================================================================
# Enable/disable file storage (in addition to database)
ENABLE_FILE_STORAGE = os.getenv("ENABLE_FILE_STORAGE", "true").lower() == "true"

# Enable/disable database storage
ENABLE_DB_STORAGE = os.getenv("ENABLE_DB_STORAGE", "true").lower() == "true"

# Add .json extension to block files
ADD_JSON_EXTENSION = os.getenv("ADD_JSON_EXTENSION", "false").lower() == "true"

# Pretty-print JSON files (vs minified)
PRETTY_PRINT_JSON = os.getenv("PRETTY_PRINT_JSON", "true").lower() == "true"

# ============================================================================
# OBSERVABILITY CONFIGURATION
# ============================================================================
# Enable metrics collection
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"

# Metrics reporting interval (seconds)
METRICS_INTERVAL = int(os.getenv("METRICS_INTERVAL", "30"))

# Enable health checks
ENABLE_HEALTH_CHECKS = os.getenv("ENABLE_HEALTH_CHECKS", "true").lower() == "true"

# ============================================================================
# GAP DETECTION CONFIGURATION
# ============================================================================
# Run gap detection before batch processing
RUN_GAP_DETECTION = os.getenv("RUN_GAP_DETECTION", "true").lower() == "true"

# Maximum number of gaps to fix in one batch
MAX_GAPS_TO_FIX = int(os.getenv("MAX_GAPS_TO_FIX", "1000"))

# ============================================================================
# GRACEFUL SHUTDOWN CONFIGURATION
# ============================================================================
# Shutdown timeout (seconds) - how long to wait for processes to finish
SHUTDOWN_TIMEOUT = int(os.getenv("SHUTDOWN_TIMEOUT", "30"))

# ============================================================================
# VALIDATION
# ============================================================================
if not ENABLE_DB_STORAGE and not ENABLE_FILE_STORAGE:
    raise ValueError("At least one storage method (DB or File) must be enabled!")

# Log configuration on startup
logger = logging.getLogger(__name__)
logger.info("=" * 80)
logger.info("Blockchain Indexer Configuration Loaded")
logger.info("=" * 80)
logger.info(f"Batch Size: {BATCH_SIZE}")
logger.info(f"Workers: {NUM_WORKERS}")
logger.info(f"Database Storage: {'Enabled' if ENABLE_DB_STORAGE else 'Disabled'}")
logger.info(f"File Storage: {'Enabled' if ENABLE_FILE_STORAGE else 'Disabled'}")
logger.info(f"Gap Detection: {'Enabled' if RUN_GAP_DETECTION else 'Disabled'}")
logger.info(f"Metrics: {'Enabled' if ENABLE_METRICS else 'Disabled'}")
logger.info("=" * 80)
