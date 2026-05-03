# [network] Nut legends

> **Category:** `network`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [LightA.pkt](./files/img_1.pkt) | `pkt` |

</details>

---


![image.png](./images/img_2.png)

An anomaly has been detected in the network topology. Direct access to the target node is blocked at several OSI model layers. You are provided with an entry point (PC Cooper R.) and a single artifact — an image file. Restore the access chain and grab the flag.

Writeup:
We see that for some reason the server doesn't respond to pings, even though the cable is connected.

Analysis: The `show vlan brief` command on the switch shows that the server is on port Fa0/10 (VLAN 1), but it should be in VLAN 20 (port Fa0/2).

Solution: We switch the server cable to port Fa0/2. Now the server is in its correct logical segment.

Alternative solution: Reconfigure the VLAN on the connected port.

Once we see pings from the PC to the server going through, we open the web browser from the PC.

![image.png](./images/img_3.png)

Flag: kubstu(end_user_license_agreement)
