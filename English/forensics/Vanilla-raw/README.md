# [forensics] Vanilla raw

> **Category:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [memory.rar](./files/img_11.rar) | `rar` |

</details>

---

We received a memory dump, but for some reason we can't analyze it — help us.

Analyzing with strings gives us nothing. Grep by pattern also yields nothing. Although the dump is 2 GB, so there must be something.
When analyzing the entropy and hex dump, we see:

![image.png](./images/img_1.png)

We conclude that most of the memory is zeros, but there are non-zero values. We look for their position. We craft a script that triggers on the first non-zero byte.

## Investigating the environment

At first glance this gives us nothing, but you can notice a possible 4-byte offset. We know the pattern KubSTU{…}. Searching by pattern apparently makes no sense, so we need to look character by character. We look for the character K.

We see this character is present at several offsets. We examine all of them and notice that at a certain offset the flag pattern starts to emerge.

We create a script that extracts the flag completely.

## 🚩 Flag

```
KubSTU{m3m0ry_unl1nk3d_tmpfs_f0r3ns1cs}
```
