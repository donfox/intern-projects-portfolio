########################################################################################################################
#                                                                                                                     
#   File: gaps_fixer.py                                                                                               
#   Author: Don Fox                                                                                                   
#   Date: 06/21/2024                                                                                                  
#                                                                                                                     
#   Description:                                                                                                      
#   Scans a list from Redis of blockchain block files that are missing from the sequence that have been downloaded. It
#   then requests the missing blocks from the on-line source and stores them in the local repository.                                                              
#                                                                                                                     
#   Usage:                                                                                                            
#   - Ensure Redis is running and accessible.                                                                         
#   - This scropt should usually run concurrently with 'gaps_detector.py' and 'blocks_extractor.py', but can be executed 
#     independntly.                   
#                                                                                                                     
#   Notes:                                                                                                            
#   - Configure Redis connection parameters using environment variables (REDIS_HOST, REDIS_PORT, REDIS_DB).           
#   - Configure the local block repository and blockchain URL as needed.                                              
#                                                                                                                     
#######################################################################################################################
import os
import json
import requests
import logging
import redis
#from redis import Redis
from time import sleep

# Import Timeout from requests.exceptions
from requests.exceptions import Timeout

# Create log directory if not exists
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'gaps_fixer.log')
logging.basicConfig(filename=log_file, filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

request_blocks_logger = logging.getLogger('blocks')

# Global varaibles
BLOCK_CHAIN_URL = "https://migaloo-api.polkachu.com/cosmos/base/tendermint/v1beta1/blocks/{}"
local_block_repository = '../blocks_repo'

def fetch_missing_blocks(missing_blocks):

    for block_number in missing_blocks:
        block_url = BLOCK_CHAIN_URL.format(block_number)
        
        request_blocks_logger.info(f"Requesting block from URL {block_url}")

        try:
            response = requests.get(block_url, timeout=12)

            if response.status_code == 200:
                python_object = json.loads(response.text)
                block_data_str = json.dumps(python_object, indent=2)
                file_path = os.path.join(local_block_repository, f"{block_number}")

               # print(f"Should be about to write {block_number} ")

                with open(file_path, "w", buffering=1024 * 1024) as file:
                    file.write(block_data_str)

                # print(f"Wrote {block_number} ")

                # Log success only once here
                request_blocks_logger.info(f"Downloaded block {block_number} fetched and stored.")

            else:
                logging.error(f"Error: Failed to fetch block {block_number}. Status code: {response.status_code}. Response: {response.text}")
                continue
        except Exception as e:
            logging.error(f"Error downloading block {block_number}: {str(e)}")
            continue


def main():

    # Initialize Redis client
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    try:
        redis_client.ping
        print("Connected to Redis")
        logging.info("Connected to Redis")
    except redis.ConnectionError:
        print("Could not connect to Redis")
        logging.error("Could not connect to Redis")
        exit()

    # Number of Redis scans per execution
    scans_per_execution = 5

    gaps_detected = redis_client.get("gaps_detected")
    for _ in range(scans_per_execution):
        gaps_detected = redis_client.get("gaps_detected")
        if gaps_detected:
            missing_blocks = json.loads(gaps_detected)
            print(f"MISSING_BLOCKS: {missing_blocks}")
            fetch_missing_blocks(missing_blocks)
            print(f"Missing blocks fetched and stored: {missing_blocks}")
        else:
            print("No missing blocks detected in Redis.")
            logging.info("No missing blocks detected in Redis.")       

        # Sleep between scans
        sleep(12)

if __name__ == '__main__':
    main()

