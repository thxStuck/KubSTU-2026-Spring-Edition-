# [forensics] Is the report in English?

> **Category:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [task.py](./files/img_3.py) | `py` |
| [KUBSTU_Financial_Report_2025.pdf](./files/img_4.pdf) | `application/pdf` |

</details>

---

A strange file arrived in the email — a financial report, and it's even in English.

Using the binwalk command you can find an embedded archive; the password for it can be found when opening the document itself or by analyzing it with the strings command. Inside the archive there's a fake flag and a meme.

By analyzing strings, you can see a bunch of base64 strings. You need to build a script that extracts all the strings and decodes them, and we'll get the real flag.

![image.png](./images/img_1.png)

## 🚩 Flag

```
KubSTU{PDF_M3t4d4t4_F0r3ns1cs_4dv4nc3d_Ch4ll3ng3_2025_S3cur3_Emb3dd3d_F1l3_3ncrypt10n_Pr0t0c0l}
```
