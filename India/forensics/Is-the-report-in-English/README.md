# [forensics] Is the report in English?

> **श्रेणी:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 चुनौती की फ़ाइलें</summary>

| फ़ाइल | प्रकार |
|------|-----|
| [task.py](./files/img_3.py) | `py` |
| [KUBSTU_Financial_Report_2025.pdf](./files/img_4.pdf) | `application/pdf` |

</details>

---

मेल पर एक अजीब फ़ाइल आई, वित्तीय रिपोर्ट, और वह भी अंग्रेज़ी में।

binwalk कमांड का उपयोग करके एक एम्बेडेड आर्काइव मिल सकता है, उसका पासवर्ड दस्तावेज़ खोलते समय या strings कमांड से विश्लेषण करने पर मिलता है। आर्काइव में नकली फ़्लैग और एक मज़ाकिया तस्वीर है।
strings का विश्लेषण करने पर बहुत सारी base64 स्ट्रिंग दिखाई देती हैं, एक स्क्रिप्ट बनानी होगी जो सभी स्ट्रिंग निकालेगी और उन्हें डीकोड करेगी और हमें असली फ़्लैग मिल जाएगा।

![image.png](./images/img_1.png)

## 🚩 फ़्लैग

```
KubSTU{PDF_M3t4d4t4_F0r3ns1cs_4dv4nc3d_Ch4ll3ng3_2025_S3cur3_Emb3dd3d_F1l3_3ncrypt10n_Pr0t0c0l}
```
