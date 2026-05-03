import os
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.join(BASE_DIR, "64_what_could_this_mean")
HASHCHAIN_FILE = os.path.join(BASE_DIR, "64_what_could_this_mean", "what_could_this_mean.txt")


with open(HASHCHAIN_FILE, "r") as f:
    data = f.read().strip()

chunks = [data[i:i+64] for i in range(0, len(data), 64)]


hash_map = {}

for folder in os.listdir(ROOT):
    folder_path = os.path.join(ROOT, folder)

    if not os.path.isdir(folder_path):
        continue

    for file in os.listdir(folder_path):
        path = os.path.join(folder_path, file)

        with open(path, "rb") as img:
            h = hashlib.sha256(img.read()).hexdigest()

        hash_map[h] = folder


flag = ""

for chunk in chunks:
    flag += hash_map.get(chunk, "?")

print("Recovered flag:")
print(flag)