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

def read_lrc_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    lyrics = []
    for line in lines:
        if line[-1] != "]":
            # Strip any leading/trailing whitespace
            line = line.strip()
            if line:
                # Parse the timestamp and lyric
                parts = line.split(']')
                for part in parts[:-1]:  # Handle multiple timestamps
                    timestamp = part[1:]  # Skip the leading '['
                    lyric = parts[-1]
                    lyrics.append((timestamp, lyric))
    return lyrics