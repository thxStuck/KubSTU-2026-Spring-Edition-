# [ppc] Mobile Waf

> **श्रेणी:** `ppc`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 चुनौती की फ़ाइलें</summary>

| फ़ाइल | प्रकार |
|------|-----|
| [Mobile_waf.rar](./files/img_1.rar) | `application/x-compressed` |
| [waf_client.py](./files/img_2.py) | `text/x-python` |

</details>

---

चुनौती।

हमारे विश्वविद्यालय पर हाल ही में बहुत सारे अनुरोध आ रहे हैं और मुझे लगता है कि वे संदिग्ध हैं।

चुनौती की फ़ाइलें:

![image.png](./images/img_3.png)

# WAF CTF Challenge - राइटअप

## चुनौती का विवरण

`nc` के माध्यम से सर्वर से कनेक्ट करने पर दिखता है:

```
=== WAF Challenge ===
You need to correctly classify 100 HTTP requests as malicious or safe.
For each request, respond with:
  - 'Block' if the request is malicious
  - 'Allow' if the request is safe

Type 'Start' to begin:
```

**कार्य**: 100 HTTP अनुरोधों को बिना गलती के लगातार वर्गीकृत करना।
**प्रकार**: Web Security / WAF
**कठिनाई**: Medium
**फ़्लैग प्रारूप**: `KubSTU(...)`

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

सफलता: स्पष्ट SQL injection — सही पहचाना।

### गलती #1: सामान्य सर्च क्वेरी

```
--- Request 5/100 ---
GET /api/search?q=union+select+null HTTP/1.1
Host: api.example.com

Your answer (Block/Allow): Block
✗ Wrong! The request was SAFE.
```

**समस्या**: `UNION SELECT` देखा और SQL injection समझ लिया।
**सीख**: API endpoints में injection के स्पष्ट संकेत (कोट, कमेंट) के बिना सरल SQL-कीवर्ड वैध सर्च क्वेरी हैं।

### गलती #2: query/search/filter पैरामीटर वाले API endpoints

```
--- Request 12/100 ---
GET /api/filter?query=SELECT+*+FROM+users HTTP/1.1
Host: api.example.com

Your answer (Block/Allow): Block
✗ Wrong! The request was SAFE.
```

**समस्या**: `query`, `search`, `filter` पैरामीटरों में SQL-जैसी क्वेरी — SQL दिखने पर भी वैध सर्च क्वेरी हैं।

### गलती #3: फ़ाइल पथ वाले API endpoints

```
--- Request 40/100 ---
GET /api/load?file=../../config.json HTTP/1.1
Host: api.example.com

Your answer (Block/Allow): Block
✗ Wrong! The request was SAFE.
```

**समस्या**: कुछ API endpoints वैध रूप से `../` सहित फ़ाइल पथ स्वीकार करते हैं।

### गलती #4: टेस्ट endpoints

```
--- Request 52/100 ---
GET /api/test?id=1' OR '1'='1 HTTP/1.1
Host: api.example.com

Your answer (Block/Allow): Block
✗ Wrong! The request was SAFE.
```

**समस्या**: टेस्ट endpoints (`/api/test`, `/api/filter`) SQL-जैसे अनुरोधों सहित कोई भी डेटा वैध टेस्ट डेटा के रूप में स्वीकार कर सकते हैं।

### गलती #5: पैरामीटराइज़्ड SQL क्वेरी

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

**समस्या**: `?` और `params` ऐरे वाली पैरामीटराइज़्ड SQL क्वेरी — यह सुरक्षित प्रैक्टिस है, injection नहीं।

### गलती #6: URL-encoded हमले

```
--- Request 73/100 ---
GET /page?name=%3Csvg%20onload%3Dalert%281%29%3E HTTP/1.1
Host: example.com

Your answer (Block/Allow): Allow
✗ Wrong! The request was MALICIOUS.
```

**समस्या**: विश्लेषण से पहले URL डीकोड नहीं किया। `%3Csvg%20onload%3Dalert%281%29%3E` डीकोड होकर `<svg onload=alert(1)>` बनता है — यह XSS है।

### गलती #7: API पैरामीटर में स्क्रिप्ट

```
--- Request 82/100 ---
GET /api/data?script=<script>alert('test')</script> HTTP/1.1
Host: api.example.com

Your answer (Block/Allow): Block
✗ Wrong! The request was SAFE.
```

**समस्या**: API endpoints के लिए `script` पैरामीटर में स्क्रिप्ट टेस्टिंग के लिए वैध डेटा हो सकती हैं।

## समाधान - स्वचालित क्लाइंट

कई असफल प्रयासों के बाद समझ आता है कि स्वचालित क्लाइंट लिखना होगा।

### जाँच के लिए हमले के प्रकार

#### SQL Injection
- ऑपरेटरों के साथ कोट: `' OR '1'='1`, `1' OR '1'='1`
- UNION SELECT injection
- SQL कमेंट: `--`, `/* */`
- खतरनाक फ़ंक्शन: `DROP TABLE`, `SLEEP()`, `SUBSTRING()`

#### XSS (Cross-Site Scripting)
- टैग: `<script>`, `<svg onload>`, `<img onerror>`
- इवेंट हैंडलर: `onload=`, `onerror=`
- JavaScript कोड: `javascript:`, `eval()`

#### Path Traversal
- पथ में `../` अनुक्रम
- सिस्टम फ़ाइलों तक पहुँच: `/etc/passwd`, `/etc/shadow`

#### Command Injection
- खतरनाक कमांड: `rm -rf`, `cat /etc/passwd`
- निष्पादन फ़ंक्शन: `system()`, `exec()`, `shell_exec()`

#### XXE (XML External Entity)
- बाहरी संस्थाएँ: `<!ENTITY xxe SYSTEM>`
- फ़ाइल प्रोटोकॉल: `file:///`

#### Template Injection
- खतरनाक कंस्ट्रक्ट वाले टेम्प्लेट: `{{...}}`, `#{}`
- सिस्टम फ़ंक्शन तक पहुँच

#### Code Injection
- कोड निष्पादन: `eval()`, `Function()`, `require()`

### महत्वपूर्ण अपवाद

1. **`query`/`search`/`filter` पैरामीटर वाले API endpoints**:
   - injection के स्पष्ट संकेत न हों तो SQL-जैसी क्वेरी भी सुरक्षित

2. **टेस्ट endpoints** (`/api/test`, `/api/filter`):
   - कोई भी डेटा सुरक्षित

3. **पैरामीटराइज़्ड SQL क्वेरी**:
   - SQL में `?` और `params` ऐरे हो तो — सुरक्षित

4. **URL-encoded डेटा**:
   - जाँच से पहले हमेशा डीकोड करें

5. **API पैरामीटर में स्क्रिप्ट**:
   - API endpoints के लिए पैरामीटर में `<script>` वैध हो सकता है

### कार्यान्वयन के मुख्य बिंदु

```python
# 1. URL डीकोडिंग
decoded_request = urllib.parse.unquote(request.replace('+', ' '))

# 2. HTTP अनुरोध से पथ निकालना
path_part = request.split()[1]  # GET /path HTTP/1.1

# 3. API endpoints के लिए जाँच
if path.startswith('/api/') and param_name in ['query', 'search', 'filter', 'q']:
    # SQL-जैसी क्वेरी भी सुरक्षित हो सकती है

# 4. पैरामीटराइज़्ड क्वेरी की जाँच
if '"sql":' in request and '"params":' in request and '?' in sql_query:
    # सुरक्षित पैरामीटराइज़्ड क्वेरी
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

1. **संदर्भ महत्वपूर्ण है**: एक ही पैटर्न API endpoints में सुरक्षित और सामान्य अनुरोधों में हानिकारक हो सकते हैं

2. **टेस्ट endpoints**: `/api/test`, `/api/filter` कोई भी डेटा स्वीकार कर सकते हैं

3. **पैरामीटराइज़ेशन = सुरक्षा**: पैरामीटरों का सही उपयोग injection रोकता है

4. **डीकोडिंग अनिवार्य**: विश्लेषण से पहले हमेशा URL डीकोड करें

5. **ऑटोमेशन जीतता है**: 100 अनुरोधों के लिए क्लाइंट मैन्युअल समाधान से कहीं अधिक कुशल है

## क्लाइंट का उपयोग

```bash
# स्वचालित समाधान
python waf_client.py --host <host> --port 1337

# nc से मैन्युअल समाधान
nc <host> 1337
# Start दर्ज करें, फिर Block या Allow जवाब दें
```

---


**Flag**: `KubSTU(y0u_4r3_4_g00d_m0b1l3_4551574n7_f0r_d373c71ng_3v1l)`


KubSTU(y0u_4r3_4_g00d_m0b1l3_4551574n7_f0r_d373c71ng_3v1l)
