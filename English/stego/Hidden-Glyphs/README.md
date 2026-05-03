# [stego] Hidden Glyphs

> **Category:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

## Challenge Name

**"Hidden Glyphs"**

## Category

Steganography / Forensics

## Difficulty

HARD

## Description for Participants

```
Our agent received an encrypted document from an informant. 
Visually it's an ordinary PDF, but we're sure there's a secret message hidden in it.
They say "the width of your gaze determines the depth of your understanding."

Find the flag.

Format: KubSTU{...}
```

## Files

- `stego_challenge.pdf` - PDF document with a hidden flag

---

## WRITEUP (Solution)

### Step 1: Initial Analysis

We open the PDF and see a normal document with text:

- "SECRET DOCUMENT"
- Information about classified data
- Alphabet: ABCDEFGHIJKLMNOPQRSTUVWXYZ
- Hints: "The font hides more than you see..." and "Each glyph has a width."

The hints point to **fonts** and **glyph widths**.

### Step 2: Investigating the PDF Structure

#### Method A: Using strings

```bash
strings stego_challenge.pdf | grep -i "type3\|widths\|font"
```

We find:

- `/Subtype /Type3` — a Type 3 font is used
- `/Widths 70 0 R` — reference to the widths object

#### Method B: pdf-parser (Didier Stevens)

```bash
# Structure overview
pdf-parser.py -a stego_challenge.pdf

# Search for Type 3 fonts
pdf-parser.py -s "/Type3" stego_challenge.pdf

# View the font object
pdf-parser.py -o 71 stego_challenge.pdf
```

#### Method C: Manual Analysis

Open the PDF in a text editor and search for:

```
/Type /Font
/Subtype /Type3
...
/Widths 70 0 R
```

### Step 3: Extracting the Widths Array

We find object 70:

```
70 0 obj
[ 670 840 700 1230 1160 1210 1120 510 950 510 950 1020 480 1100 1160 950 1190 490 1000 1160 1040 530 950 520 1140 510 950 1160 1140 490 990 1070 1210 1250 500 500 ... ]
endobj
```

This is the array of font glyph widths. In PDF, widths are typically specified in "em space" units (1000 = full width).

### Step 4: Analyzing the Values

We notice a pattern in the first values:

- 670, 840, 700, 1230, 1160, 1210, 1120, 510...

If we divide by 10:

- 67, 84, 70, 123, 116, 121, 112, 51...

These are ASCII codes! Let's verify:

- 67 = 'C'
- 84 = 'T'
- 70 = 'F'
- 123 = '{'
- ...

### Step 5: Decoding the Flag

#### Method A: Python script

```python
widths = [670, 840, 700, 1230, 1160, 1210, 1120, 510, 950, 510, 
          950, 1020, 480, 1100, 1160, 950, 1190, 490, 1000, 1160, 
          1040, 530, 950, 520, 1140, 510, 950, 1160, 1140, 490, 
          990, 1070, 1210, 1250]

flag = ''.join([chr(w // 10) for w in widths])
print(flag)
```

#### Method B: CyberChef

1. Paste the numbers
2. From Decimal (space separator)
3. Divide each number by 10
4. From Charcode

#### Method C: Bash one-liner

```bash
echo "670 840 700 1230 1160 1210 1120 510 950 510 950 1020 480 1100 1160 950 1190 490 1000 1160 1040 530 950 520 1140 510 950 1160 1140 490 990 1070 1210 1250" | tr ' ' '\n' | while read n; do printf "\x$(printf '%x' $((n/10)))"; done; echo
```

### Step 6: Result

**FLAG:** `KubSTU{typ3_3_f0nt_w1dth5_4r3_tr1cky}`

---

## Technical Explanation

### What is a Type 3 Font in PDF?

Type 3 is a user-defined font, specified directly in the PDF using PostScript operators. Unlike TrueType or OpenType, Type 3 fonts are fully described within the PDF.

Type 3 font structure:

```
/Type /Font
/Subtype /Type3
/FontBBox [0 0 1500 900]      - font boundaries
/FontMatrix [0.001 0 0 0.001 0 0] - transformation matrix
/CharProcs << ... >>          - glyph drawing procedures
/Encoding << ... >>           - character encoding
/FirstChar 48                 - first character
/LastChar 122                 - last character
/Widths [...]                 - GLYPH WIDTHS ARRAY (the flag is hidden here!)
```

### Why Does This Work?

1. **Widths** is a mandatory array defining the horizontal displacement after each glyph
2. PDF readers use these values for text positioning
3. Values can be arbitrary — text will simply render with different spacing
4. When viewing the PDF normally, nothing suspicious is visible

### Steganographic Method

- Each flag character is encoded as `ASCII_CODE * 10`
- The multiplier of 10 makes the values look like real font widths (typically 300-1000)
- The flag is distributed across the first N positions of the Widths array

---

## Required Tools

- **[pdf-parser.py](http://pdf-parser.py)** - <https://github.com/DidierStevens/DidierStevensSuite>
- **peepdf** - <https://github.com/jesparza/peepdf>
- **qpdf** - <https://github.com/qpdf/qpdf>
- **Python 3** for decoding
- Any hex/text editor

## Useful Commands

```bash
# Extract all objects from PDF
pdf-parser.py -a challenge.pdf

# Find Type 3 fonts
pdf-parser.py -s "/Type3" challenge.pdf

# Dump specific object
pdf-parser.py -o 70 -d obj70.bin challenge.pdf

# QPDF - decompression
qpdf --qdf --object-streams=disable challenge.pdf decoded.pdf
```

## Alternative Challenge Ideas

1. **ToUnicode CMap** — hide the flag in Unicode mapping, so copying text yields different results
2. **Glyph contours** — encode data in glyph contour coordinates
3. **TrueType tables** — use custom tables in a TTF font
4. **Invisible text** — white text on a white background with a custom font

---

## Author

CTF Challenge Generator

## Flag

```
KubSTU{typ3_3_f0nt_w1dth5_4r3_tr1cky}
```


