# [crypto] Not enough part 1

> **Category:** `crypto`  
> **CTF:** KubSTU CTF 2026 Spring

---

During a system dump, some parameters were damaged: only part of the bits of p were preserved — the last 72 bits were lost. Then, from the recovered parameters, a key was derived by hashing the secret (this also survived — I think it's AES-GCM?).
Flag format KubSTU{}  

[output.txt](./files/output.txt)

---


We have an RSA scheme: N, e, and a ciphertext are given. What immediately stands out is that instead of the full prime number p, only its prefix p_hi is provided. From the problem statement, the last 72 bits of p were lost, meaning the number can be represented as p = p_hi · 2^72 + x, where the unknown x is relatively small.

A polynomial modulo N was constructed in Sage, and using small_roots() the missing part of p was recovered. Once the prime was found, the second prime q = N / p was computed, then Euler's totient phi = (p - 1)(q - 1) was calculated, and the private exponent d = e^{-1} mod phi was found.  


 ![img_1.png](./images/img_1.png)


 ![img_2.png](./images/img_2.png)

[solve.sage](./files/solve.sage)

RSA here is only an intermediate step. From d, via sha256(long_to_bytes(d)) (as stated in the problem), a key for AES-GCM was derived, which was used to encrypt the flag. After recovering d, all that remained was to compute the key, initialize AES-GCM with the given nonce, ciphertext, and tag, and obtain the original message.  

 ![img_3.png](./images/img_3.png)


 ![img_4.png](./images/img_4.png)

[solve.py](./files/solve.py)

Flag: KubSTU{1_h0p3_y0u_solv3d_7hi5_wi7h0ut_4ny_pr0bl3m5}


