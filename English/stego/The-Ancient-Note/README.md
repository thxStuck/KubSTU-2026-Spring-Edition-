# [stego] The Ancient Note

> **Category:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

---

Writeup: The Ancient Note
Category: Steganography | Difficulty: Medium | Flag: KubSTU{h1dd3n_truth_b3tw33n}

Challenge description:
We're given a text file ancient_note.txt — supposedly an ancient manuscript from an abandoned library. The text is in English, philosophical reflections on searching for hidden truth.

Initial observations:
When working with the file, you may notice oddities:
- Some words can't be found via Ctrl+F
- When copying text to another location, it behaves strangely
- The file size is larger than expected for this amount of text
- Code editors may show warnings

Solution (Method 1): Via Microsoft Word

## Step 1: Detecting homoglyph characters

1. Open the file in Microsoft Word
2. Enable spell-checking (if disabled)
3. Notice — Word may underline some "normal" words as errors!

Why? Word recognizes that the word mixes letters from different alphabets (Latin + Cyrillic).

Use Find and Replace (Ctrl+H):
- In the "Find" field, type the Latin letter o
- Press "Find Next"
- Some o letters won't be found — these are Cyrillic о!

Alternatively: select all text and change the font to monospace (Consolas, Courier New). Sometimes Cyrillic characters render slightly differently.

## Step 2: Searching for invisible characters in Word

1. Press Ctrl+Shift+8 (or the ¶ button on the toolbar) — show non-printable characters
2. Between regular letters you may see strange markers
3. Copy the text, paste into Find, and remove visible characters — invisible ones will remain

Solution (Method 2): Via Notepad++

## Step 1: Searching for invisible characters

1. Open the file in Notepad++
2. Menu: View → Show Symbol → Show All Characters
3. You'll see dots and markers between regular characters — these are zero-width characters!

## Step 2: Searching for Cyrillic

1. Open Search → Find (Ctrl+F)
2. Go to the Mark tab
3. Enable Regular expression
4. In the search field, enter: [\x{0400}-\x{04FF}]
5. Press Mark All
6. All Cyrillic characters will be highlighted!

Solution (Method 3): Via VS Code

## Step 1: Automatic warning

VS Code automatically warns about suspicious characters!
1. Open the file in VS Code
2. You'll see yellow warnings: "This file contains ambiguous Unicode characters"
3. Hover over the warning — VS Code will show exactly which characters are suspicious

Solution (Method 4): Via online tools

For Homoglyph detection:
- Unicode Text Analyzer: https://www.fontspace.com/unicode/analyzer
- Homoglyph Detector: https://www.irongeek.com/homoglyph-attack-generator.php

For Zero-Width detection:
- Zero-Width Character Detector: https://www.textmagic.com/free-tools/unicode-detector
- Unicode Steganography Decoder: https://330k.github.io/misc_tools/unicode_steganography.html
- CyberChef: https://gchq.github.io/CyberChef/

Solution (Method 5): Via HEX editor

## Step 1: Opening in HxD

1. Download HxD (free hex editor for Windows)
2. Open ancient_note.txt
3. Switch encoding to UTF-8

## Step 2: Searching for zero-width bytes

In UTF-8, zero-width characters are encoded as:
- E2 80 8B — Zero Width Space (U+200B)
- E2 80 8C — Zero Width Non-Joiner (U+200C)

1. Press Ctrl+F → Hex-values tab
2. Search for E2 80 8B and E2 80 8C
3. You'll find many such sequences between regular characters!

## Step 3: Manual decoding

Write down all found zero-width characters in order:
- E2 80 8B = 0
- E2 80 8C = 1
- Get a binary string
- Split into groups of 8 bits
- Convert each group to an ASCII character

Example:
01001011 = 75 = 'K'
01110101 = 117 = 'u'
01100010 = 98 = 'b'
...

Solution (Method 6): Python script

For automation, you can use the solve.py script:
#!/usr/bin/env python3

ZW_ZERO = '\u200b'  # Zero Width Space = 0
ZW_ONE = '\u200c'   # Zero Width Non-Joiner = 1

with open('ancient_note.txt', 'r', encoding='utf-8') as f:
    text = f.read()

zw_chars = [c for c in text if c in (ZW_ZERO, ZW_ONE)]

binary = ''.join('0' if c == ZW_ZERO else '1' for c in zw_chars)

flag = ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))

print(f"FLAG: {flag}")

Run: python solve.py

Flag meaning:

## 🚩 Flag

```
KubSTU{h1dd3n_truth_b3tw33n}
```

- h1dd3n = hidden
- truth = truth
- b3tw33n = between

"Hidden truth between" — a reference to the fact that the flag is hidden between regular characters using zero-width characters.

Techniques used:
| Technique | Description |
|-----------|-------------|
| Homoglyph | Replacing Latin letters with visually identical Cyrillic ones |
| Zero-Width Steganography | Hiding binary data using invisible Unicode characters |
