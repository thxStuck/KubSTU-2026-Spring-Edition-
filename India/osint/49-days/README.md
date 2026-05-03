# [osint] 49 days

> **श्रेणी:** `osint`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 चुनौती की फ़ाइलें</summary>

| फ़ाइल | प्रकार |
|------|-----|
| [_Kid's sweet dream.canvas](./files/img_1.canvas) | `canvas` |

</details>

---

कठिनाई: nightmare

बच्चों के थीम पार्क ब्रांड का अंतर्राष्ट्रीय कॉपीराइट धारक कई न्यायक्षेत्रों में कानूनी संस्थाओं की श्रृंखला के माध्यम से कार्य करता था। इस श्रृंखला की मुख्य कड़ी — एक स्विस कंपनी — अलग नाम से बनाई गई थी और बाद में इसका नाम बदल दिया गया।
आपका कार्य:
स्विस कंपनी — कॉपीराइट धारक के ऊपर होल्डिंग का प्रारंभिक (नाम बदलने से पहले) नाम स्थापित करें
रूसी प्रबंधन कंपनी का ОКФС कोड स्थापित करें और संस्थापकों की संरचना के संदर्भ में इसकी विसंगति बताएं
2009 से 2019 तक कॉपीराइट धारक की अंतर्राष्ट्रीय संरचना में President पद पर रहे व्यक्ति का पूरा नाम और मॉस्को में सीधा कार्यालय रखने वाले उनके पिछले कार्यस्थल का पता लगाएं
फ़्लैग: KubSTU{प्रारंभिक_नाम:ОКФС:president_का_उपनाम:मॉस्को_कार्यालय_वाली_कंपनी}
प्रारूप उदाहरण: KubSTU{Some_Name:01:Ivanov:Some_Firm}
चरण 1: LLC का पता लगाना
Trademarkia.com → "Minopolis Worldwide Edutainment LLC" खोजें
CTM application 006129035 (EUIPO, 27.08.2007)
Correspondent: Alexander Lederer, Wedertorgasse 12, Wien AT 1010

अवलोकन: LLC — ऑस्ट्रियाई रूप नहीं है (वहाँ GmbH होता है)।
नाम में "Worldwide" + LLC = शायद ऑफशोर या US-Delaware।
Dr. Sami Hamid प्रोफ़ाइल: "President of Minopolis Worldwide
Edutainment LLC — operations in Asia, Middle East, Eastern Europe."

निष्कर्ष: LLC — बौद्धिक अधिकारों का वाहक। AG — संचालन होल्डिंग।
दो अलग-अलग न्यायक्षेत्रों में दो अलग कानूनी संस्थाएँ।
चरण 2: स्विस होल्डिंग → Pinfarina AG
"Minopolis Edutainment AG Switzerland" खोजें →
Moneyhouse.ch: CHE-115.593.420, Baar, ZG
पिछले नाम: PINFARINA AG (28.07.2010 तक)

SHAB (Schweizer Handelsamtsblatt) के माध्यम से क्रॉस-चेक:
Publikation 28.07.2010:
"Pinfarina AG, in Zug → Firma neu: Minopolis Edutainment AG"

नाम बदलने की तारीख: 30.06.2010 (चार्टर तारीख) / 28.07.2010 (प्रकाशन)
क्रास्नोदार (2011) में पहले अंतर्राष्ट्रीय पार्क की घोषणा से मेल खाती है।
चरण 3: ОКФС विसंगति
ООО «Агат Груп» ИНН 7730647650 → ЕГРЮЛ:
संस्थापक: Агеева Зиля Халяфовна (51%), Агеев Рустам (49%)
दोनों: ИНН 1657... से शुरू → तातारस्तान गणराज्य।
दोनों — रूसी संघ के नागरिक।

सांख्यिकी कोड (Росстат):
ОКФС = 34 = «संयुक्त निजी और विदेशी संपत्ति»
ОКОГУ = 4210011 = «विदेशी कानूनी और/या व्यक्तिगत
          भागीदारी वाली व्यापारिक कंपनियाँ»

विरोधाभास: दो रूसी व्यक्ति → ОКФС 34 = विदेशी तत्व।
संभावित स्पष्टीकरण: विदेशी भागीदार (Minopolis AG या संबंधित
संरचना) 2011 में पंजीकरण के समय शामिल हुआ, फिर निकल गया
— लेकिन ОКФС पंजीकरण के समय सौंपा जाता है और संस्थापकों
के बदलने पर स्वचालित रूप से नहीं बदलता। या Агеевы नाममात्र के
हिस्सेदार हैं। Агат Груп का पंजीकरण (15.07.2011) OZ Mall में
Minopolis की घोषणा (जून 2011) के 3 सप्ताह बाद हुआ।
चरण 4: President → Ward Howell
LinkedIn: "Sami Hamid President Minopolis"
→ The Org / Signium: "Sami held the position of President at
  Minopolis from January 2009"
→ Before: "Managing Partner at Ward Howell International,
  February 1992 – May 2009"

AESC.org: "Ward Howell co-founded its affiliated firm in Russia
in 1992" → कार्यालय मॉस्को, Можайский Вал, 8।

ZoomInfo: Ward Howell — Mozhaysky Val Street Building 8, Moscow.
कंपनी सक्रिय, 100-249 कर्मचारी।

अतिरिक्त पिवट:
Dr. Sami Hamid Minopolis AG से निकले: 07.05.2019 (SHAB)
Minopolis AG का परिसमापन: 25.06.2019
अंतराल: 49 दिन → Hamid ने जहाज़ डूबने से पहले छोड़ दिया।
फ़्लैग संकलन
घटक 1: Pinfarina_AG - AG का प्रारंभिक नाम
घटक 2: 34 - Агат Груп का ОКФС = विदेशी तत्व
घटक 3: Hamid - President 2009-2019 का उपनाम
घटक 4: Ward_Howell - मॉस्को कार्यालय वाली कंपनी
फ़्लैग - KubSTU{Pinfarina_AG:34:Hamid:Ward_Howell}
