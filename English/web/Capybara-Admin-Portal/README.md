# [web] Capybara Admin Portal

> **Category:** `web`  
> **CTF:** KubSTU CTF 2026 Spring


## Challenge Description

The capybara admin is hiding some important secret. We only managed to find out the ID of their account - `239716013`. Extract this secret as soon as possible.

## Step 1: Information Gathering and User Enumeration

We open the main page. We see a login form. Let's try entering random data.

- Entering `test:test` -> Response: `404 User not found in the enclosure`.
- Entering `admin:admin` -> Response: `404 User not found in the enclosure`.


This is a classic **User Enumeration** vulnerability. The server tells us whether a user exists. We start brute-forcing with the `rockyou.txt` list. Quite quickly we find the name `angel`.

- Entering `angel:test` -> Response: `401 Incorrect password for capybara`.


User `angel` exists!


## Step 2: Password Brute-force

Now we brute-force passwords for user `angel` using the same `rockyou.txt` list. We find the correct password: `princess`.


## Step 3: 2FA Bypass (JWT Leak)

After entering the correct credentials, we're redirected to the `/2fa` page. It asks for a 6-digit code. However, if we look at the Network tab (in developer tools) at the `/login` request, we'll see the server returned JSON:

```json
{
  "token": "eyJhbGciOiJIUzI1NiI...",
  "user_id": "679202372644",
  "redirect": "/2fa"
}
```

The server issued us a **JWT token** before 2FA was completed. This is a logic error (2FA Bypass). This token can already be used for API authorization.


## Step 4: API Analysis and Path Traversal

On the 2FA page, open the console (F12). We see logs: `[API] Internal account management endpoint: POST /admin/account/679202372644`


If we try making a request to this endpoint with our token:

```javascript

getAccountData('679202372644')
```

We get a response that we don't have permission for the flag, and the flag is in `239716013`.


If we try directly:

```javascript

getAccountData('239716013')
```

We get `403 Access Error`. The server checks that the ID in the URL matches the ID in our token.


But the API endpoint uses a `path` parameter that doesn't filter directory traversal characters. We can use **Path Traversal** so the path contains both our ID (to pass the check) and the target ID.


## Step 5: Getting the Flag

We craft a request where the path looks like: `/admin/account/679202372644/../239716013`. To prevent the server from "collapsing" the dots before processing in code, we use URL encoding for slashes (`%2f`).


Final request in the browser console:

```javascript

fetch('/admin/account/679202372644%2f..%2f239716013', {
    method: 'POST',
    headers: { 
        'Authorization': 'Bearer ' + localStorage.getItem('jwt'),
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ action: 'fetch_secure_data' })
}).then(res => res.json()).then(console.log);
```


 ![img_1.png](./images/img_1.png)

**Result:** `{"status": "success", "owner": "Chief Capybara", "data": "KubSTU{c4pyb4r4_p4th_tr4v3rs4l_m4st3r}"}`


Flag: `KubSTU{c4pyb4r4_p4th_tr4v3rs4l_m4st3r}`