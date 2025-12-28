#######################################################################################################################
#                                                                                                                     
#   File: blocks_extractor.py                                                                                         
#   Author: Don Fox                                                                                                   
#   Date: 06/21/2024                                                                                                  
#                                                                                                                     
#   Description: 
#                                                                                                      
#   This script extracts blockchain block files from an online source using RESTful requests, transforms them into JSON 
#   format and stores them locally. The names of the collected file names are written to a Redis as the 
#   'blocks_collected' list and written to the 'blocks_collector.log'.
#
#   The function in this script uses redis datastore to provide data for 'detect_gaps()' in 'gaps_detector.py' 
#
#   Usage:                                                                                                            
#   - Ensure Redis is running and accessible.                                                                         
#   - This scropt should usually run concurrently with 'gaps_fixer.py' and 'blocks_extractor.py', but can be executed 
#     independntly.                   
#                                                                                                                                       
#   Notes:                                                                                                            
#   - Runs for 60 seconds per execution. A file request may occasionally retrieve the same file multiple times 
#     due the periodic way files are generated  but duplicates are ignored.                                                                                
#   - Configure Redis connection parameters using environment variables (REDIS_HOST, REDIS_PORT, REDIS_DB).           
#   - Configure the local block repository and blockchain URL as needed.                                              
#                                                                                                                     
#######################################################################################################################
import signal
import sys
import os
import redis
import requests
import logging
import json
from requests.exceptions import Timeout, RequestException, ConnectionError
from time import sleep

def timeout_handler(signum, frame):
    print("Script timed out")
    sys.exit(0)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(60)

# Configure logger
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'blocks_extreactor.log')
logging.basicConfig(filename=log_file, filemode='a', 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize Redis client
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_db = int(os.getenv('REDIS_DB', 0))
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)

local_block_repository = os.getenv('LOCAL_BLOCK_REPOSITORY', './tendermint')
block_url = os.getenv('BLOCK_CHAIN_URL', "https://migaloo-api.polkachu.com/cosmos/base/tendermint/v1beta1/blocks/latest")

ADD_JSON_EXTENSION=False
prev_block_name=None

def fetch_and_store_blocks():    
    global prev_block_name
    blocks_cntr = 0
    logging.info("Ferching blocks from on-line source...")

    try:
        redis_client.ping()
        print("Connected to Redis")
        logging.info("Connected to Redis")
    except redis.ConnectionError:
        print("Could not connect to Redis")
        logging.error("Could not connect to Redis")
        return
        
    try:
        while True:
            try:
                response = requests.get(block_url, timeout=12) 
                if response.status_code == 200:
                    block_data_dict = json.loads(response.text)         
                    file_name = f"{ block_data_dict['block']['header']['height']}"

                    # Ignore previously encountered files.
                    if file_name == prev_block_name:
                        continue
                    else:
                        blocks_cntr += 1
                        prev_block_name = file_name
                        print(file_name)

                        block_data_str = json.dumps(block_data_dict, indent=2)
                        file_extension = ".json" if ADD_JSON_EXTENSION else ""
                        file_path = os.path.join(local_block_repository, f"{file_name}{file_extension}")

                        with open(file_path, 'w', buffering=1024 * 1024) as file:
                            file.write(block_data_str)
                            file.close()

                        # Push block name to Redis log.
                        redis_client.lpush("blocks_collected", file_name)
                        logging.info(f"Block {file_name} saved and stored in Redis.")

                else:
                    logging.error(f"Error: Failed to fetch the latest block. Status code: {response.status_code}")
                    sleep(5)  # Retry after a short delay
            except Timeout:
                logging.error("Timeout occurred while fetching the latest block")
                sleep(5)  # Retry after a short delay
            except ConnectionError as ce:
                logging.error(f"Connection Error while downloading the latest block: {str(ce)}")
                sleep(5)  # Retry after a short delay
            except RequestException as e:
                logging.error(f"RequestException while downloading the latest block: {str(e)}")
                sleep(5)  # Retry after a short delay
            except Exception as e:
                logging.error(f"An unexpected error occurred: {str(e)}")
                sleep(5)  # Retry after a short delay

    finally:
        # Close the Redis connection
        redis_client.close()
        print("Disconnected from Redis")
        logging.info("Disconnected from Redis")


if __name__ == "__main__":
    fetch_and_store_blocks()

    