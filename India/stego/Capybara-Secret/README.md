# [stego] Capybara Secret

> **श्रेणी:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

---

चुनौती की जानकारी
श्रेणी: स्टेगनोग्राफ़ी
कठिनाई: Medium

## 🚩 फ़्लैग

```
KubSTU{W0W_1ncred1ble_capyba6a}
```

## चरण 1: चित्र का विश्लेषण

challenge.jpg फ़ाइल प्राप्त करके, सबसे पहले छिपी जानकारी की जाँच करते हैं। स्टेगनोग्राफ़ी में कई लोकप्रिय विधियाँ हैं:
LSB (Least Significant Bit) — पिक्सेल के निम्न बिटों में डेटा छिपाना
मेटाडेटा (EXIF) — फ़ाइल की सेवा जानकारी में छिपाना
फ़ाइल जोड़ना — फ़ाइल के अंत में डेटा जोड़ना
और अन्य...
सरल से शुरू करते हैं — मेटाडेटा जाँचते हैं।

## चरण 2: EXIF-मेटाडेटा निकालना

तरीका 1: ExifTool (अनुशंसित)
exiftool challenge.jpg
आउटपुट में कई फ़ील्ड दिखेंगी। XP Comment फ़ील्ड पर ध्यान दें:
XP Comment                      : XhoFGH{J0J_1aperq1oyr_pnclon6n}
तरीका 2: Python + Pillow
from PIL import Image
from PIL.ExifTags import TAGS

img = Image.open('challenge.jpg')
exif_data = img._getexif()

for tag_id, value in exif_data.items():
    tag = TAGS.get(tag_id, tag_id)
    print(f"{tag}: {value}")
तरीका 3: ऑनलाइन सेवाएँ
ऑनलाइन EXIF viewer उपयोग कर सकते हैं:
https://exifinfo.org/
https://www.metadata2go.com/

## चरण 3: मिली स्ट्रिंग का विश्लेषण

मिली स्ट्रिंग: XhoFGH{J0J_1aperq1oyr_pnclon6n}
यह स्ट्रिंग:
फ़्लैग प्रारूप जैसी दिखती है (XXXXX{...} संरचना)
अपठनीय टेक्स्ट है
शायद सरल सिफ़र से एन्क्रिप्टेड है
फ़्लैग प्रारूप KubSTU{...} है, और हम XhoFGH{...} देख रहे हैं।
ROT13 सिफ़र की परिकल्पना जाँचते हैं:
K → X (13 का शिफ़्ट)
u → h (13 का शिफ़्ट)
b → o (13 का शिफ़्ट)
...
पैटर्न मिलता है — यह ROT13 है!

## चरण 4: ROT13 डिक्रिप्शन

तरीका 1: ऑनलाइन डीकोडर
कोई भी ROT13 डीकोडर उपयोग करें: https://rot13.com/
तरीका 2: Python
import codecs

encrypted = "XhoFGH{J0J_1aperq1oyr_pnclon6n}"
decrypted = codecs.decode(encrypted, 'rot_13')
print(decrypted)
तरीका 3: Linux/Bash
echo "XhoFGH{J0J_1aperq1oyr_pnclon6n}" | tr 'A-Za-z' 'N-ZA-Mn-za-m'
तरीका 4: CyberChef
CyberChef में "ROT13" रेसिपी उपयोग करें: https://gchq.github.io/CyberChef/#recipe=ROT13(true,true,false,13)

## समाधान

ROT13 लगाने के बाद फ़्लैग मिलता है:
```
KubSTU{W0W_1ncred1ble_capyba6a}
```
समाधान के लिए क्या जानना ज़रूरी था
EXIF मेटाडेटा — JPEG चित्रों में XPComment, XPKeywords जैसी गैर-मानक फ़ील्ड सहित मेटाडेटा होता है (Windows विशिष्ट)
EXIF के लिए टूल — exiftool, Python लाइब्रेरी, ऑनलाइन सेवाएँ
ROT13 सिफ़र — सरल प्रतिस्थापन सिफ़र, जहाँ प्रत्येक अक्षर वर्णमाला में 13 स्थान आगे के अक्षर से बदला जाता है। ROT13 अपना स्वयं का व्युत्क्रम है (दो बार लगाने पर मूल टेक्स्ट वापस मिलता है)
सावधानी — कचरा जैसा दिखने वाला सब कचरा नहीं होता। एन्क्रिप्टेड डेटा अपठनीय दिख सकता है, लेकिन उसकी एक निश्चित संरचना होती है
