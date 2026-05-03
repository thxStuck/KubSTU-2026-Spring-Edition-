# [stego] Meow Message

> **श्रेणी:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

# Writeup: Meow Message

**श्रेणी:** स्टेगनोग्राफी
**कठिनाई:** Easy
**फ़्लैग:** `KubSTU{wh1t3_sp4c3}`

---

## कार्य का विश्लेषण

हमें एक टेक्स्ट फ़ाइल `message.txt` दी गई है जिसमें बिल्ली का ASCII-आर्ट और रूसी भाषा में एक कविता है। पहली नज़र में — बस एक प्यारी तस्वीर और टेक्स्ट।

```
    /_____/\
   /  o   o  \
  ( ==  ^  == )
   )         (
  (           )
 ( (  )   (  ) )
(__(__)___(__)__)

  *** MEOW! ***

  Мяу-мяу, человек!
  Я не просто кот,
  Я хранитель тайн.

  В моих лапках есть
  секрет один...
  Но его не видно
  просто так.
  Присмотрись! :3
```

विवरण में संकेत कहता है: *"जो खाली दिखता है, वह वास्तव में खाली नहीं है"* — यह अदृश्य अक्षरों की ओर इशारा है।

---

## चरण 1: छिपे हुए डेटा की खोज

फ़ाइल को hex-एडिटर में खोलते हैं या अमुद्रणीय अक्षरों को देखने के लिए कमांड का उपयोग करते हैं:

### तरीका 1: xxd (Linux/Mac)

```bash
xxd message.txt | head -20
```

### तरीका 2: PowerShell (Windows)

```powershell
Get-Content message.txt | ForEach-Object { 
    $_ -replace ' ', '·' -replace "`t", '→' 
}
```

### तरीका 3: Python

```python
with open('message.txt', 'r') as f:
    for i, line in enumerate(f):
        visible = line.rstrip('\n').replace(' ', '·').replace('\t', '→')
        print(f"{i+1}: {visible}")
```

**परिणाम:** हम देखते हैं कि प्रत्येक पंक्ति के अंत में स्पेस (·) और टैब (→) के संयोजन हैं।

---

## चरण 2: एन्कोडिंग को समझना

यह **SNOW** शैली की क्लासिक **Whitespace-स्टेगनोग्राफी** है।

- प्रत्येक पंक्ति के अंत में 8 अदृश्य अक्षर हैं
- **स्पेस = 0**, **टैब = 1**
- 8 बिट = 1 बाइट = 1 ASCII अक्षर

पहली पंक्ति का उदाहरण:

```
         /_/[пробел][таб][пробел][пробел][таб][пробел][таб][таб]
```

यह है: `01001011` = दशमलव में 75 = अक्षर `K`

---

## चरण 3: डिकोडिंग

### मैनुअल तरीका

प्रत्येक पंक्ति के लिए:

1. trailing whitespace निकालें (टेक्स्ट के बाद स्पेस और टैब)
2. बाइनरी में बदलें: स्पेस→0, टैब→1
3. 8 बिट को ASCII अक्षर में बदलें

### स्वचालित तरीका (Python)

```python
#!/usr/bin/env python3

def decode_snow(filename):
    flag = ""
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            
            # Находим позицию последнего непробельного символа
            text_end = len(line.rstrip())
            trailing = line[text_end:]
            
            if len(trailing) >= 8:
                # Берём первые 8 символов whitespace
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
    print(f"Флаг: {flag}")
```

---

## चरण 4: फ़्लैग प्राप्त करना

स्क्रिप्ट चलाते हैं:

```bash
python solve.py
```

**परिणाम:**

```
Флаг: KubSTU{wh1t3_sp4c3}
```

---

## वैकल्पिक समाधान विधियाँ

### 1. SNOW उपयोगिता का उपयोग

```bash
# Установка
apt install stegsnow

# Декодирование
stegsnow -C message.txt
```

### 2. CyberChef

1. CyberChef में फ़ाइल लोड करें
2. "Extract trailing whitespace" ऑपरेशन का उपयोग करें
3. 8 बिट के डिलीमीटर के साथ "From Binary" लागू करें

### 3. Notepad++ में मैनुअल विश्लेषण

1. फ़ाइल खोलें
2. View → Show Symbol → Show All Characters
3. स्पेस/टैब के पैटर्न लिखें और मैन्युअल रूप से डिकोड करें

---

## निष्कर्ष

यह कार्य Whitespace-स्टेगनोग्राफी की बुनियादी तकनीक प्रदर्शित करता है। मुख्य कौशल:

- छिपे हुए डेटा के लिए फ़ाइलों का विश्लेषण
- बाइनरी एन्कोडिंग की समझ
- hex-एडिटर और विश्लेषण उपकरणों के साथ काम करना

**फ़्लैग:** `KubSTU{wh1t3_sp4c3}`
