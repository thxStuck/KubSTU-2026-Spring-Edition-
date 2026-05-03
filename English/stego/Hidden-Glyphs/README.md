# [stego] Hidden Glyphs

> **Category:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

---

Challenge name: "Hidden Glyphs"
Category: Steganography / Forensics
Difficulty: HARD

Challenge description for participants:
Our agent received an encrypted document from an informant.
Visually it's an ordinary PDF, but we're certain it contains a secret message.
They say "the width of your gaze determines the depth of understanding."

Find the flag.

Format: KubSTU{...}

Files: stego_challenge.pdf — PDF document with a hidden flag

WRITEUP (Solution)

## Step 1: Initial analysis

We open the PDF and see a regular document with text:
"SECRET DOCUMENT"
Information about classified data
Alphabet: ABCDEFGHIJKLMNOPQRSTUVWXYZ
Hints: "The font hides more than you see..." and "Each glyph has a width."
The hints point to the font and glyph widths.

## Step 2: Investigating the PDF structure

Method A: Using strings
strings stego_challenge.pdf | grep -i "type3\|widths\|font"
We find:
- /Subtype /Type3 — a Type 3 font is used
- /Widths 70 0 R — reference to the object with widths

Method B: pdf-parser (Didier Stevens)
# Structure overview
pdf-parser.py -a stego_challenge.pdf

# Search for Type 3 fonts
pdf-parser.py -s "/Type3" stego_challenge.pdf

# View the font object
pdf-parser.py -o 71 stego_challenge.pdf

Method C: Manual analysis
Open the PDF in a text editor and search for:
/Type /Font
/Subtype /Type3
...
/Widths 70 0 R

## Step 3: Extracting the Widths array

We find object 70:
70 0 obj
[ 670 840 700 1230 1160 1210 1120 510 950 510 950 1020 480 1100 1160 950 1190 490 1000 1160 1040 530 950 520 1140 510 950 1160 1140 490 990 1070 1210 1250 500 500 ... ]
endobj
This is the array of font glyph widths. In PDF, widths are usually specified in "em space" units (1000 = full width).

## Step 4: Analyzing the values

We notice a pattern in the first values:
670, 840, 700, 1230, 1160, 1210, 1120, 510...
If we divide by 10:
67, 84, 70, 123, 116, 121, 112, 51...
These are ASCII codes! Let's verify:
- 67 = 'C'
- 84 = 'T'
- 70 = 'F'
- 123 = '{'
- ...

## Step 5: Decoding the flag

Method A: Python script
widths = [670, 840, 700, 1230, 1160, 1210, 1120, 510, 950, 510,
          950, 1020, 480, 1100, 1160, 950, 1190, 490, 1000, 1160,
          1040, 530, 950, 520, 1140, 510, 950, 1160, 1140, 490,
          990, 1070, 1210, 1250]

flag = ''.join([chr(w // 10) for w in widths])
print(flag)

Method B: CyberChef
1. Insert numbers
2. From Decimal (space delimiter)
3. Divide each number by 10
4. From Charcode

Method C: Bash one-liner
echo "670 840 700 1230 1160 1210 1120 510 950 510 950 1020 480 1100 1160 950 1190 490 1000 1160 1040 530 950 520 1140 510 950 1160 1140 490 990 1070 1210 1250" | tr ' ' '\n' | while read n; do printf "\\x$(printf '%x' $((n/10)))"; done; echo

## Step 6: Result

FLAG: KubSTU{typ3_3_f0nt_w1dth5_4r3_tr1cky}

Technical explanation:

What is a Type 3 font in PDF?
Type 3 is a custom font defined directly in the PDF using PostScript operators. Unlike TrueType or OpenType, Type 3 fonts are entirely described within the PDF.

Why does this work?
- Widths is a required array that defines horizontal displacement after each glyph
- PDF readers use these values for text positioning
- Values can be arbitrary — the text will simply display with varying spacing
- When viewing the PDF normally, nothing suspicious is visible

Steganographic method:
- Each flag character is encoded as ASCII_CODE * 10
- The multiplier of 10 makes the values look like real font widths (typically 300-1000)
- The flag is distributed across the first N positions of the Widths array

## 🚩 Flag

```
KubSTU{typ3_3_f0nt_w1dth5_4r3_tr1cky}
```
