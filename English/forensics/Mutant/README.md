# [forensics] Mutant

> **Category:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [crypt.pdf](./files/img_1.pdf) | `application/pdf` |
| [raspak.py](./files/img_3.py) | `py` |
| [exfil.py](./files/img_4.py) | `py` |

</details>

---

Lore:
Congratulations! You've been admitted to the polytechnic university for information security. You've been given study materials. The exam is tomorrow — good luck.
Difficulty: Easy

Challenge essence:
Inside the PDF file there is encoded and packed data containing the flag.

## Structure

The visible PDF content is useless text for solving the challenge. Analyzing with strings gives us:

And also:

![image.png](./images/img_2.png)

/Contents [4 0 R 5 0 R]
This means the page consists of two content streams — object 4 and object 5. The presence of two streams is suspicious. Object 5 is the encoded or encrypted data.
The stream itself starts with <~ and ends with ~>, which is characteristic of ASCII85 encoding. Moreover, the presence of /Filter /FlateDecode indicates that the data was first compressed, then encoded.
In the end, we need to build a script that extracts the data between stream and endstream.

## Solution

Since the data is encoded and packed, we first need to decode it. The encoding is clear — ASCII85. We build a script for decoding.

Now we need to decompress the data. We create a decompression script.

Let's see what we got.

The flag is already becoming visible. At this point you can either manually extract the flag character by character, or write another script.

## 🚩 Flag

```
KubSTU{pdf_0bj3ct_m4st3r_v2}
```
