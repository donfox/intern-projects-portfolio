# Blockchain Indexer

A production-ready blockchain block indexer that combines batch processing with multiprocessing for efficient block collection and gap detection.

## Overview

This project combines the best features from two previous implementations:
- **RESTful_indexer**: Clean modular architecture with database integration
- **redis_block_extractor**: Concurrent processing capabilities

The result is a hybrid system that:
- ✅ Processes blocks in configurable batches
- ✅ Uses Python multiprocessing (no Redis dependency)
- ✅ Supports dual storage (PostgreSQL + JSON files)
- ✅ Detects and fixes gaps in block sequences
- ✅ Provides comprehensive metrics and health checks
- ✅ Handles graceful shutdown
- ✅ Ensures idempotent processing

## Architecture

```
blockchain_indexer/
├── config.py              # Centralized configuration
├── main.py                # Batch job orchestrator
├── services/              # Independent service modules
│   ├── block_collector.py # Fetches latest blocks
│   ├── gap_detector.py    # Detects missing blocks
│   ├── gap_fixer.py       # Fetches missing blocks
│   └── block_processor.py # Processes & stores blocks
├── utils/                 # Shared utilities
│   ├── block_utils.py     # Block fetching/parsing
│   ├── db_utils.py        # PostgreSQL operations
│   ├── storage_utils.py   # File storage operations
│   └── metrics.py         # Observability & metrics
├── models/
│   └── schema.sql         # Database schema
├── logs/                  # Log files
└── data/blocks/           # Block files (if enabled)
```

## Features

### Core Capabilities
- **Batch Processing**: Configurable batch size for controlled execution
- **Multiprocessing**: Concurrent workers for parallel block fetching
- **Gap Detection**: Automatically finds and fixes missing blocks
- **Dual Storage**: Store blocks in PostgreSQL and/or JSON files
- **Idempotency**: Safely handles duplicate processing

### Reliability
- **Health Checks**: Validates database and API connectivity before execution
- **Retry Logic**: Exponential backoff for failed API requests
- **Graceful Shutdown**: Handles SIGINT/SIGTERM signals properly
- **Connection Pooling**: Efficient database connection management

### Observability
- **Metrics Tracking**: Detailed statistics on blocks, API calls, storage
- **Performance Monitoring**: Blocks/second, success rates
- **Comprehensive Logging**: File and console logging
- **Progress Reporting**: Real-time status updates

## Prerequisites

- Python 3.8+
- PostgreSQL 12+ (if using database storage)
- Internet connection (to fetch blocks from blockchain API)

## Installation

1. **Clone or navigate to the project:**
   ```bash
   cd blockchain_indexer
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup PostgreSQL database:**
   ```bash
   # Create database
   createdb blockchain

   # Initialize schema
   psql -d blockchain -f models/schema.sql
   ```

5. **Configure environment (optional):**
   ```bash
   # Create .env file or export variables
   export DB_NAME="blockchain"
   export DB_USER="your_username"
   export DB_PASSWORD="your_password"
   export DB_HOST="localhost"
   export DB_PORT="5432"
   ```

## Usage

### Basic Usage

Run a batch job to collect 100 blocks:

```bash
python main.py
```

### Advanced Options

```bash
# Collect specific number of blocks
python main.py --batch-size 500

# Use more workers for faster processing
python main.py --workers 8

# Skip gap detection phase
python main.py --skip-gaps

# Combine options
python main.py --batch-size 1000 --workers 8 --skip-gaps
```

### Configuration

Edit [config.py](config.py) or use environment variables:

```python
# Batch Processing
BATCH_SIZE = 100           # Number of blocks per batch
NUM_WORKERS = 4            # Number of worker processes
BLOCK_FETCH_DELAY = 0.5    # Delay between API requests (seconds)

# Storage Options
ENABLE_DB_STORAGE = True   # Store in PostgreSQL
ENABLE_FILE_STORAGE = True # Store as JSON files

# API Configuration
API_TIMEOUT = 12           # API request timeout
MAX_RETRIES = 3            # Max retry attempts
```

### Environment Variables

All configuration can be overridden with environment variables:

```bash
export BATCH_SIZE=500
export NUM_WORKERS=8
export ENABLE_FILE_STORAGE=false
export LOG_LEVEL=DEBUG
```

## Running Individual Services

Each service can run independently for testing:

### Block Collector
```bash
cd services
python block_collector.py
```

### Gap Detector
```bash
cd services
python gap_detector.py
```

### Gap Fixer
```bash
cd services
python gap_fixer.py           # Auto-detect gaps
python gap_fixer.py 100 101   # Fix specific blocks
```

## Database Queries

### View block summary:
```sql
SELECT * FROM block_summary LIMIT 10;
```

### Check for gaps:
```sql
SELECT * FROM detect_block_gaps();
```

### Get statistics:
```sql
SELECT get_total_blocks() AS total_blocks,
       get_total_transactions() AS total_transactions;
```

## Logging

Logs are written to:
- `logs/blockchain_indexer.log` - Main application log
- Console output (stdout)

Configure log level:
```bash
export LOG_LEVEL=DEBUG  # Options: DEBUG, INFO, WARNING, ERROR
```

## Metrics

The system tracks comprehensive metrics:

- **Processing**: Blocks fetched, processed, failed
- **Gaps**: Detected and fixed
- **API**: Request count, failures, success rate
- **Storage**: Database/file writes, failures
- **Performance**: Blocks/second, elapsed time

View metrics summary at the end of each batch job.

## Troubleshooting

### Database Connection Errors
```bash
# Check PostgreSQL is running
pg_isready

# Verify connection settings
psql -d blockchain -U your_username
```

### API Timeout Issues
```bash
# Increase timeout in config.py
API_TIMEOUT = 30

# Or via environment variable
export API_TIMEOUT=30
```

### Import Errors
```bash
# Ensure you're in the project directory
cd blockchain_indexer

# Run from project root
python main.py
```

## Development

### Project Structure

- **config.py**: All configuration settings
- **main.py**: Orchestrator with multiprocessing
- **services/**: Independent service modules
- **utils/**: Shared utility functions
- **models/**: Database schema

### Adding New Features

1. Utilities go in `utils/`
2. Services go in `services/`
3. Update `config.py` for new settings
4. Add to `__init__.py` files for imports

### Testing

Run individual services in standalone mode:
```bash
python -m services.block_collector
python -m services.gap_detector
python -m services.gap_fixer
```

## Performance Tuning

### Optimize for Speed
```bash
python main.py --batch-size 1000 --workers 16
export BLOCK_FETCH_DELAY=0.1
export ENABLE_FILE_STORAGE=false  # DB only
```

### Optimize for Reliability
```bash
export MAX_RETRIES=5
export API_TIMEOUT=30
export BLOCK_FETCH_DELAY=1.0
```

### Optimize for Storage
```bash
export ENABLE_DB_STORAGE=false    # Files only
export PRETTY_PRINT_JSON=false    # Minified JSON
```

## Key Improvements Over Previous Versions

### vs. redis_block_extractor
- ✅ No Redis dependency (simpler deployment)
- ✅ Better error handling and retry logic
- ✅ Database storage option
- ✅ Configurable batch processing
- ✅ Comprehensive metrics

### vs. RESTful_indexer
- ✅ Multiprocessing for parallel execution
- ✅ Batch job model (vs continuous)
- ✅ Independent service modules
- ✅ File storage option
- ✅ Gap detection and fixing

## License

Developed by Don Fox - 2025

## Support

For issues or questions:
1. Check the logs in `logs/blockchain_indexer.log`
2. Run health checks: `python -c "from utils import run_health_checks; run_health_checks()"`
3. Review configuration in `config.py`

## Future Enhancements

Possible improvements:
- [ ] Docker containerization
- [ ] Kubernetes deployment manifests
- [ ] REST API for status monitoring
- [ ] Prometheus metrics export
- [ ] Unit and integration tests
- [ ] Block validation and verification
- [ ] Historical data backfilling tool
