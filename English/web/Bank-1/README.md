# [web] Bank 1

> **Category:** `web`  
> **CTF:** KubSTU CTF 2026 Spring

---

## Challenge description

Our golden client — Mikhail Galankov — came to us. He says a transfer was made from his account that he didn't initiate. We've been investigating for two weeks and honestly can't figure it out: we have a one-time cryptographic signature on every payment, and the bank also asks for a PIN before debiting. Mikhail swears he never gave anyone his PIN or signature, and we believe him — he's a security specialist by trade.

So you can investigate at your leisure, we've set up a separate test segment — it's a full copy of our bank, just with test money and a handful of users inside (we usually don't put more than ten people in there). Mikhail's login there is the same — mgalankov@4274. Unfortunately, the admin forgot to include his account password in the ticket, but you're experienced enough.

Category: Web · JWT · IDOR

What the challenge says:
The "golden partner" login is mgalankov@4274.
His user_id is 10. The flag shop is only accessible to this user — we need to "become" him.

## Step 1. Register as a regular client

Go to /register, fill in anything:
- Name/Surname — anything (Cyrillic required).
- Date of birth — just needs to be 18+.
- Driver's license — any digits.
- E-mail — any unique email.
- Password — any ≥6 characters.
- PIN — 8 digits.

Click "Register", remember the generated login (something like ppoc@4710).
Log in and immediately turn on Burp in interception mode.

## Step 2. Extract the JWT from the cookie

In Burp, look at any response from the server after login. In Set-Cookie we find:
Set-Cookie: access_token_cookie=eyJhbGciOiJIUzI1NiIsInR5...; HttpOnly; Path=/
Copy the value, go to https://jwt.io, paste it in the left field. On the right we see:
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
Algorithm is HS256. Perfect for offline brute-forcing.

## Step 3. Brute-force the JWT secret using rockyou

Save the full token to jwt.txt. Run hashcat:
hashcat -a 0 -m 16500 jwt.txt /usr/share/wordlists/rockyou.txt
Within seconds:
eyJhbGciOiJIUz...:facetoface
The secret is facetoface. It's a dictionary word, right there in rockyou.
Alternative without hashcat — jwt_tool.py <jwt> -C -d rockyou.txt, or the GUI jwt-cracker.

## Step 4. Forge JWT as mgalankov@4274

Back on jwt.io:
- Paste our current token in the left field.
- In VERIFY SIGNATURE at the bottom, type facetoface in the "secret" field — we see the green "Signature Verified".
- In the right payload pane, change:
  - "sub": "13" → "sub": "10"
  - "username": "ppoc@4710" → "username": "mgalankov@4274"
  - optionally push exp further out.
- The new token is instantly recalculated on the left.

Copy the new JWT. In Burp, in any request (e.g. GET /dashboard), Right Click → Send to Repeater, replace the cookie in the header:
Cookie: access_token_cookie=<new_forged_JWT>
Hit Send. The response shows mgalankov's dashboard: balance 1,500,000 ₽, his real transfer history. Congratulations — we're inside the golden partner's account.

From this point, it's easiest to work through Match & Replace in Burp Proxy (Settings → Match & Replace → add a rule for the cookie), so the forged JWT is automatically sent with every request.

## Step 5. Get the purchase token from the Telegram bot

The challenge mentions a bot like @capy_capy_bot. In Telegram:
- Open a dialog with the bot → Start.
- Send the /token command.
- The bot replies with a token string (something like: t_8a3f...). Copy it.

## Step 6. Go to the shop and initiate a purchase

In the browser (with the spoofed cookie), go to /partners → link to "Flag Shop". We see a list of products.
Click "Buy" on the first flag, on the next page paste the token from the bot. The server opens a transfer form with pre-filled fields to_account=FLAG_SHOP, amount=1000.00, description=Purchase... and asks for the PIN.

We don't know mgalankov's PIN (it's 12 digits, can't be brute-forced in reasonable time). But at the bottom of the form there's a "Decline PIN" button. Click it.

We intercept this request in Burp — it looks like this:
POST /transfer HTTP/1.1
Host: target
Cookie: access_token_cookie=<forged JWT>
Content-Type: application/x-www-form-urlencoded

skip_pin=1&to_account=FLAG_SHOP&amount=1000.00&description=Purchase%3A+...&product_id=1&token=t_8a3f...
Send it, the server redirects to /pending_transactions. On this page we see a new entry "Purchase..." with status "unconfirmed". Note its id (it's in the URL of /verify_transaction/<id> — e.g. 12).

## Step 7. Here's where the vulnerability triggers — /receipt/<id> without is_verified check

Open the receipt of the unconfirmed transaction directly in the browser:
http://target/receipt/12
The server should have said "receipt not yet available" — but it calmly serves the receipt page with the Transaction Signature field. Example:
Transaction Signature: ab3f4e91cc2d7a55
This is a valid signature for the already created transaction id=12. The server generated it on skip_pin=1 and stored it in the DB in advance, even though the transaction is still in "pending" status. This is the leak / IDOR-like logic bug.
Copy ab3f4e91cc2d7a55.

## Step 8. Confirm the transaction with the leaked signature

Go to GET /verify_transaction/12 (or click the "confirm" link on the pending page). A signature input form opens — paste ab3f4e91cc2d7a55 and submit.

In Burp we see:
POST /verify_transaction/12 HTTP/1.1
Cookie: access_token_cookie=<forged JWT>

signature=ab3f4e91cc2d7a55
The server compares the signature with the recalculated one from signature_timestamp — it matches, sets is_verified=True, triggers the Telegram bot /api/approve_purchase. The bot sends us the flag in DM.

The bank UI shows a green banner "Transaction confirmed successfully! Flag sent to Telegram bot." — go to TG, grab the flag.

Summary — why this works:
- JWT secret is dictionary-based (facetoface from rockyou), HS256, cracked in seconds.
- The receipt page /receipt/<id> has no is_verified check — the signature of an unconfirmed transaction leaks.
- In the skip_pin=1 branch, the server pre-stores a valid signature in the DB, when it should have left the field empty or generated it only upon actual confirmation.
