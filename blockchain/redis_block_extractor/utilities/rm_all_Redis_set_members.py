import redis

# Connect to Redis
redis_instance = redis.Redis(host='localhost', port=6379, db=0)

# Define the set key
set_key = "processed_blocks"

# Remove all elements from the set
redis_instance.delete(set_key)

# Optionally, recreate an empty set to retain the key
redis_instance.sadd(set_key, *[])