# [web] Bank 1

> **Category:** `web`  
> **CTF:** KubSTU CTF 2026 Spring

## Description

Our gold client — Mikhail Galankov — came to us. He says a transfer he didn't make went out from his account. We've been investigating for two weeks now and, honestly, we don't understand how: we have a one-time cryptographic signature on every payment, and before debiting, the bank also asks for a PIN. Mikhail swears he didn't share his PIN or signature with anyone, and we believe him — he's a security specialist by profession.

So you can dig around freely, we've set up a separate test segment — it's a complete copy of our bank, just with test money and a handful of users inside (we usually throw in about ten people ourselves, no more). Mikhail's login there is the same — mgalankov@4274. The admin unfortunately forgot to include his account password in the ticket, but you're experienced.

**Category:** Web · JWT · IDOR 

---

## What the challenge description tells us

- The login of the "gold partner" is `mgalankov@4274`.
- His `user_id` is `10` (see the description; in the fresh seeded DB he's actually `4`, but we go with what we're given).
- The shop with the flag is accessible **only** to this user — we need to "become" him.

---

## Step 1. Register as a regular client

Go to `/register`, fill in anything:

- First/Last name — anything (Cyrillic required).
- Date of birth — as long as it's 18+.
- Driver's license — any digits.
- E-mail — any unique one.
- Password — any ≥6 characters.
- PIN — 8 digits.

Click "Register", remember the generated login (something like `ppoc@4710`).

Log in and immediately enable **Burp** in intercept mode.

---

## Step 2. Extract the JWT from cookies

In Burp, look at any response from the server after login. In `Set-Cookie` you'll find:

```
Set-Cookie: access_token_cookie=eyJhbGciOiJIUzI1NiIsInR5...; HttpOnly; Path=/
```

Copy the value, go to **<https://jwt.io>**, paste it in the left field. On the right you'll see:

```json
{
  "fresh": false,
  "iat": 1745030000,
  "jti": "....",
  "type": "access",
  "sub": "13",
  "nbf": 1745030000,
  "exp": 1745033600,
  "username": "ppoc@4710"
}
```

The algorithm is **HS256**. Exactly what we need for offline brute-forcing.

---

## Step 3. Brute-force the JWT secret using `rockyou`

Save the entire token to a file `jwt.txt`. Launch hashcat:

```bash
hashcat -a 0 -m 16500 jwt.txt /usr/share/wordlists/rockyou.txt
```

After a few seconds:

```
eyJhbGciOiJIUz...:facetoface
```

The secret is `facetoface`. It's a dictionary word, sitting right in `rockyou`.

> Alternative without hashcat — `jwt_tool.py <jwt> -C -d rockyou.txt`, or the GUI-based `jwt-cracker`.

---

## Step 4. Forge a JWT for `mgalankov@4274`

Go back to **[jwt.io](http://jwt.io)**:

1. Paste your current token in the left field.
2. At the bottom in **VERIFY SIGNATURE**, enter `facetoface` in the "secret" field, you'll see green "Signature Verified".
3. In the right payload pane, change:
   - `"sub": "13"` → `"sub": "10"`
   - `"username": "ppoc@4710"` → `"username": "mgalankov@4274"`
   - optionally — push `exp` further out.
4. On the left, the new token is instantly recalculated.

Copy the new JWT entirely.

In Burp, in any request (e.g., `GET /dashboard`) do **Right Click → Send to Repeater**, in the header replace the cookie:

```
Cookie: access_token_cookie=<new_forged_JWT>
```

Click **Send**. In the response you'll see mgalankov's dashboard page: balance `1,500,000 ₽`, his actual transfer history. Congratulations — we're inside the gold partner's account.

From this point on, it's easiest to work in the browser via **Match & Replace** in Burp Proxy (Settings → Match & Replace → add a rule for the cookie), then the forged JWT will automatically go with every request.

---

## Step 5. Get the purchase token from the Telegram bot

The challenge description mentions a bot like `@capy_capy_bot`. In Telegram:

1. Open a dialog with the bot → **Start**.
2. Send the command `/token`.
3. The bot responds with a token string (something like: `t_8a3f...`). Copy it.

---

## Step 6. Go to the shop and initiate a purchase

In the browser (with the replaced cookie) go to `/partners` → link to "Flag Shop". You'll see a list of products.

Click "Buy" on the first flag, on the next page paste the token from the bot. The server opens a transfer form with pre-filled fields `to_account=FLAG_SHOP`, `amount=1000.00`, `description=Purchase...` and asks you to enter a PIN.

We don't know mgalankov's PIN (it's 12 digits, can't be brute-forced in a reasonable time). But at the bottom of the form there's a **"Decline PIN"** button. Click it.

Intercept this request in Burp — it looks like this:

```http
POST /transfer HTTP/1.1
Host: target
Cookie: access_token_cookie=<forged JWT>
Content-Type: application/x-www-form-urlencoded

skip_pin=1&to_account=FLAG_SHOP&amount=1000.00&description=Покупка%3A+...&product_id=1&token=t_8a3f...
```

Send it, the server redirects to `/pending_transactions`. On this page, a new entry "Purchase..." appears in "unconfirmed" status. Remember its **id** (it's in the URL of the link `/verify_transaction/<id>` — for example, `12`).

---

## Step 7. This is where the vulnerability triggers — `/receipt/<id>` without `is_verified` check

Open the receipt for the unconfirmed transaction directly in the browser:

```
http://target/receipt/12
```

The server should have said "receipt not yet available" — but it calmly serves the receipt page with the **Transaction Signature** field. Example:

```
Transaction Signature: ab3f4e91cc2d7a55
```

This is a valid signature for the **already created** transaction `id=12`. The server generated it during `skip_pin=1` and stored it in the DB in advance, even though the transaction is still in "pending" status. This is the leak / IDOR-like logic error.

Copy `ab3f4e91cc2d7a55`.

---

## Step 8. Confirm the transaction with the leaked signature

Go to `GET /verify_transaction/12` (or click the "confirm" link on the pending page). A signature input form opens — paste `ab3f4e91cc2d7a55` and submit.

In Burp you'll see:

```http
POST /verify_transaction/12 HTTP/1.1
Cookie: access_token_cookie=<forged JWT>

signature=ab3f4e91cc2d7a55
```

The server compares the signature with one recalculated from `signature_timestamp` — it matches, sets `is_verified=True`, calls the Telegram bot `/api/approve_purchase`. The bot sends us the **flag in DMs**.

In the bank UI, a green banner appears "Transaction confirmed successfully! Flag sent to the Telegram bot." — go to TG, grab the flag.

---

## Summary — why this works

1. The JWT secret is a dictionary word (`facetoface` from rockyou), HS256, cracked in seconds.
2. The receipt page `/receipt/<id>` has no `is_verified` check — the signature of an unconfirmed transaction is leaked.
3. In the `skip_pin=1` branch, the server pre-stores a valid signature in the DB, when it should have left the field empty or only generated it upon actual confirmation.

---

