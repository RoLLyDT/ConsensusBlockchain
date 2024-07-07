import cv2
import time
import numpy as np
import socket
import pickle
import struct
import imutils
import threading
from Database.Database import CoreDatabase
import Blockchain


host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print('HOST IP:', host_ip)


class ConsensusDB(CoreDatabase):
    def __init__(self, blockchain, port=5000):
        super().__init__('Blockchain')  # Initialize the database
        self.host_ip = host_ip
        self.port = port
        self.socket_address = (self.host_ip, port)
        self.server_socket = None
        self.blockchain = blockchain
        self.lock = threading.Lock()

    # Function to detect and decode QR code in the given frame
    def detect_qr_code(self, frame):
        detector = cv2.QRCodeDetector()
        value, _, _ = detector.detectAndDecode(frame)
        return value

    # Function to handle the client
    def handle_client(self, client_socket):
        data = b""
        payload_size = struct.calcsize("Q")
        while True:
            while len(data) < payload_size:
                packet = client_socket.recv(4 * 1024)
                if not packet:
                    break
                data += packet

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                data += client_socket.recv(4 * 1024)

            frame_data = data[:msg_size]
            data = data[msg_size:]
            frame = pickle.loads(frame_data)

            # Detect and print data on the disk
            qr_code_value = self.detect_qr_code(frame)
            if qr_code_value:
                # print("QR Code value:", qr_code_value)

                # Add block to the blockchain
                last_block = self.blockchain.fetchLastBlock()
                if last_block:
                    block_data = {
                        "blockHeight": last_block["blockHeight"],
                        "blockData": last_block["blockData"],
                    }
                    existing_data = self.read()
                    if not any(data['blockData']['blockHash'] == block_data['blockData']['blockHash'] for data in existing_data):
                        self.write([block_data])
                    else:
                        pass  # Block data already exists in the database

            cv2.imshow("RECEIVING VIDEO", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        # vid = cv2.VideoCapture(0)
        # try:
        #     while vid.isOpened():
        #         success, image = vid.read()
        #         image = imutils.resize(image, width=320)
        #         a = pickle.dumps(image)
        #         message = struct.pack("Q", len(a)) + a
        #         client_socket.sendall(message)
        #
        #         # Detect and print QR code value
        #         qr_code_value = self.detect_qr_code(image)
        #         if qr_code_value:
        #             # print("QR Code value:", qr_code_value)
        #
        #             # Add block to the blockchain
        #             last_block = self.blockchain.fetchLastBlock()
        #             if last_block:
        #                 block_data = {
        #                     "blockHeight": last_block["blockHeight"],
        #                     "blockData": last_block["blockData"],
        #                 }
        #                 existing_data = self.read()
        #                 if not any(data['blockData']['blockHash'] == block_data['blockData']['blockHash'] for data in existing_data):
        #                     self.write([block_data])
        #                 else:
        #                     pass  # Block data already exists in the database
        #
        #         cv2.imshow('TRANSMITTING VIDEO', image)
        #         key = cv2.waitKey(1) & 0xFF
        #         if key == ord('q'):
        #             client_socket.close()
        #             break  # Exit the loop if 'q' is pressed
        # finally:
        #     vid.release()

    # Function to start the server
    def start_server(self):
        # Socket Create
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Socket Bind
        self.server_socket.bind(self.socket_address)
        # Socket Listen
        self.server_socket.listen(5)
        print("LISTENING AT:", self.socket_address)

        while True:
            client_socket, addr = self.server_socket.accept()
            print('GOT CONNECTION FROM:', addr)
            if client_socket:
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()

    # Function to close the server
    def close_server(self):
        if self.server_socket:
            self.server_socket.close()
