# [osint] City that doesn't exist

> **श्रेणी:** `osint`  
> **CTF:** KubSTU CTF 2026 Spring

दक्षिणी रूस के सबसे बड़े शॉपिंग सेंटरों में से एक में बच्चों का थीम पार्क काम करता था — विदेशी अवधारणा का लाइसेंस प्राप्त क्लोन। 2019 में पार्क ने अचानक नाम बदल लिया। कोई आधिकारिक बयान नहीं दिया गया। 

आपका कार्य — क्लोन का प्रबंधन करने वाली कानूनी संस्था की पहचान करना और रूसी संघ के बौद्धिक संपदा रजिस्टर के माध्यम से ट्रेडमार्क पंजीकरण आवेदन की अंतिम तिथि ढूँढना।  

फ़्लैग: KubSTU{प्रबंधन_कंपनी_का_ИНН_ट्रेडमार्क_आवेदन_तिथि_Роспатент_में}  उदाहरण प्रारूप: `KubSTU{1234567890_01.01.2000}`    

---

In one of the largest shopping centers in southern Russia, there was a children's themed park — a licensed clone of a foreign concept. In 2019, the park suddenly changed its name. No official statements were made.  

Your task is to identify the legal entity that managed the clone and find the latest date of trademark registration submission through the Register of Intellectual Property of the Russian Federation.  

Flag: KubSTU{INN_of_managment_company_date_of_trademark_submission_in_Rospatent}  Format example: `KubSTU{1234567890_01.01.2000}`

---

प्रारंभिक डेटा: दक्षिणी रूस का सबसे बड़ा शॉपिंग सेंटर + बच्चों का थीम पार्क

1. Google/Яндекс → «Краснодар Крылатая 2 детский парк» → ZkidZ City → ऐतिहासिक जानकारी की खोज → Minopolis
2. [Biglion.ru](http://Biglion.ru) → ZkidZ City कूपन → शर्तों में भ्रमण नियमों की PDF का लिंक ([st.biglion.ru/upload/2019/pravila_parka_zkidz_city.pdf](http://st.biglion.ru/upload/2019/pravila_parka_zkidz_city.pdf))। दस्तावेज़ के शीर्ष में: «Утверждено Приказом № 03 от 09.01.2019 г. ООО «Эс Эй Риччи Юг»»। लेकिन और गहराई से खोजते हैं।
3. ЕГРЮЛ ([egrul.nalog.ru](http://egrul.nalog.ru)) → पते 350040, Краснодар, Крылатая, 2 से खोज → ООО «Детство +» ИНН 2312206762। मुख्य ОКВЭД: 93.29 — मनोरंजन। 127 कर्मचारी (2018)। निदेशक: Захрабян Р.А.
4. [Rusprofile.ru](http://Rusprofile.ru) → ООО «Детство +» → संस्थापक ООО «Массмаркет» (ИНН 7701722800, Москва, Ленинградский пр-кт, 37 к.9)।
5. [fips.ru](http://fips.ru) → ट्रेडमार्क रजिस्टर → "MINOPOLIS" खोज → आवेदन 2018756480 मिलता है, पंजीकरण 723853, अधिकार धारक: Минополис Уорлдуайд Эдьютейнмент ЛЛК, आवेदन तिथि: 20.12.2018।
6. उसी रजिस्टर में: प्रमाणपत्र संख्या 723853 से «अनुबंध» खंड में खोज → लाइसेंसी ООО «Детство +», अनुबंध पंजीकरण तिथि ट्रेडमार्क आवेदन तिथि से मेल खाती है।

फ़्लैग - `KubSTU{2312206762_20.12.2018}`