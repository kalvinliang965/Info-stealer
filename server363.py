import sys
import socket
from datetime import datetime
import os
import zipfile
from io import BytesIO
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

class Server363:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.encryption_key = b'16bytessecretkey'  # AES-128
        self.encryption_iv = b'16bytepubliciv!!'


    def run(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen(1)
            print(f"Listening on {self.host}:{self.port}")

            while True:
                conn, addr = s.accept()
                try:
                    print(f"Connection from {addr[0]}")
                    self.handle_client(conn, addr)
                except Exception as e:
                    print(f"Error handling client: {e}")
                finally:
                    conn.close()

    def handle_client(self, conn, addr):
        encrypted_data = self.receive_all(conn)
        print("Successfully recieve encrypted data")
        
        decrypted_data = self.decrypt(encrypted_data)
        print("Successfully decrypted data")

        output_dir = self.create_output_dir(addr[0])
        print(f"Successfully created output dir: {output_dir}")

        self.extract_zip(decrypted_data, output_dir)
        print("Successfully extract zip file to output dir")

        print(f"Saved {len(os.listdir(output_dir))} files to {output_dir}")

    def receive_all(self, conn, buffer_size=4096):
        data = BytesIO()
        while True:
            chunk = conn.recv(buffer_size)
            if not chunk:
                break
            data.write(chunk)

        return data.getvalue()

    def decrypt(self, encrypted_data):
        cipher = AES.new(self.encryption_key, AES.MODE_CBC, self.encryption_iv)
        return unpad(cipher.decrypt(encrypted_data), AES.block_size)

    def create_output_dir(self, client_ip):
        timestamp = datetime.now().strftime("%Y-%m-%d:%H:%M:%S")
        dir_name = f"{timestamp}_{client_ip}"
        os.makedirs(dir_name, exist_ok=True)
        return dir_name

    def extract_zip(self, zip_data, output_dir):
        with zipfile.ZipFile(BytesIO(zip_data)) as zf:
            zf.extractall(output_dir)

def main():
    if len(sys.argv) != 3:
        print("Usage: ./server <host> <port>")

    host = sys.argv[1]
    port = int(sys.argv[2])

    server = Server363(host, port)
    server.run()

if __name__ == "__main__":
    main()
