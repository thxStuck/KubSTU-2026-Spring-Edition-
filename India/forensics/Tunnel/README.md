# [forensics] Tunnel?

> **श्रेणी:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 चुनौती की फ़ाइलें</summary>

| फ़ाइल | प्रकार |
|------|-----|
| [Krasnodar.pcap](./files/img_1.pcap) | `pcap` |

</details>

---

हमारे सूचना सुरक्षा विभाग ने एक कार्य कंप्यूटर पर संदिग्ध गतिविधि दर्ज की। ऐसा लगता है कि हमलावर ने गैर-मानक संचार चैनल का उपयोग करके कुछ डेटा बाहर निकालने में सफलता पाई।

Krasnodar.pcap फ़ाइल में विभिन्न प्रोटोकॉल (TCP, UDP, ICMP) के हज़ारों पैकेट हैं। उनमें से अधिकांश सामान्य वेब-ट्रैफ़िक (पोर्ट 80, 443, 8080 पर HTTP/HTTPS) की नकल हैं।
DNS प्रोटोकॉल (dns) से फ़िल्टर करने पर exfiltrate.kubstu-ctf.ru के सबडोमेन को बड़ी संख्या में अनुरोध दिखाई देते हैं। अनुरोध vXX.YYYY.exfiltrate.kubstu-ctf.ru जैसे दिखते हैं, जहाँ:
vXX - पैकेट का क्रम संख्या (00 से 20 तक)।
YYYY - hex-एन्कोडेड डेटा।
फ़्लैग निकालना: — IP 192.168.1.50 वाले पैकेट फ़िल्टर करने होंगे; — सबडोमेन से सभी hex-मान सही क्रम (v00, v01, v02...) में एकत्र करने होंगे; — hex को स्ट्रिंग में डीकोड करना होगा।
निकालने के लिए कमांड का उदाहरण (tshark):
  tshark -r Krasnodar.pcap -Y "dns.qry.name contains exfiltrate.kubstu-ctf.ru" -T fields -e dns.qry.name | grep "^v" | sort -u | cut -d'.' -f2 | tr -d '\n' | xxd -r -p

## 🚩 फ़्लैग

```
KubSTU{d0nt_tru5t_th3_dn5_qu3r135_v1a_h3x}
```
