# [stego] The Ancient Note

> **Category:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

# Writeup: The Ancient Note

**Category:** Steganography
**Difficulty:** Medium
**Flag:** `KubSTU{h1dd3n_truth_b3tw33n}`

---

## Challenge Description

We're given a text file `ancient_note.txt` — supposedly an ancient manuscript from an abandoned library. The text is in English — philosophical reflections on the search for hidden truth.

---

## Initial Observations

When working with the file, you may notice oddities:

- Some words can't be found via Ctrl+F
- When copying the text elsewhere, it behaves strangely
- File size is larger than expected for this volume of text
- Code editors may show warnings

---

## Solution (Method 1): Via Microsoft Word

### Step 1: Detecting Homoglyph Characters

1. Open the file in **Microsoft Word**
2. Enable spell check (if disabled)
3. Notice — Word may underline some "ordinary" words as errors!

**Why?** Word recognizes that the word mixes letters from different alphabets (Latin + Cyrillic).

4. Use **Find and Replace** (Ctrl+H):
   - In the "Find" field, enter the Latin letter `o`
   - Click "Find Next"
   - Some `o` letters won't be found — these are Cyrillic `о`!
5. Alternatively: select all text and change the font to **monospaced** (Consolas, Courier New). Sometimes Cyrillic characters render slightly differently.

### Step 2: Searching for Invisible Characters in Word

1. Press **Ctrl+Shift+8** (or the ¶ button on the toolbar) — show non-printing characters
2. Between regular letters, you may see strange markers
3. Copy the text, paste into **Find**, and delete visible characters — invisible ones will remain

---

## Solution (Method 2): Via Notepad++

### Step 1: Searching for Invisible Characters

1. Open the file in **Notepad++**
2. Menu: **View → Show Symbol → Show All Characters**
3. You'll see dots and markers between regular characters — these are zero-width characters!


### Step 2: Searching for Cyrillic

1. Open **Search → Find** (Ctrl+F)
2. Go to the **Mark** tab
3. Enable **Regular expression**
4. In the search field, enter: `[\x{0400}-\x{04FF}]`
5. Click **Mark All**
6. All Cyrillic characters will be highlighted!

### Step 3: Viewing Character Codes

1. Install the **HEX-Editor** plugin or use **Plugins → Converter → ASCII to HEX**
2. Select a suspicious character
3. Check its code in the status bar at the bottom

---

## Solution (Method 3): Via VS Code

### Step 1: Automatic Warning

VS Code **automatically warns** about suspicious characters!

1. Open the file in VS Code
2. You'll see yellow warnings: *"This file contains ambiguous Unicode characters"*
3. Hover over the warning — VS Code will show which characters are suspicious

### Step 2: Analysis Extensions

Install the **Unicode Revealer** or **Gremlins tracker** extension:

- Highlights all non-standard Unicode characters
- Shows zero-width characters with special markers

---

## Solution (Method 4): Via Online Tools

### For Finding Homoglyphs:

1. **Unicode Text Analyzer**: <https://www.fontspace.com/unicode/analyzer>
   - Paste text
   - Shows the code of each character
   - Cyrillic letters will be in range U+0400 - U+04FF
2. **Homoglyph Detector**: <https://www.irongeek.com/homoglyph-attack-generator.php>
   - Detects mixed alphabets

### For Finding Zero-Width:

1. **Zero-Width Character Detector**: <https://www.textmagic.com/free-tools/unicode-detector>
2. **Unicode Steganography Decoder**: <https://330k.github.io/misc_tools/unicode_steganography.html>
   - Specifically for decoding zero-width steganography!
   - Paste text → automatically extracts hidden message
3. **CyberChef**: <https://gchq.github.io/CyberChef/>
   - Recipe: `Find/Replace` with regex to extract zero-width
   - Then `From Binary` for decoding

---

## Solution (Method 5): Via HEX Editor

### Step 1: Opening in HxD

1. Download **HxD** (free hex editor for Windows)
2. Open `ancient_note.txt`
3. Switch encoding to UTF-8

### Step 2: Searching for Zero-Width Bytes

In UTF-8, zero-width characters are encoded as:

- `E2 80 8B` — Zero Width Space (U+200B)
- `E2 80 8C` — Zero Width Non-Joiner (U+200C)

1. Press **Ctrl+F** → **Hex-values** tab
2. Search for `E2 80 8B` and `E2 80 8C`
3. You'll find numerous such sequences between regular characters!

### Step 3: Manual Decoding

1. Write out all found zero-width characters in order:
   - `E2 80 8B` = 0
   - `E2 80 8C` = 1
2. Get a binary string
3. Split into groups of 8 bits
4. Convert each group to an ASCII character

**Example:**

```
01001011 = 75 = 'K'
01110101 = 117 = 'u'
01100010 = 98 = 'b'
...
```

---

## Solution (Method 6): Python Script

For automation, you can use the script `solve.py`:

```python
#!/usr/bin/env python3

ZW_ZERO = '\u200b'  # Zero Width Space = 0
ZW_ONE = '\u200c'   # Zero Width Non-Joiner = 1

with open('ancient_note.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract zero-width characters
zw_chars = [c for c in text if c in (ZW_ZERO, ZW_ONE)]

# Convert to binary string
binary = ''.join('0' if c == ZW_ZERO else '1' for c in zw_chars)

# Decode to ASCII
flag = ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))

print(f"FLAG: {flag}")
```

Run: `python solve.py`

---

## Step-by-Step Solution Logic

```
┌─────────────────────────────────────────────────────────────┐
│  1. Open the file, notice oddities                           │
│     └─> Search doesn't work, file size larger than expected  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Analyze Unicode characters                               │
│     └─> Find Cyrillic among Latin (HOMOGLYPH)                │
│     └─> Realize: something is hidden here!                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Search for other hidden data                             │
│     └─> Find Zero-Width characters between letters           │
│     └─> 224 characters = 224 bits = 28 bytes                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Decode Zero-Width                                        │
│     └─> U+200B = 0, U+200C = 1                              │
│     └─> Binary string → ASCII                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  5. Get the flag!                                            │
│     └─> KubSTU{h1dd3n_truth_b3tw33n}                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Flag Meaning

`KubSTU{h1dd3n_truth_b3tw33n}`

- `h1dd3n` = hidden
- `truth` = truth
- `b3tw33n` = between

"Hidden truth between" — a reference to the fact that the flag is hidden **between** regular characters using zero-width characters.

---

## Techniques Used

| Technique | Description |
|----|----|
| **Homoglyph** | Replacing Latin letters with visually identical Cyrillic ones |
| **Zero-Width Steganography** | Hiding binary data using invisible Unicode characters |

---

## Useful Tools

| Tool | Purpose |
|----|----|
| Microsoft Word | Spell check reveals mixed alphabets |
| Notepad++ | Show all characters, regex search |
| VS Code | Automatic Unicode warnings |
| HxD | Raw byte viewer |
| CyberChef | Universal decoder |
| Unicode Analyzer (online) | Character code analysis |
| Python | Solution automation |

---

## Possible Hints

This section is intended **for CTF organizers** — hint options that can be used to help participants.

### Option 1: Hints in the Task Description (Legend)

Hints embedded in the task description text:

| Level | Hint Text |
|----|----|
| **Minimal** | *"At first glance ordinary text, but something's not right..."* |
| **Easy** | *"Strangely, some words in the document can't be found via search..."* |
| **Medium** | *"Researchers noticed that when copying the text, it becomes longer than it appears"* |
| **Obvious** | *"They say the author was a polyglot and loved mixing alphabets"* |

---

### Option 2: Paid Hints (Score Penalty)

Hint system with score reduction:

```
Hint 1 (-10%):  "Not everything that looks like Latin is Latin"
Hint 2 (-15%):  "Try copying the text into different editors"
Hint 3 (-20%):  "Between the lines... no, literally — between the characters"
Hint 4 (-25%):  "Unicode hides more than it shows"
Hint 5 (-30%):  "Zero-Width Space, Zero-Width Non-Joiner — your friends"
Hint 6 (-50%):  "Use: https://330k.github.io/misc_tools/unicode_steganography.html"
```

---

### Option 3: Hints via Task Metadata

| Element | How to Use | Example |
|----|----|----|
| **Title** | Suggestive name | "Between the Lines", "Invisible Ink", "What You Don't See" |
| **Tags** | Pointing to the technique | `unicode`, `text`, `encoding`, `invisible` |
| **Image** | Visual hint | Image of a magnifying glass, blank page, or "invisible ink" |
| **Author** | Hint pseudonym | "Mr. Unicode", "ZeroWidth" |

---

### Option 4: Hints in the File Itself

**At the beginning of the file (HTML comment):**

```
<!-- Hint: Not everything is what it seems. Check your encodings. -->
```

**At the end of the file (meta info):**

```
[Note: Document scanned with Unicode-aware OCR v2.0]
```

**In a "random" text line:**

```
P.S. The devil is in the details... or perhaps in the spaces between them.
```

---

### Option 5: Hint via File Size

State the size and character count in the task description:

> *"The file takes up 1352 bytes, although there's only about 900 visible characters. Where did the rest of the bytes go?"*

Or more subtle:

> *"File size: 1352 bytes | Visible characters: ~900"*

---

### Option 6: Free Starting Hint

One free hint, available immediately:

> *"Tip: open the file in VS Code or check it in a hex editor. Pay attention to the warnings."*

---

### Recommended Set for Medium Difficulty

Optimal combination for difficulty balance:

1. **In description:** *"At first glance ordinary text, but something's not right..."*
2. **Free hint:** *"Try copying the text into different editors"*
3. **Hint 1 (-15%):** *"Unicode hides more than it shows"*
4. **Hint 2 (-30%):** *"Look for Zero-Width characters"*
5. **Hint 3 (-50%):** *"U+200B = 0, U+200C = 1. Decode as binary."*

---

### Option 7: Progressive Stage-Based Hints

Separate hints for each solution stage:

**Stage 1 — Detecting the Anomaly:**

- *"Ctrl+F doesn't always find what you see"*
- *"File size is suspiciously large"*

**Stage 2 — Homoglyph:**

- *"Cyrillic and Latin are twins but not siblings"*
- *"U+043E looks like U+006F, but they're not the same"*

**Stage 3 — Zero-Width:**

- *"What's between the letters? Emptiness? Or not?"*
- *"Zero Width Space (U+200B) and Zero Width Non-Joiner (U+200C)"*

**Stage 4 — Decoding:**

- *"Two types of invisible characters = binary code"*
- *"224 bits = 28 ASCII characters"*

---

## Additional Resources

- [Unicode Zero-Width Characters](https://en.wikipedia.org/wiki/Zero-width_space)
- [Homoglyph Attack](https://en.wikipedia.org/wiki/Homoglyph)
- [CyberChef](https://gchq.github.io/CyberChef/)
- [Unicode Steganography Tool](https://330k.github.io/misc_tools/unicode_steganography.html)


