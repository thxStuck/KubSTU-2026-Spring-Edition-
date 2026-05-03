# [web] Bank 2

> **श्रेणी:** `web`  
> **CTF:** KubSTU CTF 2026 Spring

---

मिखाइल के मामले की जाँच के लिए बहुत-बहुत धन्यवाद। डेवलपमेंट टीम ने आपकी रिपोर्ट के अनुसार सब ठीक कर दिया, रिग्रेशन चलाया, QA ने साइन ऑफ़ कर दिया — इस कमज़ोरी का अब कोई फ़ायदा नहीं उठा सकता।
लेकिन समस्या यह है कि शिकायतें आती रहीं। इस हफ़्ते — तीन और, फिर हमारे प्रीमियम ग्राहकों से, फिर उसी पैटर्न से: उसी शॉप में किसी और का ट्रांसफ़र, सिग्नेचर वैध, PIN कोई बाहरी नहीं जानता था, लॉग में सब साफ़। शायद हमने सिर्फ़ एक दरवाज़ा बंद किया, और हमलावर ने बगल वाला ढूंढ लिया।
टेस्ट सेगमेंट फ़्रेश पैच्ड बिल्ड से फिर डिप्लॉय किया। शर्तें वही: पीड़ित — मिखाइल गालांकोव, mgalankov@4274।
श्रेणी: Web · JWT · Parameter Tampering · Broken Signature Binding
शर्तों में क्या कहा गया
v1 जैसा: लक्ष्य — mgalankov@4274, user_id = 10।
v2 में डेवलपरों ने दो चीज़ें ठीक कीं:
अपुष्ट ट्रांज़ैक्शन (skip_pin=1) में signature अब None — रसीद से कुछ नहीं देखा जा सकता।
/receipt/<id> अपुष्ट ट्रांज़ैक्शन को /verify_transaction/<id> पर रीडायरेक्ट करता है।
लेकिन /transfer-एंडपॉइंट में सिग्नेचर को यूज़र से बाइंड करना गायब हो गया। इसी में नया एक्सप्लॉइट काम करता है — FLAG_SHOP पुष्टि फ़ॉर्म में दूसरे की वैध transaction_timestamp + transaction_signature जोड़ी इंजेक्ट करना।

## चरण 1. सामान्य ग्राहक के रूप में रजिस्टर (वास्तव में दो अकाउंट चाहिए)

पहला अकाउंट रजिस्टर — यह «सिग्नेचर डोनर» होगा। लॉगिन/पासवर्ड/PIN याद रखें। PIN अपना — हमने खुद सेट किया — काम आएगा।
लॉगिन करते हैं, Burp खोलते हैं, JWT वाली cookie इंटरसेप्ट करते हैं।

## चरण 2. JWT-सीक्रेट brute-force

JWT को jwt.txt में डालते हैं:
hashcat -a 0 -m 16500 jwt.txt /usr/share/wordlists/rockyou.txt
कुछ सेकंड में सीक्रेट — ifeveryonecared3 (भी rockyou से, v2 ने शब्दकोश शब्द बदला लेकिन विचार वही)।

## चरण 3. jwt.io पर mgalankov@4274 के लिए JWT बनाना

jwt.io पर:
बाएं — हमारा वर्तमान JWT।
VERIFY SIGNATURE → secret में ifeveryonecared3, हरा «Signature Verified» दिखता है।
payload में "sub" को "10", "username" को "mgalankov@4274" बदलते हैं। exp आगे बढ़ाते हैं।
बाएं नया टोकन मिलता है।
Burp में cookie बदलते हैं।
GET /dashboard — mgalankov का अकाउंट दिखता है। हम अंदर हैं।

## चरण 4. Telegram-बॉट से टोकन

/token कमांड बॉट को → टोकन कॉपी।

## चरण 5. शॉप में खरीदारी शुरू

बनाई cookie से /partners → «फ़्लैग शॉप»। कोई सामान «खरीदें», टोकन पेस्ट।
FLAG_SHOP के लिए ट्रांसफ़र फ़ॉर्म + PIN अनुरोध खुलता है।
mgalankov का PIN नहीं जानते। लेकिन v2 में skip_pin=1 अब सिग्नेचर DB में नहीं छोड़ता — v1 रास्ता बंद। दूसरे रास्ते से जाते हैं।

## चरण 6. अपने अकाउंट से «सही» (timestamp, signature) जोड़ी निकालना

दूसरे ब्राउज़र विंडो में अपने सामान्य यूज़र से लॉगिन। PIN अपना — जानते हैं।
अपने खातों के बीच «सामान्य» ट्रांसफ़र करते हैं। Burp में इंटरसेप्ट चालू।
JS पहले /api/get_signature पर PIN के साथ XHR भेजता है। रिस्पॉन्स:
{
  "date": "2026-04-25",
  "time": "00:11:02",
  "timestamp": 1745532662,
  "signature": "9f3b81c4ea5d6178"
}
यह timestamp=1745532662, signature=9f3b81c4ea5d6178 जोड़ी गणितीय रूप से वैध है। सर्वर ने इसे हमारे यूज़र के लिए जनरेट किया, लेकिन /transfer में यह बाइंडिंग जाँची नहीं जाती। यही कमज़ोरी है।

## चरण 7. बनाए mgalankov JWT के साथ FLAG_SHOP खरीदारी पुष्ट करना

Burp Repeater में POST मैन्युअली बनाते हैं:
POST /transfer HTTP/1.1
Host: target
Cookie: access_token_cookie=<बनाया JWT mgalankov>
Content-Type: application/x-www-form-urlencoded

to_account=FLAG_SHOP
&amount=1000.00
&description=...
&product_id=1
&token=t_8a3f...
&transaction_date=2026-04-25
&transaction_time=00:11:02
&transaction_timestamp=1745532662
&transaction_signature=9f3b81c4ea5d6178
मुख्य — skip_pin=1 नहीं होना चाहिए, और दोनों transaction_timestamp + transaction_signature हमारे /api/get_signature से।
Send दबाते हैं। सर्वर timestamp=1745532662 से सिग्नेचर पुनर्गणना करता है — वही 9f3b81c4ea5d6178 मिलता है। मिलान — ट्रांज़ैक्शन पुष्ट। Telegram-बॉट फ़्लैग भेजता है।
संक्षेप में — यह क्यों काम करता है
JWT-सीक्रेट अभी भी शब्दकोश (ifeveryonecared3), rockyou से।
/transfer (transaction_signature शाखा) में जारी सिग्नेचर का यूज़र और पैरामीटर से सर्वर-साइड बाइंडिंग गायब — कोई भी वैध (timestamp, sig) जोड़ी स्वीकार होती है।
अपनी वैध जोड़ी /api/get_signature से (अपना PIN) आसानी से निकालकर बनाए mgalankov JWT के साथ अनुरोध में डालते हैं।
