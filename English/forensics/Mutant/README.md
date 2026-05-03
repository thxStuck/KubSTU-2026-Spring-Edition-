# [forensics] Mutant

> **Category:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

---

## Legend

Congratulations! You've been admitted to the polytechnic for information security. You've been given educational material. The exam is tomorrow — good luck.

Difficulty: Easy

 

[crypt.pdf](./files/crypt.pdf)

## Problem Description

Inside the PDF file there is encoded and packed data containing the flag.

## Structure

The visible content of the PDF is useless text for solving this challenge. Strings analysis gives us:

 ![img_1.png](./images/img_1.png)

And also


 ![img_2.png](./images/img_2.png)


```javascript
/Contents [4 0 R 5 0 R]
```

This means the page consists of two content streams — object 4 and object 5. Having two streams is suspicious. Object 5 is the encoded or encrypted data.

The stream itself starts with <\~ and ends with \~>, which is characteristic of ASCII85 encoding. Moreover, the presence of /Filter /FlateDecode tells us that the data was first compressed and then encoded.

So we need to write a script that extracts the data between stream and endstream.

## Solution

Since the data is encoded and packed, we first need to decode it. The encoding is clear — ASCII85. Let's write a decoding script.


[exfil.py](./files/exfil.py)

Now let's decompress the data. We create an unpacking script.


[raspak.py](./files/raspak.py)

Let's see what we got.


 ![img_3.png](./images/img_3.png)

The flag is already starting to take shape. At this point you can manually extract the flag character by character, or write another script.

Flag:  KubSTU{pdf_0bj3ct_m4st3r_v2}  