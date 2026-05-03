# [network] The skeleton key

> **Category:** `network`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [3 in 1 .pkt](./files/img_1.pkt) | `pkt` |

</details>

---

Message: "Hey, we've got some kind of chaos on one of the switches. Errors keep popping up on the ports, logs are flooded, but because of some configuration lock I can't get through the access levels to figure out which interface is malfunctioning.

Take a look at what's going on — I need not just a report, but a solution so the network stops throwing warnings. And don't even think about wiping the config!"

![image.png](./images/img_2.png)

Writeup:

1. Search for and find the problematic CORE SWITCH.

![image.png](./images/img_3.png)

2. In the banner, the player receives a Base64-encoded password to access the switch settings.
3. After entering `enable`, the player is prompted for a password — the one just obtained.
4. After running `show interfaces`, the player needs to find the flag among the port descriptions.
