# [web] MCPocalypse

> **Category:** `web`  
> **CTF:** KubSTU CTF 2026 Spring

---

Challenge description:
"CapyTech Solutions" claims their AI understands commands at a glance. You can simply say: "Restart Nginx!", and the server will obey.

Writeup:

Introduction:
This writeup describes the solution for the CTF challenge "Capy CTF: The Secret Node", based on a chain of two critical vulnerabilities in nginx-ui version 2.3.1. The goal is to obtain the flag located in /flag.txt inside the nginx_ui container by exploiting these vulnerabilities to achieve Remote Code Execution (RCE) or file disclosure.

Vulnerability overview:
The CTF challenge exploits the following vulnerability chain:

1. CVE-2026-27944: Unauthenticated backup and key disclosure
CVE-2026-27944 allows an unauthenticated user to access the /api/backup endpoint. This endpoint returns an encrypted archive containing a full backup of the nginx-ui installation, including the app.ini file. The critical aspect is that the AES-256-CBC decryption key and initialization vector (IV) are transmitted in plaintext in the X-Backup-Security response header.
By decrypting the archive with the obtained keys, you can extract the app.ini file, which contains Node.Secret — the secret needed to exploit the next vulnerability.
More details at https://github.com/advisories/GHSA-g9w5-qffc-6762

2. CVE-2026-33032 ("MCPwn"): Unauthenticated MCP message handler
CVE-2026-33032, also known as "MCPwn", involves the absence of authentication checks (AuthRequired() middleware) on the /mcp_message endpoint. nginx-ui uses the MCP (Model Context Protocol) protocol for managing Nginx, providing 12 privileged management tools.
Using the Node.Secret obtained in the first stage, an attacker can establish an unauthenticated SSE session with /mcp to get a sessionId. Then, by sending POST requests to /mcp_message with this sessionId, any privileged MCP tool can be invoked without any authentication. This allows overwriting Nginx configuration files (nginx_config_modify) and reloading the server (reload_nginx), leading to RCE or file disclosure.

Vulnerability chain:

CVE-2026-27944 — Unauthenticated backup endpoint + key disclosure:
GET /api/backup requires no authentication. This endpoint returns a full encrypted backup of the nginx-ui installation — including app.ini — and sends the AES-256-CBC decryption key and IV in plaintext in the response header:
X-Backup-Security: <base64_key>:<base64_iv>
r.GET("/backup", CreateBackup)   // ❌ no middleware
r.POST("/restore", middleware.EncryptedForm(), RestoreBackup)

Decrypting the backup yields app.ini, which contains the [node] Secret needed for step 2.

CVE-2026-33032 "MCPwn" — Unauthenticated MCP message handler:
In nginx-ui v2.3.x, a Model Context Protocol (MCP) interface was added, providing 12 nginx management tools. The bug is a single missing middleware call in mcp/router.go:
r.Any("/mcp",         middleware.IPWhiteList(), middleware.AuthRequired(), ...)
r.Any("/mcp_message", middleware.IPWhiteList(), ...)   // ❌ MISSING AuthRequired()

How the chain works:
With a sessionId obtained using the node secret, an attacker can send POST requests to /mcp_message without any credentials and invoke any privileged tool — including nginx_config_modify and reload_nginx.

## Solution

Stage 1: Extracting `Node.Secret` (CVE-2026-27944)
The first step is to obtain Node.Secret from app.ini. This is achieved by sending an unauthenticated GET request to /api/backup on nginx-ui (port 9000). The X-Backup-Security header in the response will contain base64-encoded AES key and IV. Then:
1. Decode key and IV from base64.
2. Decrypt the received encrypted ZIP archive using AES in CBC mode with the obtained key and IV.
3. Extract the app.ini file from the decrypted archive.
4. Read the Secret value from the [node] section of app.ini.

There's a ready-made exploit for obtaining Node.Secret: https://github.com/Skynoxk/CVE-2026-27944
[*] CVE-2026-27944 — downloading backup from Nginx-UI (no auth)
[+] AES key+IV from header: 7jeJX3Ph8q4/IpdY...:nuPm7h3U...
[+] Node secret extracted: sicret-ctf-capy-key-2026

Stage 2: Modifying Nginx configuration and obtaining the flag (CVE-2026-33032)

The MCPSession class and mcp_swap function implement this stage:

Establishing an MCP session: An MCPSession object is created with base_url and node_secret. The connect() method sends a GET request to f"{self.base_url}/mcp" with the node_secret parameter. The sessionId is parsed from the SSE response stream.

Modifying Nginx configuration: The call_tool method sends a POST request to f"{self.base_url}/mcp_message" with the obtained sessionId. The payload is a JSON-RPC request invoking the nginx_config_modify method.

The payload for nginx_config_modify uses the following FLAG_CONFIG:
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

- `location /flag { alias /flag.txt; internal; }`: This block tells Nginx to serve the contents of /flag.txt when /flag is requested. The internal directive makes this location accessible only for internal redirects or subrequests within Nginx.
- `location /get_flag { rewrite ^ /flag break; }`: This block creates a publicly accessible /get_flag endpoint. The rewrite directive rewrites /get_flag to /flag. Since /flag is internal, Nginx handles it internally, serving /flag.txt through the public /get_flag endpoint.

Reloading Nginx: After modifying the configuration, reload_nginx is called via call_tool to apply the changes.

Obtaining the flag: After successful Nginx reload, the script sends a GET request to f"{webapp_url}/get_flag".

![image.png](./images/img_1.png)

Flag: KubSTU(mcp_h4s_n0_4uth_4nd_1_l0v3_1t)
