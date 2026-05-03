# [stego] Capybara in Nightmare Land

> **श्रेणी:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

---

**श्रेणी:** Steganography
**लेखक:** KubSTU CTF Team
**फ़्लैग प्रारूप:** `KubSTU{...}`
📝 चुनौती का विवरण
KubGTU की कैपीबारा सूचना सुरक्षा की लेक्चर में सो गई और अजीब बुरे सपने में पहुँच गई...
इस सपने में उसने एक गुप्त संदेश छोड़ा। क्या तुम उसे ढूंढ सकते हो?
संकेत: सब कुछ वैसा नहीं है जैसा दिखता है। गहराई से देखो। 🔍
फ़ाइलें
फ़ाइल
विवरण
capybara_nightmare.png
विश्लेषण के लिए चित्र
🎯 लक्ष्य
चित्र के अंदर छिपा फ़्लैग ढूंढना।

## समाधान

## चरण 1: फ़ाइल विश्लेषण

सबसे पहले मानक टूल से फ़ाइल का विश्लेषण करते हैं:
file capybara_nightmare.png
# Output: PNG image data, 1024 x 1024, 8-bit/color RGB

binwalk capybara_nightmare.png
# Output दिखाएगा कि अंदर ZIP आर्काइव है!
binwalk PNG फ़ाइल के अंदर ZIP-आर्काइव पाता है। यह polyglot-फ़ाइल का संकेत है — एक फ़ाइल जो एक साथ वैध PNG और ZIP दोनों है।

## चरण 2: ZIP आर्काइव निकालना

PNG+ZIP polyglot काम करता है क्योंकि:
PNG फ़ाइल की शुरुआत से IEND chunk तक पढ़ा जाता है
ZIP फ़ाइल के अंत से पढ़ा जाता है (End of Central Directory ढूंढता है)
आर्काइव निकालते हैं:
# तरीका 1: बस अनज़िप करें
unzip capybara_nightmare.png -d extracted/

# तरीका 2: binwalk से
binwalk -e capybara_nightmare.png
आर्काइव में मिलता है:
README.txt — संकेत
encrypted_flag.bin — एन्क्रिप्टेड फ़्लैग

## चरण 3: README.txt का विश्लेषण

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
संकेत बताते हैं:
फ़्लैग XOR एन्क्रिप्टेड है
कुंजी चित्र में छिपी है
LSB स्टेगनोग्राफ़ी उपयोग की गई
पासवर्ड की लंबाई: 19 कैरेक्टर

## चरण 4: LSB निकालना

LSB (Least Significant Bit) — स्टेगनोग्राफ़ी तकनीक जहाँ डेटा पिक्सेल के निम्न बिटों में छिपाया जाता है। निम्न बिट बदलना आँखों को लगभग नज़र नहीं आता।
निकालने के लिए स्क्रिप्ट लिखते हैं:
from PIL import Image
import numpy as np

def extract_lsb(image_path):
    img = Image.open(image_path).convert('RGB')
    pixels = np.array(img).flatten()

    bits = ''
    chars = []

    for pixel in pixels:
        bits += str(pixel & 1)

        if len(bits) == 8:
            char = chr(int(bits, 2))
            chars.append(char)
            bits = ''

            text = ''.join(chars)
            if 'END_LSB' in text:
                return text.split('\x00')[0]

    return ''.join(chars[:100])

password = extract_lsb("capybara_nightmare.png")
print(f"Password: {password}")
# Output: N1ghtm4r3_C4py_2026
निकाला गया पासवर्ड: N1ghtm4r3_C4py_2026

## चरण 5: फ़्लैग डिक्रिप्शन

अब मिले पासवर्ड से XOR-डिक्रिप्शन करते हैं:
def xor_decrypt(encrypted: bytes, key: str) -> str:
    key_bytes = key.encode('utf-8')
    result = []
    for i, byte in enumerate(encrypted):
        result.append(chr(byte ^ key_bytes[i % len(key_bytes)]))
    return ''.join(result)

with open("encrypted_flag.bin", "rb") as f:
    encrypted = f.read()

password = "N1ghtm4r3_C4py_2026"
flag = xor_decrypt(encrypted, password)
print(f"Flag: {flag}")

## 🚩 फ़्लैग

```
KubSTU{H0ly_M0ly_CapyHaCk1r}
```
उपयोग किए गए टूल
टूल
उद्देश्य
file
फ़ाइल प्रकार पहचानना
binwalk
एम्बेडेड डेटा का विश्लेषण और निकालना
unzip
ZIP आर्काइव अनपैक करना
Python + PIL
LSB निकालना
Python
XOR डिक्रिप्शन
वैकल्पिक टूल
zsteg — स्वचालित LSB स्टेगनोग्राफ़ी पहचान
stegsolve — LSB परतों का दृश्य विश्लेषण
010 Editor — polyglot विश्लेषण के लिए hex-संपादक
संक्षिप्त समाधान एल्गोरिदम
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
│  पासवर्ड: │      │ encrypted_flag │
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
स्वचालित समाधानकर्ताओं से सुरक्षा
यह चुनौती सुरक्षा के कई स्तरों का उपयोग करती है:
Polyglot-फ़ाइल — सभी टूल स्वचालित रूप से नहीं पहचानते
कस्टम LSB मार्कर — मानक मार्करों के बजाय END_LSB
XOR एन्क्रिप्शन — कुंजी ढूंढनी होगी, कुंजी की लंबाई और प्रारूप जाने बिना सरल brute-force संभव नहीं
लेखक
KubGTU CTF प्रतियोगिताओं के लिए निर्मित।
