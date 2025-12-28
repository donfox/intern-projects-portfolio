# Redis_Collector

## Overview
"redis_collector`continuously and/or incrementally monitors and collects blockchain block files, 
detects any gaps in the sequence of collected files, and requests and stores the missing blocks to
remove the gaps Collected blocks are stored locally, and metadata is logged.

The collection process involves the running of a bash shell which then runs three python scripts
concurrently. They collect new block files, detects any missing files and then requests the missing 
files from the on line source and use them to fill the gaps. These concurrent processes communicate 
via. Redis.

## Components
1. **Bash script('run_all_scripts')**: Manages execution of the Python scripts
2. **Python Scripts**:
	- 'blocks_collector.py': Collects blockchain block files and lists their filename to Redis.
	- 'gaps_detector.py': Detects gaps in the sequence of collected block files writing the names
	  of missing files to Redis.
    - `gaps_fixer.py`: Requests and stores missing blocks by monitoring the Redis store for 
      detected gaps.
	    
## Prerequisites
- Python 3.x
- Redis server
- requests library
- logging library

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/donfox/redis_indexer.git
    cd redis_indexer
    ```

 2. Create a virtual environment and activate it:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Ensure the Redis server is running on your local machine.

## Usage Running the Scripts
Use the provided shell script `run_all_scripts.sh` to run the Python scripts concurrently. This
script ensures that all logs are properly recorded.

1. Make the shell script executable:
    ```sh
    chmod +x run_all_scripts.sh
    ```

2. Run the shell script:
    ```sh
    ./run_all_scripts.sh
    ```

There are a few key advantages to using Redis for passing information between concurrently running
scripts over simply bundling the functions into one application and using direct function calls:

### 1. **Scalability and Decoupling**
   - **Redis**: Using Redis as an intermediary allows you to decouple the different parts of your 
   application. Each script can run independently, potentially on different machines, and 
   communicate through Redis. This makes it easier to scale each part of the application 
   independently.

   - **Function Calls**: Bundling everything in one application leads to tight coupling. All the 
   logic has to run within the same process, which can make scaling more difficult, especially if 
   different parts of the application have different performance or resource needs.

### 2. **Concurrency and Distributed Systems**
   - **Redis**: Redis can handle communication between multiple instances of different scripts 
   running concurrently, even across multiple servers. It’s well-suited for distributed systems 
   where scripts may need to run on different machines or containers.

   - **Function Calls**: When using direct function calls within a single application, all code must
   run on the same machine within the same process or thread. This may not be efficient or even 
   possible when scaling out across distributed environments.

### 3. **Asynchronous Communication**
   - **Redis**: You can implement asynchronous communication via Redis by using features like Redis 
   Pub/Sub, Redis Streams, or simply storing state in Redis. Scripts can run at their own pace, and 
   you can have non-blocking message passing.

   - **Function Calls**: Using traditional function calls, you have synchronous communication where 
   the caller has to wait for the callee to finish execution before continuing. Asynchronous 
   patterns are harder to implement without additional frameworks.

### 4. **Fault Tolerance**
   - **Redis**: Redis can act as a buffer, meaning if one script crashes or is slow, the other 
   script can continue running. The crashed script can restart and pick up where it left off by 
   retrieving the required data from Redis.

   - **Function Calls**: If something goes wrong in one part of the application, it can bring down 
   the entire system, since everything is bundled together and tightly coupled.

### 5. **Persistence and Shared State**
   - **Redis**: Redis can store shared state between multiple scripts. This is useful if you need 
   to persist data across multiple runs of the scripts or between different applications.

   - **Function Calls**: In a monolithic application, state is typically shared in memory, which 
   doesn’t persist between application restarts, and it can be hard to share this state across 
   different applications or processes.

### 6. **Cross-Language and Microservices**
   - **Redis**: Redis allows different parts of your system to be written in different programming 
   languages. One script could be in Python, another in Node.js, and they can still communicate 
   seamlessly via Redis.

   - **Function Calls**: If you bundle everything into one application, all code must be in the 
   same programming language or you’ll need additional infrastructure for inter-language 
   communication.

### 7. **Load Balancing**
   - **Redis**: Redis enables load balancing by allowing multiple worker scripts to pull tasks from 
   a shared queue or list of tasks stored in Redis. This makes it easier to balance the load across 
   multiple workers.

   - **Function Calls**: Bundling scripts together does not easily allow for load balancing or task 
   distribution across multiple instances.

### When to Bundle Scripts
- If your application is simple, runs on a single machine, and doesn’t need to scale or communicate 
with other services, bundling scripts into one application with function calls may be easier to 
maintain and have less overhead than introducing Redis.

### Conclusion
Using Redis can provide advantages in scenarios where you need scalability, decoupling, distributed 
communication, or fault tolerance. However, if your application is small and tightly integrated, 
function calls within a monolithic application can be simpler and faster without the overhead of 
networked communication.
