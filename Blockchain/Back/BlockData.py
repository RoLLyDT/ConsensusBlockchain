from utilities.util import hash256

class BlockData:
    def __init__(self, version, prevHash, merkleRoot, timestamp, bits):
        self.version = version
        self.prevHash = prevHash
        self.merkleRoot = merkleRoot
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = 0
        self.blockHash = b""

    # Mining function
    def mine(self):
        while(self.blockHash[0:2]) != b'\x00\x00':
            self.blockHash = hash256(
                (str(self.version) + self.prevHash + self.merkleRoot +
                 str(self.timestamp) + self.bits + str(self.nonce)).encode())
            self.nonce += 1
            #print(f"Mining started {self.nonce}", end = '\r')
        #print("Mining completed")