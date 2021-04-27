import threading
import unittest
import subprocess
import time

class IntegrationTestsStandard(unittest.TestCase):

    '''
    These tests check expected program behavior when no errors have occurred.
    '''

    # this method lets the entire system run with 2 verifiers and a single miner 
    # for 20 seconds so that subsequent tests can check the logs
    @classmethod
    def setup_class(cls):
        threading.Thread(target=subprocess.run, args=["ilp-queue"], kwargs={"timeout":21}).start()
        threading.Thread(target=subprocess.run, args=["sample_customer"], kwargs={"timeout":15}).start()
        threading.Thread(target=subprocess.run, args=[["verifier", "-id", "1"]], kwargs={"timeout":15}).start()
        time.sleep(1)
        threading.Thread(target=subprocess.run, args=[["verifier", "-id", "2"]], kwargs={"timeout":15}).start()
        time.sleep(2)
        threading.Thread(target=subprocess.run, args=[["miner", "-id", "101"]], kwargs={"timeout":15}).start()

        time.sleep(25)
    
    def test_registration_neighbors(self):
        with open("logs/verifier1.log", "r") as f:
            contents = f.read()
            
            self.assertTrue(contents.find('Recieved 0 neighbors from queue') != -1)
            self.assertTrue(contents.find("GET /register_verifier/1") != -1)
            self.assertTrue(contents.find("Found a bad nonce") != -1)
            self.assertTrue(contents.find("Made genesis block") != -1)
            self.assertTrue(contents.find("Initializing server host localhost port 8001") != -1)
        
        with open("logs/verifier2.log", "r") as f:
            contents = f.read()
            
            self.assertTrue(contents.find('Recieved 1 neighbors from queue') != -1)
            self.assertTrue(contents.find("Grabbing blockchain from neighbor id 1") != -1)
            self.assertTrue(contents.find("Found a bad nonce") == -1)
            self.assertTrue(contents.find("Made genesis block") == -1)
            self.assertTrue(contents.find("Initializing server host localhost port 8002") != -1)
            self.assertTrue(contents.find("GET /register_verifier/2") != -1)

    def test_verification(self):
        with open("logs/verifier1.log", "r") as f:
            contents = f.read()

            self.assertTrue(contents.find("Giving previous") != -1)
            self.assertTrue(contents.find("Previous hash was correct? True") != -1)
            self.assertTrue(contents.find("GET /get_ilp_by_id") != -1)
            self.assertTrue(contents.find("Block successfully validated? True") != -1)
            self.assertTrue(contents.find("Processed block and responded SUCCESS") != -1)
            self.assertTrue(contents.find("About to advertise my 0th block") != -1)
            