# [crypto] Not enough part 1

> **Category:** `crypto`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [solve.py](./files/img_2.py) | `text/x-python` |
| [solve.sage](./files/img_5.sage) | `sage` |
| [output.txt](./files/img_7.txt) | `text/plain` |
| [output.txt](./files/img_8.txt) | `text/plain` |
| [output.txt](./files/img_9.txt) | `text/plain` |

</details>

---

During a system dump, some parameters were damaged: only part of the bits of p survived — the last 72 bits were lost. Then a key was derived from the recovered parameters by hashing the secret (this also survived — I think it's AES-GCM?). Flag format KubSTU{}

We have an RSA scheme: N, e, and the ciphertext are given. What immediately stands out is that instead of the full prime p, only its prefix p_hi is provided. From the problem statement it follows that the last 72 bits of p were lost, meaning the number can be represented as p = p_hi · 2^72 + x, where the unknown x is relatively small.

A polynomial modulo N was constructed in Sage, and using small_roots() the missing part of p was recovered. Once the prime was found, all that remained was to compute the second prime q = N / p, then reconstruct Euler's totient phi = (p - 1)(q - 1) and find the private exponent d = e^{-1} mod phi.

![image.png](./images/img_1.png)

RSA here is only used as an intermediate step. From d, via sha256(long_to_bytes(d)) (as stated in the problem), the key for AES-GCM was derived, which was used to encrypt the flag. After recovering d, all that was left was to compute the key, initialize AES-GCM with the specified nonce, ciphertext, and tag, and obtain the original message.

## 🚩 Flag

```
KubSTU{1_h0p3_y0u_solv3d_7hi5_wi7h0ut_4ny_pr0bl3m5}
```
