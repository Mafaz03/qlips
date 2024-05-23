import os

def temp_del(folders):
    if not isinstance(folders, list): folders = [folders]
    for folder in folders:
        try:
            for i in os.listdir(folder):
                os.remove(f"{folder}/{i}")
            print(f"Content of {folder} Deleted")
        except: print(f"{folder} does not exist")

def create_root_folders(folders):
    for folder in ["Temp", "Videos"]: os.makedirs(folder, exist_ok=True)