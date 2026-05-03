#!/usr/bin/env python3
"""
Usage:
python3 solve.py --root ./64_what_could_this_mean --what_could_this_mean ./64_what_could_this_mean/what_could_this_mean.txt
"""

import argparse
import hashlib
from pathlib import Path

def hash_file(path, algo="sha256"):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def infer_chunk_size(chain_len):
    # common hash lengths
    common = [32, 40, 64, 96, 128]
    for size in common:
        if chain_len % size == 0:
            return size
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--hashchain", required=True)
    parser.add_argument("--algo", default="sha256")
    args = parser.parse_args()

    root = Path(args.root)
    chain = Path(args.hashchain).read_text().strip()

    chunk_size = infer_chunk_size(len(chain))
    if not chunk_size:
        print("[-] Could not determine chunk size automatically.")
        return

    print(f"[+] Chunk size detected: {chunk_size} hex chars")
    print(f"[+] Total chunks: {len(chain)//chunk_size}")

    # build hash map
    print("[+] Building hash map...")
    hash_map = {}

    for folder in root.iterdir():
        if not folder.is_dir():
            continue
        symbol = folder.name

        for file in folder.iterdir():
            if not file.is_file():
                continue
            h = hash_file(file, args.algo)[:chunk_size]
            hash_map[h] = symbol

    # reconstruct flag
    print("[+] Reconstructing flag...")
    flag = ""

    for i in range(0, len(chain), chunk_size):
        chunk = chain[i:i+chunk_size]

        if chunk not in hash_map:
            print(f"[!] Missing hash: {chunk}")
            flag += "?"
        else:
            flag += hash_map[chunk]

    print("\n[+] Recovered flag:")
    print(flag)

if __name__ == "__main__":
    main()