#!/bin/bash
################################################################################
# Quickstart Script for Blockchain Indexer
#
# This script helps you get started quickly with the blockchain indexer.
# It sets up the environment, initializes the database, and runs a test batch.
#
# Usage:
#   ./quickstart.sh
#
# Author: Don Fox
# Date: 2025-12-09
################################################################################

set -e  # Exit on error

echo "============================================================================"
echo "Blockchain Indexer - Quickstart"
echo "============================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check Python version
echo -e "${YELLOW}[1/6] Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"
echo ""

# Step 2: Create virtual environment
echo -e "${YELLOW}[2/6] Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi
echo ""

# Step 3: Activate virtual environment and install dependencies
echo -e "${YELLOW}[3/6] Installing dependencies...${NC}"
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 4: Check PostgreSQL
echo -e "${YELLOW}[4/6] Checking PostgreSQL connection...${NC}"
if command -v psql &> /dev/null; then
    DB_NAME="${DB_NAME:-blockchain}"

    # Try to connect to database
    if psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        echo -e "${GREEN}✓ Database '$DB_NAME' found${NC}"

        # Ask if user wants to initialize schema
        read -p "Initialize/update database schema? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Initializing database schema..."
            psql -d "$DB_NAME" -f models/schema.sql > /dev/null 2>&1
            echo -e "${GREEN}✓ Database schema initialized${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Database '$DB_NAME' not found${NC}"
        read -p "Create database '$DB_NAME'? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            createdb "$DB_NAME"
            psql -d "$DB_NAME" -f models/schema.sql > /dev/null 2>&1
            echo -e "${GREEN}✓ Database created and initialized${NC}"
        else
            echo -e "${YELLOW}⚠ Skipping database setup. File storage will be used.${NC}"
            export ENABLE_DB_STORAGE=false
        fi
    fi
else
    echo -e "${YELLOW}⚠ PostgreSQL not found. File storage will be used.${NC}"
    export ENABLE_DB_STORAGE=false
fi
echo ""

# Step 5: Create necessary directories
echo -e "${YELLOW}[5/6] Creating directories...${NC}"
mkdir -p logs data/blocks
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Step 6: Run a test batch
echo -e "${YELLOW}[6/6] Running test batch...${NC}"
echo ""
echo "Starting blockchain indexer with:"
echo "  - Batch size: 10 blocks"
echo "  - Workers: 2"
echo "  - Gap detection: enabled"
echo ""
echo -e "${GREEN}Press Ctrl+C to stop at any time${NC}"
echo ""
sleep 2

# Run with small batch for testing
python main.py --batch-size 10 --workers 2

echo ""
echo "============================================================================"
echo -e "${GREEN}✓ Quickstart completed successfully!${NC}"
echo "============================================================================"
echo ""
echo "Next steps:"
echo "  1. Review the logs in logs/blockchain_indexer.log"
echo "  2. Check the data in PostgreSQL or data/blocks/"
echo "  3. Run full batch: python main.py --batch-size 100"
echo ""
echo "For more options: python main.py --help"
echo ""
