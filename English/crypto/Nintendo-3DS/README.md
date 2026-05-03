# [crypto] Nintendo 3DS

> **Category:** `crypto`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [solve.py](./files/img_1.py) | `text/x-python` |
| [output.txt](./files/img_4.txt) | `text/plain` |

</details>

---

Hey, I keep forgetting the algorithm name, but it's something very similar to Nintendo 3DS — help me figure out what was written there^^ Flag format KubSTU{}

We look at the text file and get the input data, mode, and padding, and from the name we understand it's Triple DES.

To solve it, we assemble the key (the key is split into 3 fragments in different encodings that need to be collected) with the IV (the IV is XOR-encrypted with a mask and needs to be restored) and try to decrypt.

All the data should be enough to solve it.

## 🚩 Flag

```
KubSTU{3d3s_n1nt3nd0_cbc_m0d3_n07_h4rd_3n0ugh}
```
