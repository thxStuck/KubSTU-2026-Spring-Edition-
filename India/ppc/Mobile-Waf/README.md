# [ppc] Mobile Waf

> **श्रेणी:** `ppc`  
> **CTF:** KubSTU CTF 2026 Spring

---

चुनौती।


हमारे विश्वविद्यालय पर हाल ही में बहुत सारे अनुरोध आ रहे हैं और मुझे लगता है कि वे संदिग्ध हैं। 


चुनौती फ़ाइलें:


[Mobile_waf.rar](./files/Mobile_waf.rar)

---

  

# WAF CTF Challenge - राइटअप



## चुनौती का विवरण



`nc` द्वारा सर्वर से कनेक्ट करने पर दिखता है:



```

=== WAF Challenge ===

You need to correctly classify 100 HTTP requests as malicious or safe.

For each request, respond with:

  - 'Block' if the request is malicious

  - 'Allow' if the request is safe



Type 'Start' to begin:

```



**कार्य**: बिना गलती के लगातार 100 HTTP अनुरोधों को वर्गीकृत करना।  

**प्रकार**: Web Security / WAF  

**कठिनाई**: Medium  

**फ़्लैग का प्रारूप**: `KubSTU(...)`



## पहला प्रयास - मैन्युअल समाधान



### कनेक्शन और शुरुआत



```bash

$ nc <host> 1337

```



`Start` भेजने के बाद पहला अनुरोध मिलता है:



```

--- Request 1/100 ---

GET /admin?id=1' OR '1'='1 HTTP/1.1

Host: example.com



Your answer (Block/Allow): Block

✓ Correct! (1/100)

```



**सफलता**: स्पष्ट SQL इंजेक्शन — सही पहचान।



### गलती #1: सरल खोज अनुरोध



```

--- Request 5/100 ---

GET /api/search?q=union+select+null HTTP/1.1

Host: api.example.com



Your answer (Block/Allow): Block

✗ Wrong! The request was SAFE.

Challenge failed. Try again!

```



**समस्या**: `UNION SELECT` देखा और SQL इंजेक्शन मान लिया।  

**सबक**: API endpoints में इंजेक्शन के स्पष्ट संकेतों (कोट्स, कमेंट्स) के बिना सरल SQL-कीवर्ड — वैध खोज अनुरोध हैं।



### गलती #2: query/search/filter पैरामीटर वाले API endpoints



```

--- Request 12/100 ---

GET /api/filter?query=SELECT+*+FROM+users HTTP/1.1

Host: api.example.com



Your answer (Block/Allow): Block

✗ Wrong! The request was SAFE.

```



**समस्या**: `query`, `search`, `filter` पैरामीटर में SQL-जैसे अनुरोध — वैध खोज अनुरोध हैं, भले ही वे SQL जैसे दिखें।



### गलती #3: फ़ाइल पथ वाले API endpoints



```

--- Request 40/100 ---

GET /api/load?file=../../config.json HTTP/1.1

Host: api.example.com



Your answer (Block/Allow): Block

✗ Wrong! The request was SAFE.

```



**समस्या**: कुछ API endpoints वैध रूप से पैरामीटर में फ़ाइल पथ स्वीकार करते हैं, `../` के साथ भी।



### गलती #4: टेस्ट endpoints



```

--- Request 52/100 ---

GET /api/test?id=1' OR '1'='1 HTTP/1.1

Host: api.example.com



Your answer (Block/Allow): Block

✗ Wrong! The request was SAFE.

```



**समस्या**: टेस्ट endpoints (`/api/test`, `/api/filter`) किसी भी डेटा को वैध टेस्ट डेटा के रूप में स्वीकार कर सकते हैं।



### गलती #5: पैरामीट्राइज़्ड SQL अनुरोध



```

--- Request 67/100 ---

POST /api/query HTTP/1.1

Host: api.example.com

Content-Type: application/json

Content-Length: 78



{"sql":"SELECT * FROM users WHERE id = ?","params":[123]}



Your answer (Block/Allow): Block

✗ Wrong! The request was SAFE.

```



**समस्या**: पैरामीट्राइज़्ड SQL अनुरोध (`?` और `params` ऐरे के साथ) — सुरक्षित प्रथा है, इंजेक्शन नहीं।



### गलती #6: URL-encoded हमले



```

--- Request 73/100 ---

GET /page?name=%3Csvg%20onload%3Dalert%281%29%3E HTTP/1.1

Host: example.com



Your answer (Block/Allow): Allow

✗ Wrong! The request was MALICIOUS.

```



**समस्या**: विश्लेषण से पहले URL डिकोड नहीं किया। `%3Csvg%20onload%3Dalert%281%29%3E` डिकोड करने पर `<svg onload=alert(1)>` बनता है — यह XSS है।



### गलती #7: API पैरामीटर में स्क्रिप्ट



```

--- Request 82/100 ---

GET /api/data?script=<script>alert('test')</script> HTTP/1.1

Host: api.example.com



Your answer (Block/Allow): Block

✗ Wrong! The request was SAFE.

```



**समस्या**: API endpoints के लिए `script` पैरामीटर में स्क्रिप्ट टेस्टिंग के लिए वैध डेटा हो सकते हैं।



## समाधान - ऑटोमेटिक क्लाइंट



कई असफल प्रयासों के बाद समझ आया कि ऑटोमेटिक क्लाइंट लिखना होगा।



### जाँचने के लिए हमले के प्रकार



#### SQL Injection

- ऑपरेटर के साथ कोट्स: `' OR '1'='1`, `1' OR '1'='1`

- UNION SELECT इंजेक्शन

- SQL कमेंट्स: `--`, `/* */`

- ख़तरनाक फंक्शन: `DROP TABLE`, `SLEEP()`, `SUBSTRING()`



#### XSS (Cross-Site Scripting)

- टैग: `<script>`, `<svg onload>`, `<img onerror>`

- इवेंट हैंडलर: `onload=`, `onerror=`

- JavaScript कोड: `javascript:`, `eval()`



#### Path Traversal

- पथ में `../` अनुक्रम

- सिस्टम फ़ाइलों तक पहुँच: `/etc/passwd`, `/etc/shadow`



#### Command Injection

- ख़तरनाक कमांड: `rm -rf`, `cat /etc/passwd`

- निष्पादन फंक्शन: `system()`, `exec()`, `shell_exec()`



#### XXE (XML External Entity)

- बाहरी entities: `<!ENTITY xxe SYSTEM>`

- फ़ाइल प्रोटोकॉल: `file:///`



#### Template Injection

- ख़तरनाक निर्माणों वाले टेम्पलेट: `{{...}}`, `#{}`

- सिस्टम फंक्शन तक पहुँच



#### Code Injection

- कोड निष्पादन: `eval()`, `Function()`, `require()`



### महत्वपूर्ण अपवाद



1. **`query`/`search`/`filter` पैरामीटर वाले API endpoints**: 

   - इंजेक्शन के स्पष्ट संकेतों के बिना SQL-जैसे अनुरोध भी सुरक्षित हैं

   

2. **टेस्ट endpoints** (`/api/test`, `/api/filter`): 

   - कोई भी डेटा सुरक्षित है



3. **पैरामीट्राइज़्ड SQL अनुरोध**: 

   - अगर SQL में `?` है और `params` ऐरे है — सुरक्षित



4. **URL-encoded डेटा**: 

   - जाँच से पहले हमेशा डिकोड करें



5. **API पैरामीटर में स्क्रिप्ट**: 

   - API endpoints के लिए पैरामीटर में `<script>` वैध हो सकता है



### कार्यान्वयन के मुख्य बिंदु



```python

*# 1. URL डिकोडिंग*

decoded_request = urllib.parse.unquote(request.replace('+', ' '))



*# 2. HTTP अनुरोध से पथ निकालना*

path_part = request.split()[1]  *# GET /path HTTP/1.1*



*# 3. API endpoints के लिए जाँच*

*if* path.startswith('/api/') and param_name in ['query', 'search', 'filter', 'q']:

    *# SQL-जैसे अनुरोध भी सुरक्षित हो सकते हैं*

    

*# 4. पैरामीट्राइज़्ड अनुरोधों की जाँच*

*if* '"sql":' in request and '"params":' in request and '?' in sql_query:

    *# सुरक्षित पैरामीट्राइज़्ड अनुरोध*

```



### अंतिम रन



```bash

$ python waf_client.py --host <host> --port 1337

============================================================

प्रश्न 100/100:

============================================================

अनुरोध:

GET /index.html HTTP/1.1

Host: example.com



विश्लेषण: 🟢 सुरक्षित

उत्तर: Allow

✓ सही! (100/100)



==================================================

Congratulations! You correctly classified all 100 requests!

Flag: KubSTU(y0u_4r3_4_g00d_m0b1l3_4551574n7_f0r_d373c71ng_3v1l)

==================================================

```



## निष्कर्ष



1. **संदर्भ महत्वपूर्ण है**: समान पैटर्न API endpoints में सुरक्षित और सामान्य अनुरोधों में हानिकारक हो सकते हैं



2. **टेस्ट endpoints**: `/api/test`, `/api/filter` कोई भी डेटा स्वीकार कर सकते हैं



3. **पैरामीट्राइज़ेशन = सुरक्षा**: पैरामीटर का सही उपयोग इंजेक्शन रोकता है



4. **डिकोडिंग अनिवार्य**: विश्लेषण से पहले हमेशा URL डिकोड करें



5. **ऑटोमेशन जीतता है**: 100 अनुरोधों के लिए क्लाइंट मैन्युअल समाधान से कहीं अधिक प्रभावी है



## क्लाइंट का उपयोग



```bash

*# ऑटोमेटिक समाधान*

python waf_client.py --host <host> --port 1337



*# nc द्वारा मैन्युअल समाधान*

nc <host> 1337

*# Start टाइप करें, फिर Block या Allow उत्तर दें*

```

 ![img_1.png](./images/img_1.png)



---


[waf_client.py](./files/waf_client.py)



**Flag**: `KubSTU(y0u_4r3_4_g00d_m0b1l3_4551574n7_f0r_d373c71ng_3v1l)`


  

```javascript
KubSTU(y0u_4r3_4_g00d_m0b1l3_4551574n7_f0r_d373c71ng_3v1l)
```


