# [crypto] Base

> **Category:** `crypto`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [Base.py](./files/img_1.py) | `text/x-python` |
| [Base.txt](./files/img_4.txt) | `text/plain` |
| [Base.txt](./files/img_5.txt) | `text/plain` |

</details>

---

We intercepted a strange message. It seems to be encoded with a popular method. Help us figure out what it says. Flag format KubSTU()

Solution: The structure of the string and the challenge name itself practically scream that this is a base encoding — all that's left is to try different variants. The only valid one turns out to be base64.

![image.png](./images/img_2.png)

Flag: KubSTU(b4s3_64_1s_the_ba5i5)
