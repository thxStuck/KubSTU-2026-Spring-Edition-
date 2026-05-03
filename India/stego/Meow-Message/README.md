# [stego] Meow Message

> **श्रेणी:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

---

राइटअप: Meow Message
श्रेणी: स्टेगनोग्राफ़ी, कठिनाई: Easy, फ़्लैग: KubSTU{wh1t3_sp4c3}
चुनौती का विश्लेषण
हमें ASCII-आर्ट बिल्ली और रूसी कविता वाली टेक्स्ट फ़ाइल message.txt दी गई है। पहली नज़र में — बस एक प्यारी तस्वीर और टेक्स्ट।
    /\_____/\
   /  o   o  \
  ( ==  ^  == )
   )         (
  (           )
 ( (  )   (  ) )
(__(__)___(__)__)

  *** MEOW! ***

  म्याऊ-म्याऊ, इंसान!
  मैं सिर्फ़ बिल्ली नहीं,
  मैं रहस्यों की रक्षक हूँ।

  मेरे पंजों में
  एक राज़ है...
  लेकिन वह ऐसे
  दिखता नहीं।
  ध्यान से देखो! :3
विवरण में संकेत: "जो खाली दिखता है, वह वास्तव में खाली नहीं है" — यह अदृश्य कैरेक्टरों की ओर इशारा है।

## चरण 1: छिपा डेटा खोजना

फ़ाइल को hex-एडिटर में खोलते हैं या अप्रिंटेबल कैरेक्टर देखने के लिए कमांड उपयोग करते हैं:
तरीका 1: xxd (Linux/Mac)
xxd message.txt | head -20
तरीका 2: PowerShell (Windows)
Get-Content message.txt | ForEach-Object {
    $_ -replace ' ', '·' -replace "`t", '→'
}
तरीका 3: Python
with open('message.txt', 'r') as f:
    for i, line in enumerate(f):
        visible = line.rstrip('\n').replace(' ', '·').replace('\t', '→')
        print(f"{i+1}: {visible}")
परिणाम: दिखता है कि प्रत्येक पंक्ति के अंत में स्पेस (·) और टैब (→) के संयोजन हैं।

## चरण 2: एन्कोडिंग समझना

यह SNOW शैली की क्लासिक Whitespace-स्टेगनोग्राफ़ी है।
प्रत्येक पंक्ति के अंत में 8 अदृश्य कैरेक्टर हैं
स्पेस = 0, टैब = 1
8 बिट = 1 बाइट = 1 ASCII कैरेक्टर
पहली पंक्ति का उदाहरण:
         /\_/\[स्पेस][टैब][स्पेस][स्पेस][टैब][स्पेस][टैब][टैब]
यह: 01001011 = दशमलव में 75 = कैरेक्टर K

## चरण 3: डीकोडिंग

मैन्युअल तरीका
प्रत्येक पंक्ति के लिए:
टेक्स्ट के बाद trailing whitespace (स्पेस और टैब) निकालें
बाइनरी में बदलें: स्पेस→0, टैब→1
8 बिट को ASCII कैरेक्टर में बदलें
स्वचालित तरीका (Python)
#!/usr/bin/env python3

def decode_snow(filename):
    flag = ""

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')

            text_end = len(line.rstrip())
            trailing = line[text_end:]

            if len(trailing) >= 8:
                bits = ""
                for char in trailing[:8]:
                    if char == ' ':
                        bits += '0'
                    elif char == '\t':
                        bits += '1'

                if len(bits) == 8:
                    ascii_val = int(bits, 2)
                    flag += chr(ascii_val)

    return flag

if __name__ == "__main__":
    flag = decode_snow("../challenge/message.txt")
    print(f"फ़्लैग: {flag}")

## चरण 4: फ़्लैग प्राप्त करना

स्क्रिप्ट चलाते हैं:
python solve.py
परिणाम:

## 🚩 फ़्लैग

```
KubSTU{wh1t3_sp4c3}
```
