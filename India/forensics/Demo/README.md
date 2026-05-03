# [forensics] Demo

> **श्रेणी:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 चुनौती की फ़ाइलें</summary>

| फ़ाइल | प्रकार |
|------|-----|
| [Demo.rar](./files/img_1.rar) | `rar` |

</details>

---

सुरक्षा ऑडिट के दौरान कंपनी के वेब सर्वर पर संदिग्ध गतिविधियाँ पाई गईं। यह माना जा रहा है कि हमलावर नेटवर्क में घुसने, डेटाबेस सर्वर तक पहुँचने और गोपनीय जानकारी चुराने में सफल रहा।
फ़्लैग का प्रारूप: KubSTU{…}।
बताएं कि प्रारंभिक पहुँच किस भेद्यता की सहायता से प्राप्त की गई और उसने क्या अपलोड किया? उसके बाद हमलावर किस उपयोगकर्ता के नाम से काम कर रहा था? क्या कॉपी किया? उदाहरण: KubSTU{XSS,p0wny.php,Administrator,data.txt}
समाधान:
वेब सर्वर पर Apache के access.log का विश्लेषण करते समय (फ़ाइल /home/ubuntu/Victim-Web/var/log/apache2/access.log) आपको वैध गतिविधि की सैकड़ों प्रविष्टियाँ मिलेंगी। लेकिन, उनमें से यह प्रविष्टि स्पष्ट रूप से दिखाई देती है:
192.168.1.100 - - [26/Mar/2026:10:16:05 +0300] "GET /index.php?id=1%20UNION%20SELECT%201,%27%3C%3Fphp%20system(%24_GET%5B%22cmd%22%5D)%3B%20%3F%3E%27%20INTO%20OUTFILE%20%27/var/www/html/uploads/shell.php%27 HTTP/1.1" 200 12 "-" "sqlmap/1.6.12 (http://sqlmap.org)"
यहाँ स्पष्ट SQLi और उसके बाद shell.php अपलोड है।
इसके बाद हमलावर ने शायद किसी तरह डेटाबेस से कनेक्ट किया, लेकिन उसे एक्सेस कहाँ से मिला?
सर्विस की संरचना का विश्लेषण करने पर बहुत सारा रोचक डेटा दिखाई देता है। IP, कुंजियाँ और username। हमलावर ने स्पष्ट रूप से डेटाबेस सर्वर पर dbadmin उपयोगकर्ता की निजी SSH-कुंजी का पथ खोज लिया: /home/www-data/.ssh_key_key।
फ़ाइल /home/ubuntu/Victim-DB/var/log/auth.log में आपको वेब सर्वर के IP-पते (192.168.1.10) से dbadmin उपयोगकर्ता का सफल SSH-कनेक्शन मिलेगा।
victim-db sshd[5680]: Accepted publickey for dbadmin from 192.168.1.10 port 54323 ssh-rsa SHA256:hK6cLRP4m5w60fHK1BGmWooBTXIWz+vtVHmuH/luoVQ
इसके बाद dbadmin उपयोगकर्ता के कमांड इतिहास का विश्लेषण दिखाता है कि हमलावर ने गोपनीय DB तक पहुँच प्राप्त की और डेटा कॉपी किया।
बस इतना ही, फ़्लैग बनाते हैं।
KubSTU{SQLi,shell.php,dbadmin,confidential_data.sql}
