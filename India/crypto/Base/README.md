# [crypto] Base

> **श्रेणी:** `crypto`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 चुनौती की फ़ाइलें</summary>

| फ़ाइल | प्रकार |
|------|-----|
| [Base.py](./files/img_1.py) | `text/x-python` |
| [Base.txt](./files/img_4.txt) | `text/plain` |
| [Base.txt](./files/img_5.txt) | `text/plain` |

</details>

---

हमने एक अजीब संदेश इंटरसेप्ट किया। ऐसा लगता है कि यह एक लोकप्रिय विधि से एन्कोड किया गया है। यह समझने में मदद करो कि इसमें क्या लिखा है। फ़्लैग का प्रारूप KubSTU()
समाधान: स्ट्रिंग की संरचना और चुनौती का नाम ही चिल्ला-चिल्लाकर कह रहा है कि यह base एन्कोडिंग है, बस इसके विभिन्न प्रकारों को आज़माना बाकी है। केवल base64 सही साबित हुआ।

![image.png](./images/img_2.png)

फ़्लैग: KubSTU(b4s3_64_1s_the_ba5i5)
