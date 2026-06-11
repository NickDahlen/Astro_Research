# helloworld.py
import time

for i in range(10):
    print(f"Hello from HPC! Iteration {i+1}")
    time.sleep(120)  # Sleep for 120 seconds so we can see the job in the queue
