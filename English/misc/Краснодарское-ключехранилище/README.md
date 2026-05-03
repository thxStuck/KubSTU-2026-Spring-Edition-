# [misc] Krasnodar Key Vault

> **Category:** `misc`  
> **CTF:** KubSTU CTF 2026 Spring

**Category:** Mobile / Crypto / Geo-Forensics **Difficulty:** Medium

## 1. Challenge Analysis

The `SecureVault` application requires entering a JWT token and verifies the user's location.

## 2. Solution Steps

### Step 1: Java Reverse Engineering

We decompile the APK using **Jadx**. In `MainActivity` we find:

- Coordinate check: `45.03547, 38.97531` (Center of Krasnodar).
- JWT verification: Algorithm HS256, secret `k3y45`.

### Step 2: GPS Spoofing

We use an emulator or Fake GPS to set the coordinates to Krasnodar.

### Step 3: JWT Generation

We create a token with the secret `k3y45`:

- **Header:** `{"alg": "HS256", "typ": "JWT"}`
- **Payload:** `{"user": "ctf_player", "exp": 1999999999}`

### Step 4: Native Reverse Engineering

The flag is returned by the native function `getFlagNative()`. We extract `libsecurevault.so` and analyze it in **Ghidra**. We find an XOR array with key `0x55`.

**Decryption:**

```python

enc = [0x1e, 0x20, 0x37, 0x06, 0x01, 0x00, 0x2e, 0x1f, 0x02, 0x11, 0x0a, 0x1e, 0x3e, 0x27, 0x34, 0x36, 0x3b, 0x3b, 0x3a, 0x31, 0x33, 0x34, 0x0a, 0x12, 0x05, 0x06, 0x3a, 0x18, 0x65, 0x36, 0x3e, 0x34, 0x64, 0x3b, 0x32, 0x3a, 0x0a, 0x18, 0x34, 0x26, 0x21, 0x30, 0x27, 0x2c]
print("".join([chr(b ^ 0x55) for b in enc]))
```


**Result:** `KubSTU{JWT_Krasnodar_GPS_M0ck1ng_Master}`




