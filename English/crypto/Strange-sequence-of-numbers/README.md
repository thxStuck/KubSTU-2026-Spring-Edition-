# [crypto] Strange sequence of numbers

> **Category:** `crypto`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [Strange sequence of numbers.py](./files/img_1.py) | `text/x-python` |
| [strange_sequence_of_numbers.txt](./files/img_4.txt) | `text/plain` |

</details>

---

I received a strange document with numbers inside — what could this mean? Flag format KubSTU()

Solution: We see a sequence of numbers. They're quite varied but some of them repeat (for example, the number 99). This might suggest that each code represents a specific character, and all numbers are separated by spaces. Let's try decoding them as ASCII codes.

![image.png](./images/img_2.png)

Flag: KubSTU(asc11_c0d3s_ar3_an_1nteresting_w4y_to_ge7_into_cryp70graphy)
