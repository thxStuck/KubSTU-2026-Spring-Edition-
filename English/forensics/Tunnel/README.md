# [forensics] Tunnel?

> **Category:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [Krasnodar.pcap](./files/img_1.pcap) | `pcap` |

</details>

---

Our information security department detected suspicious activity on one of the workstations. It appears the attacker managed to exfiltrate some data using a non-standard communication channel.

The file Krasnodar.pcap contains tens of thousands of packets of various protocols (TCP, UDP, ICMP). Most of them simulate normal web traffic (HTTP/HTTPS on ports 80, 443, 8080).

When filtering by DNS protocol (dns), you can notice a large number of queries to subdomains of exfiltrate.kubstu-ctf.ru. The queries look like vXX.YYYY.exfiltrate.kubstu-ctf.ru, where:
- vXX is the packet sequence number (from 00 to 20).
- YYYY is hex-encoded data.

Extracting the flag: filter packets with IP 192.168.1.50; collect all hex values from the subdomains in the correct order (v00, v01, v02...); decode hex to string.

Example extraction command (tshark):
  tshark -r Krasnodar.pcap -Y "dns.qry.name contains exfiltrate.kubstu-ctf.ru" -T fields -e dns.qry.name | grep "^v" | sort -u | cut -d'.' -f2 | tr -d '\n' | xxd -r -p

## 🚩 Flag

```
KubSTU{d0nt_tru5t_th3_dn5_qu3r135_v1a_h3x}
```
