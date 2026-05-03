# [web] CapyAgro Crop Rescue

> **Category:** `web`  
> **CTF:** KubSTU CTF 2026 Spring

---

Challenge description:
A control system failure has occurred in experimental greenhouse #3 on the CapyAgro premises. The on-site engineers can't access the control panel. The plants are dying. As external auditors, you need to find a way to restore control over the system and return the parameters to normal.

## Solution

1) After registering, try to modify your virtual sectors
2) Intercept and analyze the sent packet
3) Analyze the target sector and get the target device ID
4) Use this to send new values to the CapyAgro sector by substituting the device ID
5) Stabilized the sector and got the flag

## 🚩 Flag

KubSTU(Sav3d_th3_CapyArg0S3ct0r)
