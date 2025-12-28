#######################################################################################################################
#                                                                                                                     
#   File: gaps_dectortor.py                                                                                         
#   Author: Don Fox                                                                                                   
#   Date: 06/21/2024                                                                                                  
#                                                                                                                     
#   Description:                                                                                                      
#   This script scans the list 'blocks_collected' in the Redis store where the names of the block files downloaded 
#   so far is contained. Thes files have numeric strings as names and are sequential so any gaps in the list cam be 
#   detected. Any missing file are wrritten back to the Redis store 
#
#   Usage:                                                                                                            
#   - Ensure Redis is running and accessible.                                                                         
#   - This scropt should usually run concurrently with 'gaps_fixer.py' and 'blocks_extractor.py', but can be executed 
#     independntly.                   
#                                                                                                                     
#   Notes:
#   - This is one cof three Python3 scripts that run concurrently, the othger two being 'blocks_collector.py' and
#     'gaps_fixer.py'. They run concurrently and communicate via a common Redis store.                                                                                                   
#   - The script runs for 60 seconds, in that time the script scans the Redis 5 times or every 12 seconds.                                                                               
#   - Configure Redis connection parameters using environment variables (REDIS_HOST, REDIS_PORT, REDIS_DB).           
#                                                                                                                     
#######################################################################################################################
import signal
import sys
import redis
import logging
import time
import json
import os

# Timeout handler
def timeout_handler(signum, frame):
    print("Script timed out")
    sys.exit(0)

# Set a signal alarm for 60 seconds
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(60)

# Configure logger
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'gaps_detector.log')

logging.basicConfig(filename=log_file, filemode='a', 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize Redis client
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_db = int(os.getenv('REDIS_DB', 0))# Close the Redis connection
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)

def detect_gaps():
    logging.info("Detecting gaps in downloaded block_files...")

    try:
        redis_client.ping()
        print("Connected to Redis")
        logging.info("Connected to Redis")
    except redis.ConnectionError:
        print("Could not connect to Redis")
        logging.error("Could not connect to Redis")
        sys.exit(1)

    try:
        while True:
            try:
                # Fetch the list of block file names from Redis
                block_files = redis_client.lrange("blocks_collected", 0, -1)
                block_files = [int(block.decode('utf-8')) for block in block_files]
                block_files.sort()

                if len(block_files) < 2:
                    logging.info("Not enough block files to detect gaps.")
                    time.sleep(5)
                    continue

                # Detect gaps in the sequence
                gaps = []
                for i in range(len(block_files) - 1):
                    if block_files[i+1] != block_files[i] + 1:
                        gaps.extend(range(block_files[i] + 1, block_files[i+1]))

                if gaps:
                    logging.info(f"Gaps detected: {gaps}")
                    redis_client.set("gaps_detected", json.dumps(gaps))
                else:
                    logging.info("No gaps detected.")

                time.sleep(5)  # Wait for a while before checking again
            except Exception as e:
                logging.error(f"Error detecting gaps: {str(e)}")
                time.sleep(5)  # Wait before retrying

    finally:
        print("Disconnected from Redis")
        logging.info("Disconnected from Redis")
        redis_client.close()
        

if __name__ == "__main__":
    detect_gaps()
