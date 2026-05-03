# [web] Deadlock

> **Category:** `web`  
> **CTF:** KubSTU CTF 2026 Spring

---

Lore:
Here and there. Back and forth, frontend into backend and the flag. Basically it's simple. Just go grab the flag from /admin.

Challenge essence:
We have two servers:
- Proxy (port 5000) — accepts requests from users
- Backend (port 8081) — not directly accessible, only through the proxy

The backend has an admin panel /admin, access to which requires the header X-Admin-Access: true.
But the proxy strips this header from all requests and adds X-Forwarded-For.

Protection:
If you send a direct request to the proxy at /admin with the header:
GET /admin HTTP/1.1
X-Admin-Access: true
The proxy will strip the header → the backend won't give the flag.

Vulnerability:
The proxy has a 0.CL Desync — it triggers when it sees Content-Length:\r\n (with a newline and space). In this mode, the proxy doesn't modify the second request (doesn't strip headers and doesn't add X-Forwarded-For).

Bypass:
We send one request to port 5000 that contains two requests inside:
1. First (normal) — the proxy processes it and strips headers
2. Second (smuggled) — the proxy doesn't see it, passes it as-is to the backend

The backend receives the second request to /admin with the X-Admin-Access: true header and without X-Forwarded-For → returns the flag.

Final Payload:
GET / HTTP/1.1
Host: admin.challenge.local:5000
Content-Length:
 67
Connection: keep-alive

GET /admin HTTP/1.1
Host: localhost:8081
X-Admin-Access: true

## 🚩 Flag

```
KubSTU{Pipelined_Smuggling_Success_5521}
```
