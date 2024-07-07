import sys
import os
import datetime
import hashlib
import json
import time

from Database.Database import accInfo


class menuFeatures:
    def __init__(self):
        self.account_info = accInfo()

    # Function to create an account
    def create_account(self):
        address = self.account_info.createAccount()
        return address

    # Function to check the balance of an account
    def check_balance(self, address):
        account = self.account_info.getAccount(address)
        if account:
            print(f"Balance of account {account.address}: {account.balance}")
        else:
            print("Account not found.")

    # Function to make a transaction
    def make_transaction(self, sender, receiver, amount):
        sender_account = self.account_info.getAccount(sender)
        receiver_account = self.account_info.getAccount(receiver)

        # Check if both accounts exist
        if sender_account and receiver_account:
            if sender_account.balance >= amount:
                sender_account.balance -= amount
                receiver_account.balance += amount
                self.account_info.updateBalance(sender, sender_account.balance)
                self.account_info.updateBalance(receiver, receiver_account.balance)
                print("Transaction successful!")
            else:
                print("Insufficient balance.")
        else:
            print("Account not found.")

    # Function to close the connection
    def close_connection(self):
        sys.exit()

    # Function to display the menu
    def display_menu(self):
        print("\nAccount Management Menu:")
        print("1. Create Account")
        print("2. Get Account Balance")
        print("3. Make Transaction")
        print("4. Exit")

    # Function to run the menu
    def run_menu(self):
        while True:
            self.display_menu()
            choice = input("Enter your choice: ")

            if choice == '1':
                address = self.create_account()
                print(f"Account created successfully, with an address: {address}")
            elif choice == '2':
                address = input("Enter account address: ")
                self.check_balance(address)
            elif choice == '3':
                sender = input("Enter sender address: ")
                receiver = input("Enter receiver address: ")
                amount = float(input("Enter amount: "))
                self.make_transaction(sender, receiver, amount)
            elif choice == '4':
                self.close_connection()
            else:
                print("Invalid choice. Please try again.")