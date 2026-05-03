# [web] Deadlock

> **Category:** `web`  
> **CTF:** KubSTU CTF 2026 Spring

## Legend

Here and there. Frontend to backend and flag. In short, it's simple. Just go and grab the flag from /admin.

## Here and there. Frontend to backend and the flag is ready. In short, it's simple — just go and grab the flag from /admin 

## Problem Description

We have two servers:

- **Proxy** (port 5000) - accepts requests from users
- **Backend** (port 8081) - not directly accessible, only through the proxy

The backend has an admin panel `/admin`, accessing which requires the header `X-Admin-Access: true`.

But the proxy **removes** this header from all requests and adds `X-Forwarded-For`.

## Protection

If you send a direct request to the proxy at `/admin` with the header:

```http
GET /admin HTTP/1.1
X-Admin-Access: true
```

  The proxy removes the header → the backend won't return the flag.  

## **Vulnerability**

The proxy has a **[0.CL](https://0.cl/) Desync** — it triggers when it sees Content-Length:\r\n (with a newline and space).
In this mode, the proxy **does not modify** the second request (doesn't remove headers and doesn't add X-Forwarded-For).

## **Bypass**

We send **one** request to port 5000, which contains **two** requests inside:

1. **First (normal)** — the proxy processes it and removes headers
2. **Second (smuggled)** — the proxy doesn't see it, passes it as-is to the backend

The backend receives the second request to /admin with the header X-Admin-Access: true and without X-Forwarded-For → returns the flag.

## **Final Payload**

```javascript
GET / HTTP/1.1
Host: admin.challenge.local:5000
Content-Length:
 67
Connection: keep-alive

GET /admin HTTP/1.1
Host: localhost:8081
X-Admin-Access: true
```

## **Flag**

```javascript
KubSTU{Pipelined_Smuggling_Success_5521}
```

  