# [stego] Meow Message

> **Category:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

---

Writeup: Meow Message
Category: Steganography | Difficulty: Easy | Flag: KubSTU{wh1t3_sp4c3}

Challenge analysis:
We're given a text file message.txt with ASCII art of a cat and a poem. At first glance — just a cute picture with text.
    /\_____/\
   /  o   o  \
  ( ==  ^  == )
   )         (
  (           )
 ( (  )   (  ) )
(__(__)___(__)__)

  *** MEOW! ***

  Meow-meow, human!
  I'm not just a cat,
  I'm a keeper of secrets.

  In my paws there is
  one secret...
  But it can't be seen
  just like that.
  Look closely! :3

The hint in the description says: "Not everything that appears empty is actually empty" — this hints at invisible characters.

## Step 1: Detecting hidden data

We open the file in a hex editor or use a command to view non-printable characters:

Method 1: xxd (Linux/Mac)
xxd message.txt | head -20

Method 2: PowerShell (Windows)
Get-Content message.txt | ForEach-Object {
    $_ -replace ' ', '·' -replace "`t", '→'
}

Method 3: Python
with open('message.txt', 'r') as f:
    for i, line in enumerate(f):
        visible = line.rstrip('\n').replace(' ', '·').replace('\t', '→')
        print(f"{i+1}: {visible}")

Result: We see that at the end of each line there are combinations of spaces (·) and tabs (→).

## Step 2: Understanding the encoding

This is classic Whitespace steganography in the SNOW style.
- Each line contains 8 invisible characters at the end
- Space = 0, Tab = 1
- 8 bits = 1 byte = 1 ASCII character

Example from the first line:
         /\_/\[space][tab][space][space][tab][space][tab][tab]
This is: 01001011 = 75 in decimal = character K

## Step 3: Decoding

Manual method:
For each line:
1. Extract trailing whitespace (spaces and tabs after text)
2. Convert to binary: space→0, tab→1
3. Convert 8 bits to ASCII character

Automated method (Python):
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
    print(f"Flag: {flag}")

## Step 4: Getting the flag

We run the script:
python solve.py
Result:

## 🚩 Flag

```
KubSTU{wh1t3_sp4c3}
```

Alternative solving methods:

1. Using the SNOW utility
# Installation
apt install stegsnow

# Decoding
stegsnow -C message.txt

2. CyberChef
- Load the file in CyberChef
- Use the "Extract trailing whitespace" operation
- Apply "From Binary" with 8-bit delimiter

3. Manual analysis in Notepad++
- Open the file
- View → Show Symbol → Show All Characters
- Write down the space/tab patterns and decode manually

Takeaways:
The challenge demonstrates the basic Whitespace steganography technique. Key skills:
- Analyzing files for hidden data
- Understanding binary encoding
- Working with hex editors and analysis tools
