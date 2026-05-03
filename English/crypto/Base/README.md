# [crypto] Base

> **Category:** `crypto`  
> **CTF:** KubSTU CTF 2026 Spring

---

We intercepted a strange message. It seems to be encoded using a popular method. Help us figure out what it says.  
Flag format KubSTU()

[Base.txt](./files/Base.txt)

---

Solution:
The structure of the string and the challenge name itself practically scream that this is a base encoding — all that's left is to try its variations.
Only base64 turned out to be valid.


 ![img_1.png](./images/img_1.png)


 ![img_2.png](./images/img_2.png)


[Base.py](./files/Base.py)

Flag: KubSTU(b4s3_64_1s_the_ba5i5)


