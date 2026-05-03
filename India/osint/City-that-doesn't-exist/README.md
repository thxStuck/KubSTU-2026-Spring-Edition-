# [osint] City that doesn't exist

> **श्रेणी:** `osint`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 चुनौती की फ़ाइलें</summary>

| फ़ाइल | प्रकार |
|------|-----|
| [_Kid's sweet dream.canvas](./files/img_1.canvas) | `canvas` |

</details>

---

दक्षिणी रूस के सबसे बड़े शॉपिंग सेंटरों में से एक में एक बच्चों का थीम पार्क काम करता था — विदेशी अवधारणा का लाइसेंस्ड क्लोन। 2019 में पार्क ने अचानक नाम बदल दिया। कोई आधिकारिक बयान नहीं आया।
आपका कार्य — क्लोन को संचालित करने वाली कानूनी संस्था स्थापित करना और रूसी संघ के बौद्धिक संपदा रजिस्टर के माध्यम से ट्रेडमार्क पंजीकरण आवेदन की अंतिम तारीख ढूंढना।
फ़्लैग: KubSTU{प्रबंधन_कंपनी_का_ИНН_Роспатент_में_ट्रेडमार्क_आवेदन_तारीख}  प्रारूप उदाहरण: KubSTU{1234567890_01.01.2000}
In one of the largest shopping centers in southern Russia, there was a children's themed park — a licensed clone of a foreign concept. In 2019, the park suddenly changed its name. No official statements were made.
Your task is to identify the legal entity that managed the clone and find the latest date of trademark registration submission through the Register of Intellectual Property of the Russian Federation.

## 🚩 फ़्लैग

```
KubSTU{INN_of_managment_company_date_of_trademark_submission_in_Rospatent}
```
प्रारंभिक डेटा: दक्षिणी रूस का सबसे बड़ा शॉपिंग सेंटर + बच्चों का थीम पार्क
Google/Yandex → «Краснодар Крылатая 2 बच्चों का पार्क» → ZkidZ City → ऐतिहासिक जानकारी खोजना → Minopolis
Biglion.ru → ZkidZ City कूपन → शर्तों में विज़िट नियमों का PDF लिंक (st.biglion.ru/upload/2019/pravila_parka_zkidz_city.pdf)। दस्तावेज़ के शीर्ष में: «आदेश № 03 दिनांक 09.01.2019 द्वारा अनुमोदित, ООО «Эс Эй Риччи Юг»»। लेकिन गहराई से खोजते हैं।
ЕГРЮЛ (egrul.nalog.ru) → पते 350040, Краснодар, Крылатая, 2 से खोज → ООО «Детство +» ИНН 2312206762। मुख्य ОКВЭД: 93.29 — मनोरंजन। 127 कर्मचारी (2018)। निदेशक: Захрабян Р.А.
Rusprofile.ru → ООО «Детство +» → संस्थापक ООО «Массмаркет» (ИНН 7701722800, मॉस्को, Ленинградский пр-кт, 37 к.9)।
fips.ru → ट्रेडमार्क रजिस्टर → «MINOPOLIS» खोजें → आवेदन 2018756480 मिलता है, पंजीकरण 723853, अधिकार धारक: Минополис Уорлдуайд Эдьютейнмент ЛЛК, आवेदन तारीख: 20.12.2018।
उसी रजिस्टर में: प्रमाणपत्र संख्या 723853 से «अनुबंध» सेक्शन में खोज → लाइसेंसी ООО «Детство +», अनुबंध पंजीकरण तारीख ट्रेडमार्क आवेदन तारीख से मेल खाती है।
फ़्लैग - KubSTU{2312206762_20.12.2018}
