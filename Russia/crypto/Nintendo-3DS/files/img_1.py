#!/usr/bin/env python3

import base64
from Crypto.Cipher import DES3
from Crypto.Util.Padding import unpad

fragment_1 = base64.b64decode("TjFudDNuZG8=")
print(f"Fragment 1 (base64 → bytes): {fragment_1}")

fragment_2 = bytes([83, 51, 99, 117, 114, 49, 116, 121])
print(f"Fragment 2 (decimal → bytes): {fragment_2}")

fragment_3 = bytes.fromhex("4b33792132303236")
print(f"Fragment 3 (hex → bytes):     {fragment_3}")

key = fragment_1 + fragment_2 + fragment_3
print(f"\nFull key: {key}")
print(f"Key length: {len(key)}")

iv_xored = bytes.fromhex("0a001f0273760054")
iv_mask  = b"M4r10Br0"

iv = bytes(a ^ b for a, b in zip(iv_xored, iv_mask))
print(f"\nIV recovered: {iv}")


ciphertext = bytes.fromhex(
    "072a8e75459a545679f3aa56a9fafb38"
    "871022de0c9bd5d7ef55e8dad7861662"
    "eb0fb630d9cdf9dd8c64a3a8ac28b86a"
)

cipher = DES3.new(key, DES3.MODE_CBC, iv)
plaintext = unpad(cipher.decrypt(ciphertext), 8)

flag = plaintext.decode()
print(f"\nFlag: {flag}")

