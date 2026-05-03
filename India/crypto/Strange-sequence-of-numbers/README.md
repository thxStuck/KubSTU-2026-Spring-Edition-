# [crypto] Strange sequence of numbers

> **श्रेणी:** `crypto`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 चुनौती की फ़ाइलें</summary>

| फ़ाइल | प्रकार |
|------|-----|
| [Strange sequence of numbers.py](./files/img_1.py) | `text/x-python` |
| [strange_sequence_of_numbers.txt](./files/img_4.txt) | `text/plain` |

</details>

---

अंदर संख्याओं वाला एक अजीब दस्तावेज़ मिला, इसका क्या मतलब हो सकता है? फ़्लैग का प्रारूप KubSTU()
समाधान: हम संख्याओं की एक श्रृंखला देखते हैं — वे काफ़ी भिन्न हैं लेकिन कुछ दोहराती हैं (उदाहरण के लिए 99)। इससे यह विचार आ सकता है कि इन कोडों के पीछे कोई विशेष वर्ण है, और सभी संख्याएँ स्पेस से अलग की गई हैं। इन्हें ASCII कोड के रूप में डिक्रिप्ट करने का प्रयास करते हैं।

![image.png](./images/img_2.png)

फ़्लैग: KubSTU(asc11_c0d3s_ar3_an_1nteresting_w4y_to_ge7_into_cryp70graphy)
