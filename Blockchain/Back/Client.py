import cv2
import socket
import pickle
import struct
import imutils

class QRCodeClient:
    def __init__(self, host_ip, port=5000):
        self.host_ip = host_ip
        self.port = port
        self.socket = None

    # Function to detect and decode QR code in the given frame
    def detect_qr_code(self, frame):
        # Function to detect and decode QR code in the given frame
        detector = cv2.QRCodeDetector()
        value, _, _ = detector.detectAndDecode(frame)
        return value

    # Function to connect to the server
    def connect_to_server(self):
        # Create socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to server
        self.socket.connect((self.host_ip, self.port))

    # Function to send video frames to the server
    def send_video(self):
        vid = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        try:
            while vid.isOpened():
                success, image = vid.read()
                if not success:
                    break

                image = imutils.resize(image, width=480)

                # Detect and print QR code value
                qr_code_value = self.detect_qr_code(image)
                if qr_code_value:
                    print("QR Code value:", qr_code_value)

                a = pickle.dumps(image)
                message = struct.pack("Q", len(a)) + a
                self.socket.sendall(message)

                cv2.imshow("TRANSMITTING VIDEO VIDEO", image)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
        finally:
            vid.release()


    # Function to close the connection
    def close_connection(self):
        if self.socket:
            self.socket.close()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    host_ip = '172.20.10.5' #paste your server ip address here to connect successfully
    port = 5000

    # Create a QRCodeClient object
    qr_client = QRCodeClient(host_ip, port)
    qr_client.connect_to_server()
    qr_client.send_video()
    qr_client.close_connection()