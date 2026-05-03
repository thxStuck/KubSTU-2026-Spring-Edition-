# [crypto] Furry Cipher

> **Category:** `crypto`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [Solver furry text.py](./files/img_1.py) | `text/x-python` |
| [Furry Cipher.zip](./files/img_7.zip) | `application/x-zip-compressed` |
| [Furry Cipher solve.py](./files/img_12.py) | `text/x-python` |
| [Furry Cipher.py](./files/img_13.py) | `text/x-python` |
| [Furry Cipher solve.py](./files/img_14.py) | `text/x-python` |
| [Furry Cipher.py](./files/img_17.py) | `text/x-python` |

</details>

---

I was scrolling through my email and saw a message from FurryHater_2009) asking to decrypt some strange message, and they also attached two files.
Flag format KubSTU()

Solution: We see a custom encryption algorithm and a large text file full of characters — they're used as padding and need to be removed. The nickname FurryHater_2009) itself hints at which characters are allowed, i.e. ( A-z 0-9 _ () ) — this is our allowed alphabet, meaning the forbidden set includes ( *?&№#"@!=+^\ /|,.<>'" ).

So we remove everything not in our alphabet and get the encrypted flag split into 4 parts. We assemble it and start looking at the second file — the algorithm itself.

After assembling the flag parts we get a complete but encrypted flag. We need to repeat the algorithm but in reverse. We find the modular inverses: 13⁻¹=29, 17⁻¹=11, 19⁻¹=23 mod 62. Using the known flag prefix KubSTU( as known plaintext we find the key_values, build the script, and get the flag.

![image.png](./images/img_2.png)

Flag: KubSTU(h0w_d1d_you_re4d_7ha7_br0_1t_1s_a_furry_c1pher)
