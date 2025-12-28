####################################################################################################
# scan_blocks_dir.py
#
#	Scans a local directory containing downloaded blockchain block files to detect gaps in the 
#   sequence. The names of the missing files a stored in a list during the process.  
#
#   When the list is complete it is passed to a function that does an HTTP request for each file 
#   and writes the retrieved file back to the local diretory filling those gaps.
#
#	Files found missing, are recorded to log and the file in each successful request is logged as 
#   is the record of it being written to the directory.  
#
####################################################################################################
import os
import requests
import logging
import json

local_block_repository = "../blocks_repo"
BLOCK_CHAIN_URL = "https://migaloo-api.polkachu.com/cosmos/base/tendermint/v1beta1/blocks/{}"

# Configure logger
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'scan_blocks.log')

logging.basicConfig(filename=log_file, filemode='a', 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def fetch_missing_blocks(missing_blocks):

    for block_number in missing_blocks:
        block_url = BLOCK_CHAIN_URL.format(block_number)
        
        logging.info(f"Requesting block from URL {block_url}")

        try:
            response = requests.get(block_url, timeout=12)

            if response.status_code == 200:
                python_object = json.loads(response.text)
                block_data_str = json.dumps(python_object, indent=2)
                file_path = os.path.join(local_block_repository, f"{block_number}")

                with open(file_path, "w", buffering=1024 * 1024) as file:
                    file.write(block_data_str)

                # Log success only once here
                logging.infp(f"Downloaded block {block_number} fetched and stored.")

            else:
                logging.error(f"Error: Failed to fetch block {block_number}. Status code: {response.status_code}. Response: {response.text}")
                continue
        except Exception as e:
           logging.error(f"Error downloading block {block_number}: {str(e)}")
           continue


def collect_missing_blocks():
    
    print("Detecting gaps in blocks...")
    
    # Get listing of files in the block file repo.
    block_files = [int(file) for file in os.listdir(local_block_repository) \
        if len(file) == 7 and file.isdigit()]

    block_files.sort()

    # Detect gaps in the sequence
    missing_blocks = []
    for i in range(len(block_files) - 1):
        if block_files[i+1] != block_files[i] + 1:
            missing_blocks.extend(range(block_files[i] + 1, block_files[i+1]))

    logging.info(f"Missing Blocks: {missing_blocks}")

    if missing_blocks:
        fetch_missing_blocks(missing_blocks)

if __name__ == "__main__":
   	collect_missing_blocks()









