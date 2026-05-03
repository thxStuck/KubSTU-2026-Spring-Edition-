# [stego] Capybara in Nightmare Land

> **श्रेणी:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

**श्रेणी:** Steganography  

**लेखक:** KubSTU CTF Team  

**फ़्लैग प्रारूप:** `KubSTU{...}` 

## 📝 चुनौती का विवरण

> *KubSTU की कैपीबारा सूचना सुरक्षा की लेक्चर में सो गई और एक अजीब बुरे सपने में पहुँच गई...*
>
> *इस सपने में उसने एक गुप्त संदेश छोड़ा। क्या तुम इसे ढूंढ सकते हो?*
>
> **संकेत:** सब कुछ वैसा नहीं है जैसा दिखता है। गहराई में देखो। 🔍

##  फ़ाइलें

| फ़ाइल | विवरण |
|----|----|
| `capybara_nightmare.png` | विश्लेषण के लिए छवि |

## 🎯 लक्ष्य

छवि के अंदर छिपा हुआ फ़्लैग खोजना।

---

## समाधान

### चरण 1: फ़ाइल विश्लेषण

सबसे पहले मानक उपकरणों से फ़ाइल का विश्लेषण करते हैं:

```bash
file capybara_nightmare.png
# Output: PNG image data, 1024 x 1024, 8-bit/color RGB

binwalk capybara_nightmare.png
# Output दिखाएगा कि अंदर एक ZIP आर्काइव है!
```

`binwalk` उपकरण PNG फ़ाइल के अंदर ZIP-आर्काइव का पता लगाता है। यह **polyglot-फ़ाइल** का संकेत है — ऐसी फ़ाइल जो एक साथ वैध PNG और ZIP दोनों होती है।

### चरण 2: ZIP आर्काइव निकालना

PNG+ZIP polyglot इसलिए काम करता है क्योंकि:

- PNG फ़ाइल की शुरुआत से IEND chunk तक पढ़ा जाता है
- ZIP फ़ाइल के अंत से पढ़ा जाता है (End of Central Directory खोजता है)

आर्काइव निकालते हैं:

```bash
# तरीका 1: सीधे अनज़िप करें
unzip capybara_nightmare.png -d extracted/

# तरीका 2: binwalk के माध्यम से
binwalk -e capybara_nightmare.png
```

आर्काइव के अंदर मिलता है:

- `README.txt` — संकेत
- `encrypted_flag.bin` — एन्क्रिप्टेड फ़्लैग

### चरण 3: README.txt का विश्लेषण

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

संकेत हमें बताते हैं:

1. फ़्लैग XOR से एन्क्रिप्ट किया गया है
2. कुंजी छवि में छिपी है
3. LSB स्टेगनोग्राफी का उपयोग किया गया है
4. पासवर्ड की लंबाई: 19 अक्षर

### चरण 4: LSB निकालना

**LSB (Least Significant Bit)** — स्टेगनोग्राफी की एक तकनीक, जहाँ डेटा छवि के पिक्सेल के सबसे कम महत्वपूर्ण बिट्स में छिपाया जाता है। सबसे कम महत्वपूर्ण बिट में बदलाव आँखों से लगभग अदृश्य होता है।

निकालने के लिए स्क्रिप्ट लिखते हैं:

```python
from PIL import Image
import numpy as np

def extract_lsb(image_path):
    img = Image.open(image_path).convert('RGB')
    pixels = np.array(img).flatten()
    
    bits = ''
    chars = []
    
    for pixel in pixels:
        bits += str(pixel & 1)  # सबसे कम महत्वपूर्ण बिट निकालें
        
        if len(bits) == 8:
            char = chr(int(bits, 2))
            chars.append(char)
            bits = ''
            
            # अंत मार्कर खोजें
            text = ''.join(chars)
            if 'END_LSB' in text:
                return text.split('\x00')[0]
    
    return ''.join(chars[:100])

password = extract_lsb("capybara_nightmare.png")
print(f"Password: {password}")
# Output: N1ghtm4r3_C4py_2026
```

निकाला गया पासवर्ड: `N1ghtm4r3_C4py_2026`

### चरण 5: फ़्लैग डिक्रिप्शन

अब मिले पासवर्ड का उपयोग XOR-डिक्रिप्शन के लिए करते हैं:

```python
def xor_decrypt(encrypted: bytes, key: str) -> str:
    key_bytes = key.encode('utf-8')
    result = []
    for i, byte in enumerate(encrypted):
        result.append(chr(byte ^ key_bytes[i % len(key_bytes)]))
    return ''.join(result)

# एन्क्रिप्टेड फ़्लैग पढ़ें
with open("encrypted_flag.bin", "rb") as f:
    encrypted = f.read()

password = "N1ghtm4r3_C4py_2026"
flag = xor_decrypt(encrypted, password)
print(f"Flag: {flag}")
```

---

## फ़्लैग

```
KubSTU{H0ly_M0ly_CapyHaCk1r}
```

---

## उपयोग किए गए उपकरण

| उपकरण | उद्देश्य |
|----|----|
| `file` | फ़ाइल प्रकार की पहचान |
| `binwalk` | एम्बेडेड डेटा का विश्लेषण और निकालना |
| `unzip` | ZIP आर्काइव को अनपैक करना |
| Python + PIL | LSB निकालना |
| Python | XOR डिक्रिप्शन |

### वैकल्पिक उपकरण

- **zsteg** — LSB स्टेगनोग्राफी का स्वचालित पता लगाना
- **stegsolve** — LSB परतों का दृश्य विश्लेषण
- **010 Editor** — polyglot विश्लेषण के लिए hex-एडिटर

---

## समाधान का संक्षिप्त एल्गोरिथ्म

```
┌─────────────────────────────────────┐
│  capybara_nightmare.png             │
│  (PNG + ZIP polyglot)               │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌────────────┐      ┌────────────────┐
│  PNG के    │      │    ZIP के      │
│  रूप में   │      │    रूप में     │
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

## स्वचालित सॉल्वरों से सुरक्षा

इस टास्क में सुरक्षा के कई स्तर उपयोग किए गए हैं:

1. **Polyglot-फ़ाइल** — सभी उपकरण स्वचालित रूप से इसका पता नहीं लगाते
2. **कस्टम LSB मार्कर** — मानक मार्करों के बजाय `END_LSB`
3. **XOR एन्क्रिप्शन** — कुंजी खोजना आवश्यक है, कुंजी की लंबाई और प्रारूप जाने बिना सरल brute-force संभव नहीं है

---

## लेखक

KubSTU CTF प्रतियोगिताओं के लिए बनाया गया।
