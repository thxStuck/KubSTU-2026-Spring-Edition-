# [forensics] Tunnel

> **Category:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

---

Our information security department detected suspicious activity on one of the workstations. It appears the attacker managed to exfiltrate some data using a non-standard communication channel.   

                  

[Krasnodar.pcap](./files/Krasnodar.pcap)

1. The file __Krasnodar.pcap__ contains tens of thousands of packets of various protocols (TCP, UDP, ICMP). Most of them are simulated normal web traffic (HTTP/HTTPS on ports 80, 443, 8080).
2. When filtering by the DNS protocol (__dns__), you can notice a large number of queries to subdomains of __exfiltrate.kubstu-ctf.ru__.
   The queries look like __vXX.YYYY.exfiltrate.kubstu-ctf.ru__, where:
   - __vXX__ — the packet sequence number (from 00 to 20).
   - __YYYY__ — hex-encoded data.
3. Extracting the flag:
   — Filter packets with IP __192.168.1.50__;
   — Collect all hex values from the subdomains in the correct order (v00, v01, v02...);
   — Decode hex to string.

Example extraction command (tshark):

  tshark -r Krasnodar.pcap -Y "dns.qry.name contains exfiltrate.kubstu-ctf.ru" -T fields -e dns.qry.name | grep "^v" | sort -u | cut -d'.' -f2 | tr -d '\n' | xxd -r -p

Flag: KubSTU{d0nt_tru5t_th3_dn5_qu3r135_v1a_h3x}