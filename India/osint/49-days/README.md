# [osint] 49 days

> **श्रेणी:** `osint`  
> **CTF:** KubSTU CTF 2026 Spring

कठिनाई: nightmare


बच्चों के थीम पार्क ब्रांड का अंतर्राष्ट्रीय अधिकार धारक कई क्षेत्राधिकारों में कानूनी संस्थाओं की श्रृंखला के माध्यम से काम करता था। इस श्रृंखला की मुख्य कड़ी — एक स्विस कंपनी — दूसरे नाम से बनाई गई थी और बाद में नाम बदला गया।

आपका कार्य:

1. स्विस कंपनी — अधिकार धारक के ऊपर की होल्डिंग — का मूल (नाम बदलने से पहले) नाम स्थापित करना
2. रूसी प्रबंधन कंपनी का ОКФС कोड स्थापित करना और संस्थापकों की संरचना के संबंध में इसकी विसंगति समझाना
3. 2009 से 2019 तक अधिकार धारक की अंतर्राष्ट्रीय संरचना में President पद पर रहे व्यक्ति का पूरा नाम और उसका पिछला कार्यस्थल ढूँढना, जिसका मॉस्को में सीधा कार्यालय है

फ़्लैग: KubSTU{मूल_नाम:ОКФС:अध्यक्ष_का_उपनाम:मॉस्को_कार्यालय_वाली_कंपनी}

उदाहरण प्रारूप: `KubSTU{Some_Name:01:Ivanov:Some_Firm}`

---

## चरण 1: LLC का पता लगाना

Trademarkia.com → "Minopolis Worldwide Edutainment LLC" खोज

> CTM application 006129035 (EUIPO, 27.08.2007)
>
> Correspondent: Alexander Lederer, Wedertorgasse 12, Wien AT 1010


अवलोकन: **LLC — ऑस्ट्रियाई रूप नहीं है (वहाँ GmbH होता है)**।

"Worldwide" नाम में + LLC = संभवतः ऑफ़शोर या US-Delaware।

Dr. Sami Hamid प्रोफ़ाइल: "President of Minopolis Worldwide 

> Edutainment LLC — operations in Asia, Middle East, Eastern Europe."


निष्कर्ष: LLC — बौद्धिक अधिकारों का वाहक। AG — ऑपरेशनल होल्डिंग।

> दो अलग-अलग क्षेत्राधिकारों में दो अलग कानूनी संस्थाएँ।

---

## चरण 2: स्विस होल्डिंग → Pinfarina AG

खोज "Minopolis Edutainment AG Switzerland" →

Moneyhouse.ch: CHE-115.593.420, Baar, ZG

> Past names: PINFARINA AG (28.07.2010 तक)


SHAB (Schweizer Handelsamtsblatt) द्वारा क्रॉस-चेक:

Publikation 28.07.2010:

> "Pinfarina AG, in Zug → Firma neu: Minopolis Edutainment AG"


नाम बदलने की तिथि: `30.06.2010 (चार्टर तिथि)` / `28.07.2010 (प्रकाशन)`

क्रास्नोदार में पहले अंतर्राष्ट्रीय पार्क की घोषणा (2011) से मेल खाता है।

---

## चरण 3: ОКФС विसंगति

ООО «Агат Груп» ИНН 7730647650 → ЕГРЮЛ:

संस्थापक: Агеева Зиля Халяфовна (51%), Агеев Рустам (49%)

दोनों: ИНН 1657... से शुरू → तातारस्तान गणराज्य।

दोनों — रूसी संघ के नागरिक।


सांख्यिकी कोड (Росстат):

ОКФС = 34 = «संयुक्त निजी और विदेशी संपत्ति»

ОКОГУ = 4210011 = «विदेशी कानूनी और/या भौतिक व्यक्तियों की

          भागीदारी वाले आर्थिक समाज»


विरोधाभास: दो रूसी भौतिक व्यक्ति → ОКФС 34 = विदेशी तत्व।

संभावित व्याख्या: विदेशी भागीदार (Minopolis AG या संबद्ध 

संरचना) 2011 में पंजीकरण के समय शामिल हुआ, फिर 

संस्थापकों से बाहर हो गया — लेकिन ОКФС पंजीकरण के समय दिया जाता है और 

संस्थापक बदलने पर स्वचालित रूप से नहीं बदलता। या Агеевы नॉमिनल रूप में 

हिस्सेदारी रखते हैं। Агат Груп का पंजीकरण (15.07.2011) OZ Mall में 

Minopolis की घोषणा (जून 2011) के 3 सप्ताह बाद हुआ।

---

## चरण 4: President → Ward Howell

LinkedIn: "Sami Hamid President Minopolis"

→ The Org / Signium: "Sami held the position of President at 

  Minopolis from January 2009"

→ Before: "Managing Partner at Ward Howell International, 

  February 1992 – May 2009"


AESC.org: "Ward Howell co-founded its affiliated firm in Russia 

in 1992" → मॉस्को कार्यालय, Можайский Вал, 8।


ZoomInfo: Ward Howell — Mozhaysky Val Street Building 8, Moscow.

कंपनी सक्रिय, 100-249 कर्मचारी।


अतिरिक्त पिवट:

Dr. Sami Hamid Minopolis AG से जाते हैं: 07.05.2019 (SHAB)

Minopolis AG का परिसमापन: 25.06.2019

अंतराल: 49 दिन → Hamid ने डूबने से पहले जहाज़ छोड़ दिया।

---

## फ़्लैग बनाना

घटक 1: Pinfarina_AG - AG का मूल नाम

घटक 2: 34 - Агат Груп का ОКФС = विदेशी तत्व

घटक 3: Hamid - President 2009-2019 का उपनाम

घटक 4: Ward_Howell - मॉस्को कार्यालय वाली कंपनी

---

फ़्लैग - `KubSTU{Pinfarina_AG:34:Hamid:Ward_Howell}`


