# [crypto] Unlucky 13

> **Category:** `crypto`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [solve.py](./files/img_1.py) | `text/x-python` |
| [Unlucky 13.zip](./files/img_5.zip) | `application/x-zip-compressed` |

</details>

---

13 is an unlucky number. Three layers of encryption, thirteen reasons not to try decrypting this. Something leaked — hopefully it'll help you. Flag format KubSTU{}

We open encrypt.py and see that the flag is encrypted in three layers, one after another:
1. XOR with a byte stream from a custom generator cursed_prng(13, ...)
2. Function forgotten_cipher with a key derived from sha256(b"Unlucky13")
3. RSA with e = 3

In output.txt we're given only n, e, and c — the result of RSA encryption. To reach the flag, we need to go through all three layers in reverse order: first RSA, then layer 2, then layer 1.

First, RSA. We notice that e = 3 — a very small public exponent.
RSA works like this: c = m^e mod n, i.e. c = m³ mod n.
But our flag is ~52 bytes (416 bits), and n is 2048 bits. This means m³ is approximately 1248 bits, which is still less than n (2048 bits). So when cubing, the mod doesn't actually do anything, and c = m³ is just a regular number without any modular reduction.
All we need to do is take the cube root of c.

Next, RC4. Now we look at the forgotten_cipher function in encrypt.py. It's never named explicitly, but if you look closely at the code — initialization of array S from 0 to 255, shuffling by key, then stream generation via PRGA — this is RC4.
RC4 is a stream cipher, and it's symmetric, meaning encryption and decryption are the same operation. We run the same data through the same function with the same key.

XOR.

The last layer is the simplest. The flag was XORed with a stream from the custom PRNG with seed=13. XOR is symmetric, so we simply generate the same stream and XOR again.

![image.png](./images/img_2.png)

## 🚩 Flag

```
KubSTU{unLucky_13_l4y3r5_0f_encrypt10n_n0_luck_h3r3}
```
