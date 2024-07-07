import sys
import os
import datetime
import hashlib
import json
import time
import logging

from threading import Lock, Thread

script_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(script_path))
sys.path.append(project_root)

from flask import Flask, jsonify
from BlockData import BlockData
from Database.Database import Database, accInfo
from utilities.util import hash256
from MenuFeatures import menuFeatures
import Consensus

VERSION = 1

# Block class
class Block:
    # Transaction storage
    def __init__(self, blockHeight, blockSize, blockData, TxCount, Txs):
        self.blockHeight = blockHeight
        self.blockSize = blockSize
        self.blockData = blockData
        self.Txcount = TxCount
        self.Txs = Txs


#   Blockchain class
class Blockchain:
    # First block creation and set its hash to "0"
    def __init__(self):
        self.chain = []
        self.addBlock(blockHeight=0, prevHash='0')
        # print("Blockchain init")

    # Write block data to disk
    def writeDataOnDisk(self, block):
        database = Database()
        database.write(block)

    # Fetch the last block from the database
    def fetchLastBlock(self):
        database = Database()
        lastBlock = database.lastBlock()
        return lastBlock

    # Add a block to the blockchain
    def addBlock(self, blockHeight, prevHash):
        timestamp = int(time.time())
        transaction = f"Validator sent {blockHeight} tokens to User1"
        merkleRoot = hash256(transaction.encode()).hex()
        bits = 'ffff001f'
        blockData = BlockData(VERSION, prevHash, merkleRoot, timestamp, bits)
        blockData.mine()

        block_dict = {
            'blockHeight': blockHeight,
            'blockSize': 1,
            'blockData': {
                'version': blockData.version,
                'prevHash': blockData.prevHash,
                'merkleRoot': blockData.merkleRoot,
                'timestamp': blockData.timestamp,
                'bits': blockData.bits,
                'nonce': blockData.nonce,
                'blockHash': blockData.blockHash.hex()  # Convert bytes to hex for JSON serialisation
            },
            'Txcount': 1,
            'Txs': transaction
        }

        self.writeDataOnDisk([block_dict])
        # print(f"Block added {blockHeight}")
        # self.chain.append(Block(blockHeight, 1, blockData.__dict__, 1, transaction).__dict__)
        # print(self.chain)
        # return self.chain[-1]

    mining_lock = Lock()  # Create a lock for pausing mining

    # Main function for mining
    def main(self):
        while True:  # Infinite loop
            with self.mining_lock:
                # Fetch the last block within the loop to get the correct prevHash and blockHeight
                lastBlock = self.fetchLastBlock()
                if lastBlock:
                    blockHeight = lastBlock["blockHeight"] + 1
                    prevHash = lastBlock['blockData']['blockHash']
                else:
                    blockHeight = 0  # Start from 0 if no existing blocks
                    prevHash = '0'  # Use '0' for the first block

                self.addBlock(blockHeight, prevHash)  # Create and write the block to disk
                # print(f"Mining paused {blockHeight}")

            time.sleep(0.5)


# Disable the Werkzeug logging
log = logging.getLogger('werkzeug')
log.disabled = True

# Disable the Flask banner
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

app = Flask(__name__)


# Current blockchain information
@app.route('/get_chain', methods=['GET'])
def display_chain():
    with Blockchain.mining_lock:
        blocks = []

        # Fetch all blocks from the database
        database = Database()
        chain = database.read()

        # If there are blocks in the chain, add each block to the response
        if chain:
            for block in chain:
                blocks.append({
                    'blockHeight': block['blockHeight'],
                    'blockData': block['blockData']
                })

            return jsonify(blocks), 200
        else:
            return jsonify({'message': 'Blockchain is empty'}), 404


"""
@app.route('/menu', methods=['GET'])
def menu():
    # Implement your menu functionality here
    # For example, you can return a JSON response containing the menu options
    menu_options = {
        '1': 'Option 1: Check balance',
        '2': 'Option 2: Perform transaction',
        '3': 'Option 3: View transaction history'
    }
    return jsonify(menu_options)
"""

if __name__ == "__main__":
    # Clear the contents of the BlockchainData file - apply if needed
    database = Database()
    database.clearBlockchainData()

    blockchain = Blockchain()

    # Start the mining thread
    mining_thread = Thread(target=blockchain.main, daemon=True)
    mining_thread.start()

    # flask
    web_thread = Thread(target=app.run, daemon=True, kwargs={'host': '127.0.0.1', 'port': 5000})
    web_thread.start()

    consensus = Consensus.ConsensusDB(blockchain)

    # Start the consensus thread
    consensus_thread = Thread(target=consensus.start_server,  daemon=True)
    consensus_thread.start()

    time.sleep(1)
    # menu
    menu_features = menuFeatures()
    menu_features.run_menu()