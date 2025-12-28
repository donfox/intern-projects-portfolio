import redis

print("check_output.py is running")

# Connect to Redis
redis_instance = redis.Redis(host='localhost', port=6379, db=0)

# Define the Redis set key
BLOCKS_SET = 'processed_blocks'

# Check if the block number exists in the set
block_number = 10551931
is_member = redis_instance.sismember(BLOCKS_SET, block_number)

# Print the result
if is_member:
    print(f"Block {block_number} is in the set {BLOCKS_SET}.")
else:
    print(f"Block {block_number} is NOT in the set {BLOCKS_SET}.")