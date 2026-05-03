# [stego] Krasnodar tram

> **श्रेणी:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

मुझे क्रास्नोदार के ट्राम बहुत पसंद हैं। यह बहुत सुविधाजनक, तेज़ और सस्ता है। ट्राम वाइब में डूबो और मेरा संदेश खोजो।

 ![img_1.jpg](./images/img_1.jpg)

 ![img_2.jpg](./images/img_2.jpg)


---

मेटाडेटा की जाँच से समाधान शुरू करते हैं।

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

दोनों तस्वीरों के मेटाडेटा में 4 अक्षरों के ब्लॉक और अंत में = दिखाई देते हैं। यह मान सकते हैं कि ये सब एक b64 स्ट्रिंग से संबंधित हैं। सभी ब्लॉक लिख लेते हैं और न्यूरल नेटवर्क से ब्लॉकों को आज़माकर कार्यशील स्ट्रिंग खोजने को कहते हैं।

```python
import base64

# 267.jpg से ब्लॉक (विषम स्थितियाँ)
blocks_267 = ['Ly9r=', 'aHR0=', 'dHUu=', 'cy0x=', 'cy0x=', 'dHUu=', 'Ly9r=', 'aHR0=', 'aHR0=', 'Ly9r=', 'dHUu=', 'cy0x=']

# 678.jpg से ब्लॉक (सम स्थितियाँ)
blocks_678 = ['cHM6=', 'dWJz=', 'Njk==', 'cnUv=', 'cHM6=', 'cnUv=', 'dWJz=', 'cHM6=', 'dWJz=', 'cnUv=', 'Njk==']

print("267.jpg से ब्लॉकों का डिकोडिंग:")
for i, block in enumerate(blocks_267, 1):
    try:
        decoded = base64.b64decode(block).decode('utf-8', errors='replace')
        print(f"  {i:2d}. {block:8s} -> {repr(decoded)}")
    except Exception as e:
        print(f"  {i:2d}. {block:8s} -> त्रुटि: {e}")

print("\n678.jpg से ब्लॉकों का डिकोडिंग:")
for i, block in enumerate(blocks_678, 1):
    try:
        decoded = base64.b64decode(block).decode('utf-8', errors='replace')
        print(f"  {i:2d}. {block:8s} -> {repr(decoded)}")
    except Exception as e:
        print(f"  {i:2d}. {block:8s} -> त्रुटि: {e}")

# अब उन्हें बारी-बारी से मिलाते हैंprint("\n\nब्लॉकों का बारी-बारी मिश्रण (267 विषम, 678 सम):")
interleaved = []
max_len = max(len(blocks_267), len(blocks_678))

for i in range(max_len):
    if i < len(blocks_267):
        interleaved.append(('267', blocks_267[i]))
    if i < len(blocks_678):
        interleaved.append(('678', blocks_678[i]))

# बारी-बारी अनुक्रम को डिकोड करते हैंprint("\nक्रमिक डिकोडिंग:")
full_string = ""for source, block in interleaved:
    try:
        decoded = base64.b64decode(block).decode('utf-8', errors='replace')
        full_string += decoded
        print(f"{source}: {block:8s} -> {repr(decoded):15s} | संचित: {repr(full_string)}")
    except Exception as e:
        print(f"{source}: {block:8s} -> त्रुटि: {e}")

print(f"\n\nअंतिम स्ट्रिंग: {repr(full_string)}")
```


अंत में स्क्रिप्ट यह परिणाम देता है: `//kps:httubstu.69s-1ru/s-1ps:tu.ru///kubshttps:httubs//kru/tu.69s-1`

> इसके अलावा आप एक स्क्रिप्ट का उपयोग कर सकते हैं जो प्राप्त स्ट्रिंग में वैध लिंक खोजने का प्रयास करेगा।
>
> ```python
> result = "//kps:httubstu.69s-1ru/s-1ps:tu.ru///kubshttps:httubs//kru/tu.69s-1"# URL पैटर्न खोजने का प्रयासimport re
> 
> # संभावित URL खोजें# दिखाई देता है: kubs, tu, ru, http, ps (https), s-1, 69# भागों में तोड़ने का प्रयासparts = [
>     "//k", "ps:", "htt", "ubs", "tu.", "69", "s-1", "ru/",
>     "s-1", "ps:", "tu.", "ru/",
>     "//", "kubs", "https:", "htt", "ubs", "//", "k", "ru/",
>     "tu.", "69", "s-1"]
> 
> # अलग तरीके से समूह बनाने का प्रयास - शायद ये कई URL हैं# kubstu.ru - यह KubSTU (कुबान राज्य प्रौद्योगिकी विश्वविद्यालय) हैprint("संभावित URL:")
> print("1. https://kubstu.ru/")
> print("2. https://s-1.kubstu.ru/")
> print("3. http://s-1.kubstu.ru/")
> print("4. https://kubs69.ru/")
> 
> # स्ट्रिंग से URL निकालने का प्रयासurl_pattern = r'(https?://[^\s/]+)'# लेकिन स्ट्रिंग में सब मिला हुआ है...# दूसरा तरीका आज़माते हैं - दोहराए जाने वाले पैटर्न खोजेंprint("\nस्ट्रिंग का विश्लेषण:")
> print(f"kubs मिलता है: {result.count('kubs')} बार")
> print(f"tu मिलता है: {result.count('tu')} बार")
> print(f"ru मिलता है: {result.count('ru')} बार")
> print(f"http मिलता है: {result.count('http')} बार")
> print(f"ps: मिलता है: {result.count('ps:')} बार")
> print(f"s-1 मिलता है: {result.count('s-1')} बार")
> print(f"69 मिलता है: {result.count('69')} बार")
> 
> # URL पुनर्निर्माण का प्रयासprint("\nसंभावित व्याख्या:")
> # अगर ps: = https: (ps यह https का भाग है http के बिना)# तो हो सकता है:urls = [
>     "https://kubstu.ru/",
>     "https://s-1.kubstu.ru/",
>     "https://kubs69.ru/"]
> 
> for url in urls:
>     print(f"  {url}")
> ```


---

यदि स्ट्रिंग को ध्यान से देखें, तो पता चलता है कि यहाँ `https:`, `//kubs`, `tu.ru`, `s-1`, `69` मौजूद हैं। इन्हें जोड़कर `https://kubstu.ru/s-169` मिलता है। लिंक पर जाने पर हमें हमारे शानदार साइबर सुरक्षा और सूचना संरक्षण विभाग का पेज दिखाई देता है। इसके बाद हम निष्कर्ष निकालते हैं कि हम गलत जगह पहुँच गए(

मेटाडेटा देखने के चरण पर वापस जाते हैं और देखते हैं कि इसी तरह के और ब्लॉक हैं जो इस प्रारूप में हैं: `iso=200|Q3N2`, `wb=135|b20v`।

 फिर से मेटाडेटा पर जाते हैं, सभी ब्लॉक इकट्ठा करते हैं और कार्यशील लिंक की तलाश में उनके साथ प्रयोग शुरू करते हैं

```python
import base64
import itertools

# फ़ाइलों से ब्लॉक
blocks_267 = ['b20v', 'ZWJp', 'Q3N2', 'Ly9w', 'aHR0']
blocks_678 = ['cHM6', 'YXN0', 'U3VC', 'bi5j', 'cEs=']

print("=== प्रत्येक ब्लॉक का अलग-अलग डिकोडिंग ===\n")

print("267.jpg से:")
decoded_267 = []
for block in blocks_267:
    try:
        # ज़रूरत पड़ने पर padding जोड़ें        padded = block + '=' * (4 - len(block) % 4) if len(block) % 4 else block
        decoded = base64.b64decode(padded).decode('utf-8', errors='replace')
        decoded_267.append(decoded)
        print(f"  {block:8s} -> {repr(decoded)}")
    except Exception as e:
        print(f"  {block:8s} -> त्रुटि: {e}")

print("\n678.jpg से:")
decoded_678 = []
for block in blocks_678:
    try:
        padded = block + '=' * (4 - len(block) % 4) if len(block) % 4 else block
        decoded = base64.b64decode(padded).decode('utf-8', errors='replace')
        decoded_678.append(decoded)
        print(f"  {block:8s} -> {repr(decoded)}")
    except Exception as e:
        print(f"  {block:8s} -> त्रुटि: {e}")

print("\n=== विभिन्न संयोजन आज़माते हैं ===\n")

# सभी ब्लॉक एक साथall_blocks = blocks_267 + blocks_678
all_decoded = decoded_267 + decoded_678

# 1. डिकोड किए गए ब्लॉकों का सरल जोड़print("1. डिकोड किए गए ब्लॉकों का सरल जोड़:")
candidate = ''.join(all_decoded)
print(f"   {repr(candidate)}")

# 2. base64 ब्लॉकों को जोड़ना फिर डिकोड करनाprint("\n2. base64 ब्लॉकों को जोड़ना फिर डिकोड करना:")
combined_b64 = ''.join(all_blocks)
try:
    padded = combined_b64 + '=' * (4 - len(combined_b64) % 4) if len(combined_b64) % 4 else combined_b64
    decoded = base64.b64decode(padded).decode('utf-8', errors='replace')
    print(f"   {repr(decoded)}")
except Exception as e:
    print(f"   त्रुटि: {e}")

# 3. ब्लॉकों का बारी-बारी मिश्रण (267, 678, 267, 678...)print("\n3. ब्लॉकों का बारी-बारी मिश्रण (267, 678, 267, 678...):")
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
    print(f"   त्रुटि: {e}")

# 4. उल्टा क्रमprint("\n4. ब्लॉकों का उल्टा क्रम:")
reversed_blocks = all_blocks[::-1]
combined_reversed = ''.join(reversed_blocks)
try:
    padded = combined_reversed + '=' * (4 - len(combined_reversed) % 4) if len(combined_reversed) % 4 else combined_reversed
    decoded = base64.b64decode(padded).decode('utf-8', errors='replace')
    print(f"   {repr(decoded)}")
except Exception as e:
    print(f"   त्रुटि: {e}")

# 6. विश्लेषण के लिए प्रत्येक ब्लॉक का परिणाम दिखाते हैंprint("\n=== मैनुअल असेंबली के लिए विश्लेषण ===")
print("\nडिकोड किए गए भाग:")
for i, (b267, d267, b678, d678) in enumerate(zip(blocks_267, decoded_267, blocks_678, decoded_678)):
    print(f"  {i+1}. 267: {b267} -> {repr(d267):15s} | 678: {b678} -> {repr(d678)}")
```

स्क्रिप्ट निम्नलिखित परिणाम देती है:

`=== प्रत्येक ब्लॉक का अलग-अलग डिकोडिंग ===`

> `267.jpg से: b20v     -> 'om/' ZWJp     -> 'ebi' Q3N2     -> 'Csv' Ly9w     -> '//p' aHR0     -> 'htt'`
>
> `678.jpg से: cHM6     -> 'ps:' YXN0     -> 'ast' U3VC     -> 'SuB' bi5j     -> 'n.c' cEs=     -> 'pK'`

`=== विभिन्न संयोजन आज़माते हैं ===`

> `डिकोड किए गए ब्लॉकों का सरल जोड़: 'om/ebiCsv//phttps:astSuBn.cpK'`
>
> `base64 ब्लॉकों को जोड़ना फिर डिकोड करना: 'om/ebiCsv//phttps:astSuBn.cpK'`
>
> `ब्लॉकों का बारी-बारी मिश्रण (267, 678, 267, 678...): 'om/ps:ebiastCsvSuB//pn.chttpK'`
>
> `उल्टा क्रम: 'pK'`

`=== मैनुअल असेंबली के लिए विश्लेषण ===`

`डिकोड किए गए भाग:`

> `267: b20v -> 'om/'           | 678: cHM6 -> 'ps:'`
>
> `267: ZWJp -> 'ebi'           | 678: YXN0 -> 'ast'`
>
> `267: Q3N2 -> 'Csv'           | 678: U3VC -> 'SuB'`
>
> `267: Ly9w -> '//p'           | 678: bi5j -> 'n.c'`
>
> `267: aHR0 -> 'htt'           | 678: cEs= -> 'pK'`

इससे हम निष्कर्ष निकालते हैं कि यहाँ `https://` है, डोमेन `p` से शुरू होता है और संभवतः `n.com/` पर समाप्त होता है => यह अनुमान लगाया जा सकता है कि यह `pastebin.com` का लिंक होगा।


---

इसके आधार पर, आगे पेस्ट का सटीक पता खोजते हैं:

```python
import base64  
import re  
import requests  
from itertools import permutations  
  
# मूल base64 ब्लॉक  
blocks_267 = ['b20v', 'ZWJp', 'Q3N2', 'Ly9w', 'aHR0']  
blocks_678 = ['cHM6', 'YXN0', 'U3VC', 'bi5j', 'cEs=']  
  
  
def decode_block(b64):  
    """base64 ब्लॉक को ऑटो-पैडिंग के साथ डिकोड करता है"""  
    try:  
        padded = b64 + '=' * (4 - len(b64) % 4) if len(b64) % 4 else b64  
        return base64.b64decode(padded).decode('utf-8', errors='replace')  
    except:  
        return ''  
  
  
# सभी ब्लॉकों को डिकोड करते हैं  
decoded_267 = [decode_block(b) for b in blocks_267]  
decoded_678 = [decode_block(b) for b in blocks_678]  
  
print("🔓 डिकोड किए गए खंड:")  
print(f"267.jpg: {decoded_267}")  
print(f"678.jpg: {decoded_678}")  
print()  
  
# खोज के लिए लक्ष्य डोमेन  
TARGET = "pastebin.com"  
  
  
def score_candidate(s, target):  
    """मूल्यांकन करता है कि स्ट्रिंग target डोमेन वाले लिंक से कितनी मिलती-जुलती है"""  
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
    """URL में स्पष्ट त्रुटियों को ठीक करने का प्रयास"""  
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
    """जाँचता है कि लिंक वैध pastebin-लिंक जैसा दिखता है या नहीं"""  
    if not url.startswith(('http://', 'https://')):  
        return False  
    if TARGET not in url:  
        return False  
    pattern = rf'https?://(www.)?{re.escape(TARGET)}/(raw/)?[A-Za-z0-9]+'  
    return bool(re.match(pattern, url))  
  
  
def download_paste(url):  
    """pastebin-पेज की सामग्री डाउनलोड करता है"""  
    if '/raw/' not in url and TARGET in url:  
        raw_url = url.replace(f'://{TARGET}/', f'://{TARGET}/raw/')  
    else:  
        raw_url = url  
  
    try:  
        print(f"⬇️  डाउनलोड कर रहा हूँ: {raw_url}")  
        response = requests.get(raw_url, timeout=10, headers={  
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'  
        })  
        response.raise_for_status()  
        return response.text  
    except requests.RequestException as e:  
        print(f"❌ डाउनलोड त्रुटि: {e}")  
        return None  
  
  
print("🔍 कार्यशील pastebin.com लिंक की खोज...\n")  
  
all_decoded = decoded_267 + decoded_678  
all_blocks = blocks_267 + blocks_678  
  
best_url = None  
best_score = -1  
  
# रणनीति 1: डिकोड किए गए खंडों के क्रमपरिवर्तनों की जाँच  
print("1. डिकोड किए गए खंडों के क्रमपरिवर्तनों की जाँच...")  
for perm in permutations(all_decoded):  
    candidate = ''.join(perm)  
  
    for fixed in try_fix_url(candidate, TARGET):  
        if is_valid_pastebin_url(fixed):  
            score = score_candidate(fixed, TARGET)  
            if score > best_score:  
                best_score = score  
                best_url = fixed  
                print(f"   ✅ मिला: {fixed} (score: {score})")  
  
# रणनीति 2: base64 ब्लॉकों के क्रमपरिवर्तन -> डिकोडिंग  
print("\n2. base64 ब्लॉकों के क्रमपरिवर्तन और फिर डिकोडिंग...")  
for perm in permutations(all_blocks):  
    combined = ''.join(perm)  
    decoded = decode_block(combined)  
  
    for fixed in try_fix_url(decoded, TARGET):  
        if is_valid_pastebin_url(fixed):  
            score = score_candidate(fixed, TARGET)  
            if score > best_score:  
                best_score = score  
                best_url = fixed  
                print(f"   ✅ मिला: {fixed} (score: {score})")  
  
# रणनीति 3: ब्लॉकों का बारी-बारी मिश्रण (267, 678, 267...)  
print("\n3. ब्लॉकों के बारी-बारी मिश्रण की जाँच...")  
interleaved = []  
for i in range(max(len(blocks_267), len(blocks_678))):  
    if i < len(blocks_267): interleaved.append(blocks_267[i])  
    if i < len(blocks_678): interleaved.append(blocks_678[i])  
  
candidate = decode_block(''.join(interleaved))  
for fixed in try_fix_url(candidate, TARGET):  
    if is_valid_pastebin_url(fixed):  
        print(f"   ✅ मिला: {fixed}")  
        if best_score < 50:  
            best_url = fixed  
            best_score = 50  
  
# रणनीति 4: ज्ञात खंडों पर आधारित मैनुअल पुनर्निर्माण  
print("\n4. ज्ञात पैटर्न से मैनुअल पुनर्निर्माण...")  
manual_parts = {  
    'https': ['htt', 'ps:'],  
    '://': ['//'],  
    'pastebin': ['p', 'ast', 'ebi', 'n'],  
    '.com': ['.c', 'om'],  
    '/': ['/']  
}  
  
manual_url = "https://pastebin.com/"  
if is_valid_pastebin_url(manual_url):  
    print(f"   ✅ पुनर्निर्मित: {manual_url}")  
    best_url = manual_url  
    best_score = 100  
  
print(f"\n🎯 सर्वश्रेष्ठ लिंक: {best_url}")  
  
if best_url and best_score > 30:  
    print(f"\n📥 सामग्री डाउनलोड करने का प्रयास...")  
    content = download_paste(best_url)  
  
    if content:  
        print("\n" + "=" * 60)  
        print("📋 PASTEBIN की सामग्री:")  
        print("=" * 60)  
        print(content)  
        print("=" * 60)  
  
        with open('pastebin_content.txt', 'w', encoding='utf-8') as f:  
            f.write(content)  
        print("💾 pastebin_content.txt में सहेजा गया")  
    else:  
        print("\n⚠️ सामग्री डाउनलोड नहीं हो सकी। संभावित कारण:")  
        print("   • लिंक को कैप्चा चाहिए")  
        print("   • पेस्ट हटा दिया गया या निजी है")  
        print("   • User-Agent या cookie आवश्यक है")  
else:  
    print("\n❌ वैध pastebin.com लिंक नहीं मिला")  
    print("\n💡 मैन्युअल रूप से संयोजनों की जाँच करें:")  
    print(f"   खंड: {all_decoded}")
```

कुछ मिनटों के काम के बाद स्क्रिप्ट हमें लक्ष्य लिंक `https://pastebin.com/raw/SuBCsvpK` और फ़्लैग देती है - `KubSTU{g0d_s4v3_7h3_kr45n0d4r_7r4m}`

टास्क हल हो गया)
