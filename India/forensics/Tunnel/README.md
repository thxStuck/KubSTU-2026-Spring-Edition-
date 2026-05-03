# [forensics] Tunnel

> **श्रेणी:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

---

हमारे सूचना सुरक्षा विभाग ने एक कार्य कंप्यूटर पर संदिग्ध गतिविधि दर्ज की। ऐसा लगता है कि हमलावर ने एक अमानक संचार चैनल का उपयोग करके कुछ डेटा बाहर निकाल लिया।   

                  

[Krasnodar.pcap](./files/Krasnodar.pcap)

1. फ़ाइल __Krasnodar.pcap__ में विभिन्न प्रोटोकॉल (TCP, UDP, ICMP) के हज़ारों पैकेट हैं। उनमें से अधिकांश सामान्य वेब ट्रैफ़िक (पोर्ट 80, 443, 8080 पर HTTP/HTTPS) की नकल हैं।
2. DNS प्रोटोकॉल (__dns__) द्वारा फ़िल्टर करने पर __exfiltrate.kubstu-ctf.ru__ के सबडोमेन पर बड़ी संख्या में अनुरोध देखे जा सकते हैं।
   अनुरोध __vXX.YYYY.exfiltrate.kubstu-ctf.ru__ जैसे दिखते हैं, जहाँ:
   - __vXX__ - पैकेट का क्रम संख्या (00 से 20 तक)।
   - __YYYY__ - hex-एन्कोडेड डेटा।
3. फ़्लैग निकालना:
   —  IP __192.168.1.50__ वाले पैकेट फ़िल्टर करने होंगे;
   — सबडोमेन से सभी hex-मान सही क्रम (v00, v01, v02...) में एकत्र करें;
   — hex को स्ट्रिंग में डिकोड करें।

निकालने के लिए कमांड का उदाहरण (tshark):

  tshark -r Krasnodar.pcap -Y "dns.qry.name contains exfiltrate.kubstu-ctf.ru" -T fields -e dns.qry.name | grep "^v" | sort -u | cut -d'.' -f2 | tr -d '\n' | xxd -r -p

फ़्लैग: KubSTU{d0nt_tru5t_th3_dn5_qu3r135_v1a_h3x}