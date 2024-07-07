import json
import sys
import os
import sqlite3
import random
import string
import hashlib


class CoreDatabase:
    def __init__(self, filename):
        self.basepath = os.path.join(os.path.dirname(__file__), 'DataStorage')
        self.filename = filename
        self.filepath = os.path.join(self.basepath, self.filename)  # File location

    # Function to read data from the file
    def read(self):
        if not os.path.exists(self.filepath):
            print(f"File {self.filepath} does not exist")
            return False

        with open(self.filepath, 'r') as file:
            line = file.read()

        if len(line) > 0:
            data = json.loads(line)
        else:
            data = []
        return data

    # Function to write data to the file
    def write(self, item):
        data = self.read()
        if data:
            data = data + item
        else:
            data = item

        with open(self.filepath, 'w+') as file:
            file.write(json.dumps(data, indent=4))

    # Function to clear the contents of the file
    def clearFile(self):
        # Open file in write mode to clear its contents
        with open(self.filepath, 'w') as file:
            file.truncate()


# Account class
class Account:
    def __init__(self, address, balance):
        self.address = address
        self.balance = balance


# Function to generate a random address
def generateAddress(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

# Account information class
class accInfo:
    def __init__(self):
        self.conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'DataStorage', 'accounts.db'))  # Open connection once

    # Function to create the accounts table
    def createAccountsTable(self, conn):
        self.conn.execute("CREATE TABLE IF NOT EXISTS accounts "
                          "(address TEXT, "
                          "balance REAL)")

    # Function to create an account
    def createAccount(self):
        randAddress = generateAddress(30)
        hashAddress = hashlib.sha256(randAddress.encode()).hexdigest()
        address = "0x" + hashAddress[:10]

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE address=?", (address,))
        existingAccount = cursor.fetchone()

        if not existingAccount:
            self.createAccountsTable(self.conn)
            self.conn.execute("INSERT INTO accounts (address, balance) VALUES (?, ?)", (address, 0))
            self.conn.commit()

            return address

    # Function to get an account
    def getAccount(self, address):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE address=?", (address,))
        accountData = cursor.fetchone()

        if accountData:
            return Account(accountData[0], accountData[1])  # Create Account object
        else:
            return None  # Account not found

    # Function to update the balance of an account
    def updateBalance(self, address, new_balance):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE accounts SET balance=? WHERE address=?", (new_balance, address))
        if cursor.rowcount == 0:
            print(ValueError(f"Account with address {address} not found"))
        self.conn.commit()

    def close(self):
        self.conn.close()  # Close connection when done


############################################################################################################

class Database(CoreDatabase):
    def __init__(self):
        self.filename = 'BlockchainData'
        super().__init__(self.filename)  # Pass the filename to the superclass constructor

    # Function to get the last block from the database
    def lastBlock(self):
        data = self.read()
        if data:
            return data[-1]
        else:
            return False

    # Function to clear the blockchain data
    def clearBlockchainData(self):
        self.clearFile()
