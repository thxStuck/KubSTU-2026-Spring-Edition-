# [stego] Capybara Secret

> **Category:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

## Challenge Info

- **Category:** Steganography
- **Difficulty:** Medium
- **Flag:** `KubSTU{W0W_1ncred1ble_capyba6a}`

---

## Step 1: Image Analysis

Upon receiving the file `challenge.jpg`, we first check it for hidden information. In steganography, there are several popular methods:

- LSB (Least Significant Bit) — hiding data in the least significant bits of pixels
- Metadata (EXIF) — hiding in the file's service information
- File concatenation — appending data to the end of a file
- And others...

Let's start simple — check the metadata.

## Step 2: Extracting EXIF Metadata

### Method 1: ExifTool (recommended)

```bash
exiftool challenge.jpg
```

The output will show many fields. Pay attention to the **XP Comment** field:

```
XP Comment                      : XhoFGH{J0J_1aperq1oyr_pnclon6n}
```

### Method 2: Python + Pillow

```python
from PIL import Image
from PIL.ExifTags import TAGS

img = Image.open('challenge.jpg')
exif_data = img._getexif()

for tag_id, value in exif_data.items():
    tag = TAGS.get(tag_id, tag_id)
    print(f"{tag}: {value}")
```

### Method 3: Online Services

You can use online EXIF viewers:

- <https://exifinfo.org/>
- <https://www.metadata2go.com/>

## Step 3: Analyzing the Found String

Found string: `XhoFGH{J0J_1aperq1oyr_pnclon6n}`

This string:

- Resembles the flag format (structure `XXXXX{...}`)
- Contains unreadable text
- Is likely encrypted with a simple cipher

The flag format is `KubSTU{...}`, and we see `XhoFGH{...}`.

Let's check the ROT13 cipher hypothesis:

- K → X (shift by 13)
- u → h (shift by 13)
- b → o (shift by 13)
- ...

The pattern matches — this is ROT13!

## Step 4: ROT13 Decryption

### Method 1: Online Decoder

Use any ROT13 decoder: <https://rot13.com/>

### Method 2: Python

```python
import codecs

encrypted = "XhoFGH{J0J_1aperq1oyr_pnclon6n}"
decrypted = codecs.decode(encrypted, 'rot_13')
print(decrypted)
```

### Method 3: Linux/Bash

```bash
echo "XhoFGH{J0J_1aperq1oyr_pnclon6n}" | tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

### Method 4: CyberChef

Use CyberChef with the "ROT13" recipe: <https://gchq.github.io/CyberChef/#recipe=ROT13(true,true,false,13)>

## Solution

After applying ROT13, we get the flag:

```
KubSTU{W0W_1ncred1ble_capyba6a}
```

---

## What You Needed to Know to Solve This

1. **EXIF metadata** — JPEG images contain metadata, including non-standard fields like XPComment, XPKeywords (Windows-specific)
2. **EXIF tools** — exiftool, Python libraries, online services
3. **ROT13 cipher** — a simple substitution cipher where each letter is replaced by the letter 13 positions ahead in the alphabet. ROT13 is its own inverse (applying it twice returns the original text)
4. **Attention to detail** — not everything that looks like garbage is garbage. Encrypted data may look unreadable but have a specific structure

---

## Alternative Automated Solver

```python
import struct
import codecs

def extract_xp_comment(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    
    pos = 2
    while pos < len(data) - 1:
        if data[pos] != 0xff:
            pos += 1
            continue
        marker = data[pos + 1]
        if marker == 0xe1:
            length = struct.unpack('>H', data[pos+2:pos+4])[0]
            segment = data[pos+4:pos+2+length]
            if segment[:6] == b'Exif\x00\x00':
                tiff = segment[6:]
                endian = '<' if tiff[:2] == b'II' else '>'
                ifd_off = struct.unpack(endian + 'I', tiff[4:8])[0]
                n = struct.unpack(endian + 'H', tiff[ifd_off:ifd_off+2])[0]
                for i in range(n):
                    e = ifd_off + 2 + i * 12
                    tag = struct.unpack(endian + 'H', tiff[e:e+2])[0]
                    if tag == 0x9C9C:
                        cnt = struct.unpack(endian + 'I', tiff[e+4:e+8])[0]
                        off = struct.unpack(endian + 'I', tiff[e+8:e+12])[0]
                        return tiff[off:off+cnt].decode('utf-16le').rstrip('\x00')
            pos += 2 + length
        elif 0xe0 <= marker <= 0xef or marker == 0xfe:
            pos += 2 + struct.unpack('>H', data[pos+2:pos+4])[0]
        else:
            break
    return None

encrypted = extract_xp_comment('challenge.jpg')
print(f"Encrypted: {encrypted}")
print(f"Flag: {codecs.decode(encrypted, 'rot_13')}")
```

---

## Flag

```
KubSTU{W0W_1ncred1ble_capyba6a}
```


