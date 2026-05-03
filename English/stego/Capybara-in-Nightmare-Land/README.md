# [stego] Capybara in Nightmare Land

> **Category:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

**Category:** Steganography  

**Author:** KubSTU CTF Team  

**Flag format:** `KubSTU{...}` 

## Challenge Description

> *A capybara from KubSTU fell asleep during an information security lecture and ended up in a strange nightmare...*
>
> *In this dream, she left a secret message. Can you find it?*
>
> **Hint:** Not everything is what it seems. Look deeper.

##  Files

| File | Description |
|----|----|
| `capybara_nightmare.png` | Image for analysis |

## Goal

Find the hidden flag inside the image.

---

## Solution

### Step 1: File Analysis

First, let's analyze the file using standard tools:

```bash
file capybara_nightmare.png
# Output: PNG image data, 1024 x 1024, 8-bit/color RGB

binwalk capybara_nightmare.png
# Output will show that there's a ZIP archive inside!
```

The `binwalk` tool detects a ZIP archive inside the PNG file. This is a sign of a **polyglot file** — a file that is simultaneously a valid PNG and ZIP.

### Step 2: Extracting the ZIP Archive

The PNG+ZIP polyglot works because:

- PNG is read from the beginning of the file to the IEND chunk
- ZIP is read from the end of the file (looks for End of Central Directory)

We extract the archive:

```bash
# Method 1: simply unzip
unzip capybara_nightmare.png -d extracted/

# Method 2: via binwalk
binwalk -e capybara_nightmare.png
```

Inside the archive we find:

- `README.txt` — a hint
- `encrypted_flag.bin` — encrypted flag

### Step 3: Analyzing README.txt

```
╔══════════════════════════════════════════════════════════════╗
║           🦫 CAPYBARA'S ENCRYPTED SECRET 🦫                  ║
╠══════════════════════════════════════════════════════════════╣
║  The flag is XOR encrypted.                                  ║
║  The key is hidden in the original image...                  ║
║  Look closer at the pixels! 🔍                               ║
║                                                              ║
║  Hint: LSB (Least Significant Bit)                           ║
║  Password length: 19 characters                              ║
╚══════════════════════════════════════════════════════════════╝
```

The hints tell us:

1. The flag is XOR encrypted
2. The key is hidden in the image
3. LSB steganography is used
4. Password length: 19 characters

### Step 4: LSB Extraction

**LSB (Least Significant Bit)** — a steganography technique where data is hidden in the least significant bits of image pixels. Changing the least significant bit is practically invisible to the human eye.

We write an extraction script:

```python
from PIL import Image
import numpy as np

def extract_lsb(image_path):
    img = Image.open(image_path).convert('RGB')
    pixels = np.array(img).flatten()
    
    bits = ''
    chars = []
    
    for pixel in pixels:
        bits += str(pixel & 1)  # Extract least significant bit
        
        if len(bits) == 8:
            char = chr(int(bits, 2))
            chars.append(char)
            bits = ''
            
            # Look for end marker
            text = ''.join(chars)
            if 'END_LSB' in text:
                return text.split('\x00')[0]
    
    return ''.join(chars[:100])

password = extract_lsb("capybara_nightmare.png")
print(f"Password: {password}")
# Output: N1ghtm4r3_C4py_2026
```

Extracted password: `N1ghtm4r3_C4py_2026`

### Step 5: Decrypting the Flag

Now we use the found password for XOR decryption:

```python
def xor_decrypt(encrypted: bytes, key: str) -> str:
    key_bytes = key.encode('utf-8')
    result = []
    for i, byte in enumerate(encrypted):
        result.append(chr(byte ^ key_bytes[i % len(key_bytes)]))
    return ''.join(result)

# Read the encrypted flag
with open("encrypted_flag.bin", "rb") as f:
    encrypted = f.read()

password = "N1ghtm4r3_C4py_2026"
flag = xor_decrypt(encrypted, password)
print(f"Flag: {flag}")
```

---

## Flag

```
KubSTU{H0ly_M0ly_CapyHaCk1r}
```

---

## Tools Used

| Tool | Purpose |
|----|----|
| `file` | File type identification |
| `binwalk` | Analysis and extraction of embedded data |
| `unzip` | ZIP archive extraction |
| Python + PIL | LSB extraction |
| Python | XOR decryption |

### Alternative Tools

- **zsteg** — automatic LSB steganography detection
- **stegsolve** — visual LSB layer analysis
- **010 Editor** — hex editor for polyglot analysis

---

## Solution Algorithm Summary

```
┌─────────────────────────────────────┐
│  capybara_nightmare.png             │
│  (PNG + ZIP polyglot)               │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌────────────┐      ┌────────────────┐
│  As PNG    │      │    As ZIP      │
│  (LSB)     │      │                │
└─────┬──────┘      └───────┬────────┘
      │                     │
      ▼                     ▼
┌────────────┐      ┌────────────────┐
│  Password: │      │ encrypted_flag │
│  N1ghtm4r3 │      │     .bin       │
│  _C4py_    │      └───────┬────────┘
│  2026      │              │
└─────┬──────┘              │
      │                     │
      └─────────┬───────────┘
                │
                ▼
        ┌──────────────┐
        │  XOR Decrypt │
        └──────┬───────┘
               │
               ▼
    ┌─────────────────────────┐
    │ KubSTU{H0ly_M0ly_       │
    │        CapyHaCk1r}      │
    └─────────────────────────┘
```

---

## Protection Against Automated Solvers

This challenge uses several layers of protection:

1. **Polyglot file** — not all tools automatically detect it
2. **Custom LSB marker** — `END_LSB` instead of standard markers
3. **XOR encryption** — requires finding the key; simple brute-force is impossible without knowing the key length and format

---

## Author

Created for KubSTU CTF competitions.