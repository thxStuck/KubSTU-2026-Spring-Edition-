# [stego] Capybara Secret

> **Category:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

---

Challenge info:
Category: Steganography
Difficulty: Medium

## 🚩 Flag

```
KubSTU{W0W_1ncred1ble_capyba6a}
```

## Step 1: Image analysis

After receiving the file challenge.jpg, the first thing to do is check it for hidden information. In steganography, there are several popular methods:
- LSB (Least Significant Bit) — hiding data in the least significant bits of pixels
- Metadata (EXIF) — hiding in file service information
- File concatenation — appending data to the end of a file
- And others...

Let's start simple — check the metadata.

## Step 2: Extracting EXIF metadata

Method 1: ExifTool (recommended)
exiftool challenge.jpg
The output will show many fields. Pay attention to the XP Comment field:
XP Comment                      : XhoFGH{J0J_1aperq1oyr_pnclon6n}

Method 2: Python + Pillow
from PIL import Image
from PIL.ExifTags import TAGS

img = Image.open('challenge.jpg')
exif_data = img._getexif()

for tag_id, value in exif_data.items():
    tag = TAGS.get(tag_id, tag_id)
    print(f"{tag}: {value}")

Method 3: Online services
You can use an online EXIF viewer:
https://exifinfo.org/
https://www.metadata2go.com/

## Step 3: Analyzing the found string

Found string: XhoFGH{J0J_1aperq1oyr_pnclon6n}
This string:
- Resembles the flag format (structure XXXXX{...})
- Contains unreadable text
- Is probably encrypted with a simple cipher

The flag format is KubSTU{...}, but we see XhoFGH{...}.
Let's check the ROT13 hypothesis:
- K → X (shift by 13)
- u → h (shift by 13)
- b → o (shift by 13)
- ...

The pattern matches — this is ROT13!

## Step 4: ROT13 decryption

Method 1: Online decoder
Use any ROT13 decoder: https://rot13.com/

Method 2: Python
import codecs

encrypted = "XhoFGH{J0J_1aperq1oyr_pnclon6n}"
decrypted = codecs.decode(encrypted, 'rot_13')
print(decrypted)

Method 3: Linux/Bash
echo "XhoFGH{J0J_1aperq1oyr_pnclon6n}" | tr 'A-Za-z' 'N-ZA-Mn-za-m'

Method 4: CyberChef
Use CyberChef with the "ROT13" recipe: https://gchq.github.io/CyberChef/#recipe=ROT13(true,true,false,13)

## Solution

After applying ROT13, we get the flag:
```
KubSTU{W0W_1ncred1ble_capyba6a}
```

What you needed to know to solve this:
- EXIF metadata — JPEG images contain metadata, including non-standard fields like XPComment, XPKeywords (Windows-specific)
- EXIF tools — exiftool, Python libraries, online services
- ROT13 cipher — a simple substitution cipher where each letter is replaced by the letter 13 positions ahead in the alphabet. ROT13 is its own inverse (applying it twice returns the original text)
- Attention to detail — not everything that looks like junk is junk. Encrypted data may look unreadable but have a definite structure
