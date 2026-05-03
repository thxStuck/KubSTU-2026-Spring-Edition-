# [ppc] Mobile Waf

> **Category:** `ppc`  
> **CTF:** KubSTU CTF 2026 Spring

---

Challenge.


Our university has been receiving a lot of requests lately and I think they're suspicious. 


Challenge files:


[Mobile_waf.rar](./files/Mobile_waf.rar)

---

  

# WAF CTF Challenge - Write-up



## Challenge Description



When connecting to the server via `nc`, we see:



```

=== WAF Challenge ===

You need to correctly classify 100 HTTP requests as malicious or safe.

For each request, respond with:

  - 'Block' if the request is malicious

  - 'Allow' if the request is safe



Type 'Start' to begin:

```



**Task**: Classify 100 HTTP requests in a row without errors.  

**Type**: Web Security / WAF  

**Difficulty**: Medium  

**Flag format**: `KubSTU(...)`



## First Attempt - Manual Solution



### Connection and Start



```bash

$ nc <host> 1337

```



After sending `Start`, I get the first request:



```

--- Request 1/100 ---

GET /admin?id=1' OR '1'='1 HTTP/1.1

Host: example.com



Your answer (Block/Allow): Block

✓ Correct! (1/100)

```



**Success**: Obvious SQL injection — correctly identified.



### Mistake #1: Simple Search Queries



```

--- Request 5/100 ---

GET /api/search?q=union+select+null HTTP/1.1

Host: api.example.com



Your answer (Block/Allow): Block

✗ Wrong! The request was SAFE.

Challenge failed. Try again!

```



**Problem**: Saw `UNION SELECT` and assumed it was SQL injection.  

**Lesson**: In API endpoints, simple SQL keywords without injection indicators (quotes, comments) are legitimate search queries.



### Mistake #2: API Endpoints with query/search/filter Parameters



```

--- Request 12/100 ---

GET /api/filter?query=SELECT+*+FROM+users HTTP/1.1

Host: api.example.com



Your answer (Block/Allow): Block

✗ Wrong! The request was SAFE.

```



**Problem**: SQL-like queries in `query`, `search`, `filter` parameters are legitimate search queries, even if they look like SQL.



### Mistake #3: API Endpoints with File Paths



```

--- Request 40/100 ---

GET /api/load?file=../../config.json HTTP/1.1

Host: api.example.com



Your answer (Block/Allow): Block

✗ Wrong! The request was SAFE.

```



**Problem**: Some API endpoints legitimately accept file paths in parameters, even with `../`.



### Mistake #4: Test Endpoints



```

--- Request 52/100 ---

GET /api/test?id=1' OR '1'='1 HTTP/1.1

Host: api.example.com



Your answer (Block/Allow): Block

✗ Wrong! The request was SAFE.

```



**Problem**: Test endpoints (`/api/test`, `/api/filter`) can accept any data, including SQL-like queries, as legitimate test data.



### Mistake #5: Parameterized SQL Queries



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



**Problem**: Parameterized SQL queries (with `?` and a `params` array) are a safe practice, not injection.



### Mistake #6: URL-Encoded Attacks



```

--- Request 73/100 ---

GET /page?name=%3Csvg%20onload%3Dalert%281%29%3E HTTP/1.1

Host: example.com



Your answer (Block/Allow): Allow

✗ Wrong! The request was MALICIOUS.

```



**Problem**: Didn't decode the URL before analysis. `%3Csvg%20onload%3Dalert%281%29%3E` decodes to `<svg onload=alert(1)>` — this is XSS.



### Mistake #7: Scripts in API Parameters



```

--- Request 82/100 ---

GET /api/data?script=<script>alert('test')</script> HTTP/1.1

Host: api.example.com



Your answer (Block/Allow): Block

✗ Wrong! The request was SAFE.

```



**Problem**: For API endpoints, scripts in `script` parameters can be legitimate test data.



## Solution - Automated Client



After many failed attempts, I realized I needed to write an automated client.



### Attack Types to Check



#### SQL Injection

- Quotes with operators: `' OR '1'='1`, `1' OR '1'='1`

- UNION SELECT injections

- SQL comments: `--`, `/* */`

- Dangerous functions: `DROP TABLE`, `SLEEP()`, `SUBSTRING()`



#### XSS (Cross-Site Scripting)

- Tags: `<script>`, `<svg onload>`, `<img onerror>`

- Event handlers: `onload=`, `onerror=`

- JavaScript code: `javascript:`, `eval()`



#### Path Traversal

- `../` sequences in paths

- Access to system files: `/etc/passwd`, `/etc/shadow`



#### Command Injection

- Dangerous commands: `rm -rf`, `cat /etc/passwd`

- Execution functions: `system()`, `exec()`, `shell_exec()`



#### XXE (XML External Entity)

- External entities: `<!ENTITY xxe SYSTEM>`

- File protocols: `file:///`



#### Template Injection

- Templates with dangerous constructs: `{{...}}`, `#{}`

- Access to system functions



#### Code Injection

- Code execution: `eval()`, `Function()`, `require()`



### Important Exceptions



1. **API endpoints with `query`/`search`/`filter` parameters**: 

   - Even SQL-like queries are safe if there are no explicit injection indicators

   

2. **Test endpoints** (`/api/test`, `/api/filter`): 

   - Any data is safe



3. **Parameterized SQL queries**: 

   - If SQL contains `?` and there's a `params` array — it's safe



4. **URL-encoded data**: 

   - Always decode before checking



5. **Scripts in API parameters**: 

   - For API endpoints, `<script>` in parameters can be legitimate



### Key Implementation Points



```python

*# 1. URL decoding*

decoded_request = urllib.parse.unquote(request.replace('+', ' '))



*# 2. Extracting path from HTTP request*

path_part = request.split()[1]  *# GET /path HTTP/1.1*



*# 3. Check for API endpoints*

*if* path.startswith('/api/') and param_name in ['query', 'search', 'filter', 'q']:

    *# Even SQL-like queries can be safe*

    

*# 4. Checking parameterized queries*

*if* '"sql":' in request and '"params":' in request and '?' in sql_query:

    *# Safe parameterized query*

```



### Final Run



```bash

$ python waf_client.py --host <host> --port 1337

============================================================

Question 100/100:

============================================================

Request:

GET /index.html HTTP/1.1

Host: example.com



Analysis: 🟢 SAFE

Answer: Allow

✓ Correct! (100/100)



==================================================

Congratulations! You correctly classified all 100 requests!

Flag: KubSTU(y0u_4r3_4_g00d_m0b1l3_4551574n7_f0r_d373c71ng_3v1l)

==================================================

```



## Conclusions



1. **Context is critical**: The same patterns can be safe in API endpoints and malicious in regular requests



2. **Test endpoints**: `/api/test`, `/api/filter` can accept any data



3. **Parameterization = safety**: Proper use of parameters prevents injections



4. **Decoding is mandatory**: Always decode URLs before analysis



5. **Automation wins**: For 100 requests, an automated client is much more effective than manual solving



## Using the Client



```bash

*# Automated solution*

python waf_client.py --host <host> --port 1337



*# Manual solution via nc*

nc <host> 1337

*# Enter Start, then respond Block or Allow*

```

 ![img_1.png](./images/img_1.png)



---


[waf_client.py](./files/waf_client.py)



**Flag**: `KubSTU(y0u_4r3_4_g00d_m0b1l3_4551574n7_f0r_d373c71ng_3v1l)`


  

```javascript
KubSTU(y0u_4r3_4_g00d_m0b1l3_4551574n7_f0r_d373c71ng_3v1l)
```


