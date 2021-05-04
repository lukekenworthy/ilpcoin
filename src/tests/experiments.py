import threading
import unittest
import subprocess
import time

timeout = 30
def time_to_verification(num_verifiers:int):
    try:
        threading.Thread(target=subprocess.run, args=[["ilp-queue", "-verifiers", str(num_verifiers)]], kwargs={"timeout":timeout+num_verifiers+3}).start()
        for i in range(num_verifiers):
            time.sleep(1)
            threading.Thread(target=subprocess.run, args=[["verifier", "-id", str(i+1)]], kwargs={"timeout":timeout-1}).start()
        time.sleep(1)
        threading.Thread(target=subprocess.run, args=[["miner", "-id", "101"]], kwargs={"timeout":timeout}).start()
        time.sleep(timeout+num_verifiers+5)
    except:
        pass

    with open("logs/queue.log", "r") as f:
        contents = f.read()
        return contents.count("is popped from queue.")

if __name__ == '__main__':
    blocks = []
    for i in range(1, 10):
        b = time_to_verification(i)
        blocks.append(b)
    for i in range(1, 10):
        print(f"With {i} verifiers, we verify {blocks[i-1]} blocks in {timeout} seconds")