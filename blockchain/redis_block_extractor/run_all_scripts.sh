#!/bin/bash

#
# run_all_scripts.sh
#            
# This exercise uses the Redis data store to communicate between three scripts
# rather than using function calls.
#
# This script runs three python programs concurrently which, together, extract
# blockchain block files from an online API and loads them into a local 
# directory.
#

LOG_DIR="logs"
mkdir -p $LOG_DIR

SCRIPT_LOG="$LOG_DIR/script.log"
BLOCKS_EXTRACTOR=LOG_DIR/"blocks_extractor.log"
BLOCKS_EXTRACTOR=LOG_DIR/"blocks_dectector.log"
GAPS_FIXER=LOG_DIR/"GAPS_FIXER.log"

echo "Script started at $(date)" >> "$SCRIPT_LOG"

echo "blocks_extractor started at $(date)" >> "$SCRIPT_LOG"
python3 blocks_extractor.py >> "$LOG_DIR/blocks_exractor.log" 2>&1 &

echo "blocks_detector started at $(date)" >> "$SCRIPT_LOG"
python3 gaps_detector.py >> "$LOG_DIR/gaps_detector.log" 2>&1 &

echo "gaps_fixer started at $(date)" >> "$SCRIPT_LOG"
python3 gaps_fixer.py >> "$LOG_DIR/gaps_fixer.log" 2>&1 &

wait
echo "All scripts completed at $(date)" >> "$SCRIPT_LOG"
