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
        threading.Thread(target=subprocess.run, args=[["ilp-queue", "-verifiers", "1"]], kwargs={"timeout":21}).start()
        threading.Thread(target=subprocess.run, args=["sample_customer"], kwargs={"timeout":15}).start()
        time.sleep(1)
        threading.Thread(target=subprocess.run, args=[["verifier", "-id", "1"]], kwargs={"timeout":15}).start()
        time.sleep(1)
        threading.Thread(target=subprocess.run, args=[["verifier", "-id", "2"]], kwargs={"timeout":15}).start()
        time.sleep(2)
        threading.Thread(target=subprocess.run, args=[["miner", "-id", "101"]], kwargs={"timeout":15}).start()

        time.sleep(30)
    
    def test_registration_neighbors(self):
        with open("logs/verifier1.log", "r") as f:
            contents = f.read()
            
            # verifier 1 should get neighbors register itself
            self.assertTrue(contents.find('Recieved 0 neighbors from queue') != -1)
            self.assertTrue(contents.find("GET /register_verifier/1") != -1)

            # verifier 1 should make genesis block
            self.assertTrue(contents.find("Found a bad nonce") != -1)
            self.assertTrue(contents.find("Made genesis block") != -1)

            # verifier 1 should start its server
            self.assertTrue(contents.find("Initializing server host localhost port 8001") != -1)
        
        with open("logs/verifier2.log", "r") as f:
            contents = f.read()
            
            # verifier 2 should be able to get a neighbor and a blockchain
            self.assertTrue(contents.find('Recieved 1 neighbors from queue') != -1)
            self.assertTrue(contents.find("Grabbing blockchain from neighbor id 1") != -1)
            self.assertTrue(contents.find("GET /register_verifier/2") != -1)

            # verifier 2 should NOT make a genesis block
            self.assertTrue(contents.find("Found a bad nonce") == -1)
            self.assertTrue(contents.find("Made genesis block") == -1)

            # verifier 2 should start its server
            self.assertTrue(contents.find("Initializing server host localhost port 8002") != -1)

    def test_verification(self):
        with open("logs/verifier1.log", "r") as f1, open("logs/verifier2.log", "r") as f2:
            contents1 = f1.read()
            contents2 = f2.read()

            # Both verifiers should communicate with the miner
            self.assertTrue(contents1.find("Giving previous") != -1 and contents2.find("Giving previous") != -1)

            # at least one verifier must verify a block
            self.assertTrue(contents1.find("Previous hash was correct? True") != -1 or contents2.find("Previous hash was correct? True") != -1)
            self.assertTrue(contents1.find("GET /get_ilp_by_id") != -1 or contents2.find("GET /get_ilp_by_id") != -1)
            self.assertTrue(contents1.find("Block successfully validated? True") != -1 or contents2.find("Block successfully validated? True") != -1)
            self.assertTrue(contents1.find("Processed block and responded SUCCESS") != -1 or contents2.find("Processed block and responded SUCCESS") != -1)
            self.assertTrue(contents1.find("About to advertise my 0th block") != -1 or contents2.find("About to advertise my 0th block") != -1)
            
            # the miner should advertise to at least one verifier
            self.assertTrue(contents1.find("PUT /send_block/101") != -1 or contents2.find("PUT /send_block/101") != -1)

    def test_queue_initialization(self):
        with open("logs/queue.log", "r") as f:
            contents = f.read()
            
            # first verifier should get 0 neighbors
            self.assertTrue(contents.find("sending neighbors []") != -1)

            # second verifier should get 1 neighbor
            self.assertTrue(contents.find("sending neighbors ['1']") != -1)

            # miner should get both verifiers
            self.assertTrue(contents.find("sending neighbors ['1', '2']") != -1)
            
            # miner should try to grab the top of the queue
            self.assertTrue(contents.find("GET /get_top_ilp") != -1)

            # two verifiers should try to verify an ILP
            self.assertGreaterEqual(contents.find("Looking up ilp with id: 1"), 2)

            # first ILP should get popped off
            self.assertTrue(contents.find("Ilp with id 1 is popped from queue.") != -1)

class IntegrationTestsBuggyMiner(unittest.TestCase):

    # this method lets the entire system run with 2 verifiers, one faulty miner, and one functioning miner
    # for 30 seconds so that subsequent tests can check the logs
    @classmethod
    def setup_class(cls):
        threading.Thread(target=subprocess.run, args=[["ilp-queue", "-verifiers", "1"]], kwargs={"timeout":30}).start()
        threading.Thread(target=subprocess.run, args=["sample_customer"], kwargs={"timeout":10}).start()
        threading.Thread(target=subprocess.run, args=[["verifier", "-id", "1"]], kwargs={"timeout":20}).start()
        time.sleep(1)
        threading.Thread(target=subprocess.run, args=[["verifier", "-id", "2"]], kwargs={"timeout":20}).start()
        time.sleep(2)
        threading.Thread(target=subprocess.run, args=[["miner", "-id", "101"]], kwargs={"timeout":20}).start()
        threading.Thread(target=subprocess.run, args=[["miner", "-id", "102", "-buggy"]], kwargs={"timeout":20}).start()

        time.sleep(32)
    
    def test_faulty_miner(self):

        with open("logs/verifier1.log", "r") as f1, open("logs/verifier2.log", "r") as f2:
            contents1 = f1.read()
            contents2 = f2.read()

            # some verifier should catch the faulty block
            self.assertTrue(contents1.find("Block successfully validated? False") != -1 or contents2.find("Block successfully validated? False") != -1)
            # and reject for the right reason
            self.assertTrue(contents1.find("Found invalid nonce or proof of work") != -1 or contents2.find("Found invalid nonce or proof of work") != -1)
            # and notify the faulty miner
            self.assertTrue(contents1.find("Processed block and responded ERR_4") != -1 or contents2.find("Processed block and responded ERR_4") != -1)

            # we should also have enough time to find a good block
            self.assertTrue(contents1.find("Block has been verified successfully") != -1 or contents2.find("Block has been verified successfully") != -1)

    def test_multiple_miners(self):
        with open("logs/queue.log", "r") as f:
            contents = f.read()

            # we should advertise both verifiers
            self.assertTrue(contents.find("sending neighbors ['1', '2']") != -1)

            # we should not advertise a miner
            self.assertTrue(contents.find("sending neighbors ['1', '2', '101']") == -1)