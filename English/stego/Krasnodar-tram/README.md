# [stego] Krasnodar tram

> **Category:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

I really love the trams in Krasnodar. It's very convenient, fast, and affordable. Get into the tram vibe and find my message.

 ![img_1.jpg](./images/img_1.jpg)

 ![img_2.jpg](./images/img_2.jpg)


---

We start solving by examining the metadata.

```
PS S:\CTF\steg> exiftool 267.jpg
ExifTool Version Number         : 13.45
File Name                       : 267.jpg
Directory                       : .
File Size                       : 491 kB
File Modification Date/Time     : 2026:03:20 11:41:38+03:00
File Access Date/Time           : 2026:03:20 11:41:47+03:00
File Creation Date/Time         : 2026:03:20 11:39:55+03:00
File Permissions                : -rw-rw-rw-
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
Exif Byte Order                 : Big-endian (Motorola, MM)
Software                        : Adobe Photoshop 25.0
Y Cb Cr Positioning             : Centered
XP Keywords                     : Ly9r=
XP Subject                      : wb=135|b20v
Current IPTC Digest             : 33d0317331e9fa7b6be97c6535ab0b74
Object Name                     : exp=85|ZWJp
Source                          : iso=200|Q3N2
Application Record Version      : 4
Keywords                        : aHR0=, dHUu=, cy0x=
Caption-Abstract                : cy0x=
XMP Toolkit                     : Image::ExifTool 13.45
Description                     : dHUu=
Subject                         : Ly9r=
Credit                          : exp=50|Ly9w
Headline                        : wb=35|aHR0
Label                           : recovery fragments
Nickname                        : aHR0=
DCT Encode Version              : 100
APP14 Flags 0                   : [14]
APP14 Flags 1                   : (none)
Color Transform                 : YCbCr
Comment                         : VISIBLE CACHE:.aHR0=.Ly9r=.dHUu=.cy0x=
Image Width                     : 1500
Image Height                    : 1000
Encoding Process                : Baseline DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:4:4 (1 1)
Image Size                      : 1500x1000
Megapixels                      : 1.5
```

```

ExifTool Version Number         : 13.45
File Name                       : 678.jpg
Directory                       : .
File Size                       : 709 kB
File Modification Date/Time     : 2026:03:20 11:41:39+03:00
File Access Date/Time           : 2026:03:20 11:41:47+03:00
File Creation Date/Time         : 2026:03:20 11:39:55+03:00
File Permissions                : -rw-rw-rw-
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
Exif Byte Order                 : Big-endian (Motorola, MM)
Software                        : Adobe Photoshop 25.0
Y Cb Cr Positioning             : Centered
XP Keywords                     : cHM6=
Current IPTC Digest             : 96af56f5483fe7a0bf425675e771ca21
Object Name                     : exp=35|cHM6
By-line                         : f=50|YXN0
Source                          : Archive
Application Record Version      : 4
Keywords                        : dWJz=, Njk==
Caption-Abstract                : cnUv=
XMP Toolkit                     : Image::ExifTool 13.45
Description                     : f=135|U3VC
Subject                         : cHM6=, cnUv=
Instructions                    : dWJz=
Label                           : recovery fragments
Nickname                        : exp=85|bi5j
DCT Encode Version              : 100
APP14 Flags 0                   : [14], Encoded with Blend=1 downsampling
APP14 Flags 1                   : (none)
Color Transform                 : YCbCr
Comment                         : VISIBLE CACHE:.cHM6=.dWJz=.cnUv=.Njk==
Image Width                     : 1400
Image Height                    : 960
Encoding Process                : Progressive DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:4:4 (1 1)
Image Size                      : 1400x960
Megapixels                      : 1.3
```

---

In the metadata of both photos, we can see 4-character blocks with = at the end. We can assume these all belong to a single base64 string. We write out all the blocks and ask an AI to play around with them to find a working string.

```python
import base64

# Blocks from 267.jpg (odd positions)
blocks_267 = ['Ly9r=', 'aHR0=', 'dHUu=', 'cy0x=', 'cy0x=', 'dHUu=', 'Ly9r=', 'aHR0=', 'aHR0=', 'Ly9r=', 'dHUu=', 'cy0x=']

# Blocks from 678.jpg (even positions)
blocks_678 = ['cHM6=', 'dWJz=', 'Njk==', 'cnUv=', 'cHM6=', 'cnUv=', 'dWJz=', 'cHM6=', 'dWJz=', 'cnUv=', 'Njk==']

print("Decoding blocks from 267.jpg:")
for i, block in enumerate(blocks_267, 1):
    try:
        decoded = base64.b64decode(block).decode('utf-8', errors='replace')
        print(f"  {i:2d}. {block:8s} -> {repr(decoded)}")
    except Exception as e:
        print(f"  {i:2d}. {block:8s} -> Error: {e}")

print("\nDecoding blocks from 678.jpg:")
for i, block in enumerate(blocks_678, 1):
    try:
        decoded = base64.b64decode(block).decode('utf-8', errors='replace')
        print(f"  {i:2d}. {block:8s} -> {repr(decoded)}")
    except Exception as e:
        print(f"  {i:2d}. {block:8s} -> Error: {e}")

# Now interleave them
print("\n\nInterleaving blocks (267 odd, 678 even):")
interleaved = []
max_len = max(len(blocks_267), len(blocks_678))

for i in range(max_len):
    if i < len(blocks_267):
        interleaved.append(('267', blocks_267[i]))
    if i < len(blocks_678):
        interleaved.append(('678', blocks_678[i]))

# Decode the interleaved sequence
print("\nSequential decoding:")
full_string = ""
for source, block in interleaved:
    try:
        decoded = base64.b64decode(block).decode('utf-8', errors='replace')
        full_string += decoded
        print(f"{source}: {block:8s} -> {repr(decoded):15s} | Accumulated: {repr(full_string)}")
    except Exception as e:
        print(f"{source}: {block:8s} -> Error: {e}")

print(f"\n\nFINAL STRING: {repr(full_string)}")
```


The script outputs the following result: `//kps:httubstu.69s-1ru/s-1ps:tu.ru///kubshttps:httubs//kru/tu.69s-1`

> You can also use an additional script to try finding a valid link in the resulting string.
>
> ```python
> result = "//kps:httubstu.69s-1ru/s-1ps:tu.ru///kubshttps:httubs//kru/tu.69s-1"# Try to find URL patterns
> import re
> 
> # Look for possible URLs# I see: kubs, tu, ru, http, ps (https), s-1, 69# Try to split into parts
> parts = [
>     "//k", "ps:", "htt", "ubs", "tu.", "69", "s-1", "ru/",
>     "s-1", "ps:", "tu.", "ru/",
>     "//", "kubs", "https:", "htt", "ubs", "//", "k", "ru/",
>     "tu.", "69", "s-1"]
> 
> # Try grouping differently - could be multiple URLs# kubstu.ru is KubSTU (Kuban State Technological University)
> print("Possible URLs:")
> print("1. https://kubstu.ru/")
> print("2. https://s-1.kubstu.ru/")
> print("3. http://s-1.kubstu.ru/")
> print("4. https://kubs69.ru/")
> 
> # Try to extract URL from string
> url_pattern = r'(https?://[^\s/]+)'# But everything is mixed up in the string...# Let's try a different approach - look for repeating patterns
> print("\nString analysis:")
> print(f"kubs appears: {result.count('kubs')} times")
> print(f"tu appears: {result.count('tu')} times")
> print(f"ru appears: {result.count('ru')} times")
> print(f"http appears: {result.count('http')} times")
> print(f"ps: appears: {result.count('ps:')} times")
> print(f"s-1 appears: {result.count('s-1')} times")
> print(f"69 appears: {result.count('69')} times")
> 
> # Try to reconstruct URL
> print("\nPossible decryption:")
> # If ps: = https: (ps is part of https without http)# Then it could be:
> urls = [
>     "https://kubstu.ru/",
>     "https://s-1.kubstu.ru/",
>     "https://kubs69.ru/"]
> 
> for url in urls:
>     print(f"  {url}")
> ```


---

If we look closely at the string, we can see that it contains `https:`, `//kubs`, `tu.ru`, `s-1`, `69`. Putting it all together we get `https://kubstu.ru/s-169`. We follow the link and see the page of our wonderful Department of Cybersecurity and Information Protection. Then we conclude that we went to the wrong place(

We go back to the metadata examination step and notice that there are more blocks in a painfully similar format: `iso=200|Q3N2`, `wb=135|b20v`.

 We go through the metadata again, collect all the blocks and start playing with them to find a working link.

```python
import base64
import itertools

# Blocks from files
blocks_267 = ['b20v', 'ZWJp', 'Q3N2', 'Ly9w', 'aHR0']
blocks_678 = ['cHM6', 'YXN0', 'U3VC', 'bi5j', 'cEs=']

print("=== Decoding each block separately ===\n")

print("From 267.jpg:")
decoded_267 = []
for block in blocks_267:
    try:
        # Add padding if needed
        padded = block + '=' * (4 - len(block) % 4) if len(block) % 4 else block
        decoded = base64.b64decode(padded).decode('utf-8', errors='replace')
        decoded_267.append(decoded)
        print(f"  {block:8s} -> {repr(decoded)}")
    except Exception as e:
        print(f"  {block:8s} -> Error: {e}")

print("\nFrom 678.jpg:")
decoded_678 = []
for block in blocks_678:
    try:
        padded = block + '=' * (4 - len(block) % 4) if len(block) % 4 else block
        decoded = base64.b64decode(padded).decode('utf-8', errors='replace')
        decoded_678.append(decoded)
        print(f"  {block:8s} -> {repr(decoded)}")
    except Exception as e:
        print(f"  {block:8s} -> Error: {e}")

print("\n=== Trying different combinations ===\n")

# All blocks together
all_blocks = blocks_267 + blocks_678
all_decoded = decoded_267 + decoded_678

# 1. Simple concatenation of decoded versions
print("1. Simple concatenation of decoded blocks:")
candidate = ''.join(all_decoded)
print(f"   {repr(candidate)}")

# 2. Concatenation of base64 blocks then decoding
print("\n2. Concatenation of base64 blocks then decoding:")
combined_b64 = ''.join(all_blocks)
try:
    padded = combined_b64 + '=' * (4 - len(combined_b64) % 4) if len(combined_b64) % 4 else combined_b64
    decoded = base64.b64decode(padded).decode('utf-8', errors='replace')
    print(f"   {repr(decoded)}")
except Exception as e:
    print(f"   Error: {e}")

# 3. Interleaving blocks (267, 678, 267, 678...)
print("\n3. Interleaving blocks (267, 678, 267, 678...):")
interleaved = []
for i in range(max(len(blocks_267), len(blocks_678))):
    if i < len(blocks_267):
        interleaved.append(blocks_267[i])
    if i < len(blocks_678):
        interleaved.append(blocks_678[i])

combined_interleaved = ''.join(interleaved)
try:
    padded = combined_interleaved + '=' * (4 - len(combined_interleaved) % 4) if len(combined_interleaved) % 4 else combined_interleaved
    decoded = base64.b64decode(padded).decode('utf-8', errors='replace')
    print(f"   {repr(decoded)}")
except Exception as e:
    print(f"   Error: {e}")

# 4. Reverse order
print("\n4. Reverse block order:")
reversed_blocks = all_blocks[::-1]
combined_reversed = ''.join(reversed_blocks)
try:
    padded = combined_reversed + '=' * (4 - len(combined_reversed) % 4) if len(combined_reversed) % 4 else combined_reversed
    decoded = base64.b64decode(padded).decode('utf-8', errors='replace')
    print(f"   {repr(decoded)}")
except Exception as e:
    print(f"   Error: {e}")

# 5. Show decoded parts for manual assembly
print("\n=== Analysis for manual assembly ===")
print("\nDecoded parts:")
for i, (b267, d267, b678, d678) in enumerate(zip(blocks_267, decoded_267, blocks_678, decoded_678)):
    print(f"  {i+1}. 267: {b267} -> {repr(d267):15s} | 678: {b678} -> {repr(d678)}")
```

The script outputs the following:

`=== Decoding each block separately ===`

> `From 267.jpg: b20v     -> 'om/' ZWJp     -> 'ebi' Q3N2     -> 'Csv' Ly9w     -> '//p' aHR0     -> 'htt'`
>
> `From 678.jpg: cHM6     -> 'ps:' YXN0     -> 'ast' U3VC     -> 'SuB' bi5j     -> 'n.c' cEs=     -> 'pK'`

`=== Trying different combinations ===`

> `Simple concatenation of decoded blocks: 'om/ebiCsv//phttps:astSuBn.cpK'`
>
> `Concatenation of base64 blocks then decoding: 'om/ebiCsv//phttps:astSuBn.cpK'`
>
> `Interleaving blocks (267, 678, 267, 678...): 'om/ps:ebiastCsvSuB//pn.chttpK'`
>
> `Reverse block order: 'pK'`

`=== Analysis for manual assembly ===`

`Decoded parts:`

> `267: b20v -> 'om/'           | 678: cHM6 -> 'ps:'`
>
> `267: ZWJp -> 'ebi'           | 678: YXN0 -> 'ast'`
>
> `267: Q3N2 -> 'Csv'           | 678: U3VC -> 'SuB'`
>
> `267: Ly9w -> '//p'           | 678: bi5j -> 'n.c'`
>
> `267: aHR0 -> 'htt'           | 678: cEs= -> 'pK'`

From this we conclude that there's `https://`, the domain starts with `p` and most likely ends with `n.com/` => we can assume this will be a link to `pastebin.com`.


---

Based on this, we then search for the exact paste address:

```python
import base64  
import re  
import requests  
from itertools import permutations  
  
# Original base64 blocks  
blocks_267 = ['b20v', 'ZWJp', 'Q3N2', 'Ly9w', 'aHR0']  
blocks_678 = ['cHM6', 'YXN0', 'U3VC', 'bi5j', 'cEs=']  
  
  
def decode_block(b64):  
    """Decodes a base64 block with auto-padding"""  
    try:  
        padded = b64 + '=' * (4 - len(b64) % 4) if len(b64) % 4 else b64  
        return base64.b64decode(padded).decode('utf-8', errors='replace')  
    except:  
        return ''  
  
  
# Decode all blocks  
decoded_267 = [decode_block(b) for b in blocks_267]  
decoded_678 = [decode_block(b) for b in blocks_678]  
  
print("Decoded fragments:")  
print(f"267.jpg: {decoded_267}")  
print(f"678.jpg: {decoded_678}")  
print()  
  
# Target domain for search  
TARGET = "pastebin.com"  
  
  
def score_candidate(s, target):  
    """Scores how much a string resembles a link with the target domain"""  
    score = 0  
    s_lower = s.lower()  
  
    if 'https://' in s_lower or 'http://' in s_lower:  
        score += 10  
    if '://' in s_lower:  
        score += 5  
  
    if target in s_lower:  
        score += 50  
    elif all(part in s_lower for part in target.split('.')):  
        score += 20  
  
    if re.match(r'^https?://[a-z0-9.-]+', s_lower):  
        score += 15  
  
    return score  
  
  
def try_fix_url(candidate, target):  
    """Tries to fix obvious URL errors"""  
    fixes = []  
  
    candidate = candidate.replace('httpK', 'https')  
    candidate = candidate.replace('httpS', 'https')  
    candidate = candidate.replace('Kttp', 'http')  
    candidate = candidate.replace('Ps:', 'ps:')  
  
    if target in candidate and '://' not in candidate:  
        fixes.append('https://' + candidate)  
  
    if '://' in candidate and target not in candidate:  
        parts = re.findall(r'[a-z]+', candidate.lower())  
        for i in range(len(parts)):  
            for j in range(i + 1, len(parts) + 1):  
                maybe_domain = '.'.join(parts[i:j])  
                if target in maybe_domain or maybe_domain in target:  
                    fixes.append(candidate.replace(''.join(parts[i:j]), target))  
  
    fixes.append(candidate)  
    return list(set(fixes))  
  
  
def is_valid_pastebin_url(url):  
    """Checks if the link looks like a valid pastebin link"""  
    if not url.startswith(('http://', 'https://')):  
        return False  
    if TARGET not in url:  
        return False  
    pattern = rf'https?://(www.)?{re.escape(TARGET)}/(raw/)?[A-Za-z0-9]+'  
    return bool(re.match(pattern, url))  
  
  
def download_paste(url):  
    """Downloads the pastebin page contents"""  
    if '/raw/' not in url and TARGET in url:  
        raw_url = url.replace(f'://{TARGET}/', f'://{TARGET}/raw/')  
    else:  
        raw_url = url  
  
    try:  
        print(f"Downloading: {raw_url}")  
        response = requests.get(raw_url, timeout=10, headers={  
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'  
        })  
        response.raise_for_status()  
        return response.text  
    except requests.RequestException as e:  
        print(f"Download error: {e}")  
        return None  
  
  
print("Searching for a working pastebin.com link...\n")  
  
all_decoded = decoded_267 + decoded_678  
all_blocks = blocks_267 + blocks_678  
  
best_url = None  
best_score = -1  
  
# Strategy 1: Permutation brute-force of decoded fragments  
print("1. Brute-forcing permutations of decoded fragments...")  
for perm in permutations(all_decoded):  
    candidate = ''.join(perm)  
  
    for fixed in try_fix_url(candidate, TARGET):  
        if is_valid_pastebin_url(fixed):  
            score = score_candidate(fixed, TARGET)  
            if score > best_score:  
                best_score = score  
                best_url = fixed  
                print(f"   Found: {fixed} (score: {score})")  
  
# Strategy 2: Permutation brute-force of base64 blocks -> decoding  
print("\n2. Brute-forcing permutations of base64 blocks with subsequent decoding...")  
for perm in permutations(all_blocks):  
    combined = ''.join(perm)  
    decoded = decode_block(combined)  
  
    for fixed in try_fix_url(decoded, TARGET):  
        if is_valid_pastebin_url(fixed):  
            score = score_candidate(fixed, TARGET)  
            if score > best_score:  
                best_score = score  
                best_url = fixed  
                print(f"   Found: {fixed} (score: {score})")  
  
# Strategy 3: Interleaving blocks (267, 678, 267...)  
print("\n3. Checking block interleaving...")  
interleaved = []  
for i in range(max(len(blocks_267), len(blocks_678))):  
    if i < len(blocks_267): interleaved.append(blocks_267[i])  
    if i < len(blocks_678): interleaved.append(blocks_678[i])  
  
candidate = decode_block(''.join(interleaved))  
for fixed in try_fix_url(candidate, TARGET):  
    if is_valid_pastebin_url(fixed):  
        print(f"   Found: {fixed}")  
        if best_score < 50:  
            best_url = fixed  
            best_score = 50  
  
# Strategy 4: Manual reconstruction based on known fragments  
print("\n4. Manual reconstruction by known patterns...")  
manual_url = "https://pastebin.com/"  
if is_valid_pastebin_url(manual_url):  
    print(f"   Reconstructed: {manual_url}")  
    best_url = manual_url  
    best_score = 100  
  
print(f"\nBest link: {best_url}")  
  
if best_url and best_score > 30:  
    print(f"\nAttempting to download contents...")  
    content = download_paste(best_url)  
  
    if content:  
        print("\n" + "=" * 60)  
        print("PASTEBIN CONTENTS:")  
        print("=" * 60)  
        print(content)  
        print("=" * 60)  
  
        with open('pastebin_content.txt', 'w', encoding='utf-8') as f:  
            f.write(content)  
        print("Saved to pastebin_content.txt")  
    else:  
        print("\nFailed to download contents. Possible reasons:")  
        print("   - The link requires a captcha")  
        print("   - The paste was deleted or is private")  
        print("   - A User-Agent or cookie is needed")  
else:  
    print("\nFailed to find a valid pastebin.com link")  
    print("\nTry manually checking combinations:")  
    print(f"   Fragments: {all_decoded}")
```

After a couple of minutes of the script running, we get the target link `https://pastebin.com/raw/SuBCsvpK` and the flag - `KubSTU{g0d_s4v3_7h3_kr45n0d4r_7r4m}`

Challenge solved)