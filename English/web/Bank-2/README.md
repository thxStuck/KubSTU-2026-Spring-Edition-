# [web] Bank 2

> **Category:** `web`  
> **CTF:** KubSTU CTF 2026 Spring

---

Thank you so much for the investigation on Mikhail's case. The development team carefully fixed everything based on your report, ran regression tests, QA signed off — nobody will exploit that vulnerability again.

But the problem is that complaints keep coming in. This week — three more, again from our premium clients, again the same pattern: unauthorized transfer to the same shop, signature is valid, no outsider knew the PIN, logs are clean. Apparently we only closed one door, and the attacker found the next one.

We've redeployed the test segment with a fresh, already patched build. Same conditions: the victim is Mikhail Galankov, mgalankov@4274.

Category: Web · JWT · Parameter Tampering · Broken Signature Binding

What the challenge says:
Same as v1: target is mgalankov@4274, user_id = 10.
In v2, the developers "tightened" two things:
- In unconfirmed transactions (skip_pin=1), the signature field is now None — nothing to peek from the receipt.
- /receipt/<id> redirects unconfirmed transactions to /verify_transaction/<id>.

However, the signature-to-user binding disappeared from the /transfer endpoint. This is where the new exploit works — injecting someone else's valid (transaction_timestamp, transaction_signature) pair into the FLAG_SHOP purchase confirmation form.

## Step 1. Register as a regular client (we actually need TWO accounts)

Register the first account — this will be our "signature donor". Remember login/password/PIN. The PIN is ours — we set it ourselves — it'll be needed.
Log in, open Burp, intercept the cookie with the JWT.

## Step 2. Brute-force the JWT secret

Put the JWT in jwt.txt:
hashcat -a 0 -m 16500 jwt.txt /usr/share/wordlists/rockyou.txt
Within seconds the secret is ifeveryonecared3 (also from rockyou — v2 changed the dictionary word but not the concept).

## Step 3. Forge JWT as mgalankov@4274 on jwt.io

On jwt.io:
- Left — our current JWT.
- In VERIFY SIGNATURE at the bottom → secret: type ifeveryonecared3, see the green "Signature Verified".
- In payload, change "sub" to "10", "username" to "mgalankov@4274". Optionally push exp further.
- Get the new token on the left.

In Burp — Match & Replace on cookie, or manually in Repeater:
Cookie: access_token_cookie=<forged JWT as mgalankov>
GET /dashboard request — response shows mgalankov's account (balance 1.5M, seven transfer history). We're inside.

## Step 4. Get the token from the Telegram bot

/token command to the bot → copy the token string.

## Step 5. Go to the shop and initiate a purchase

With the forged cookie:
/partners → "Flag Shop" link (already accessible since the server sees username == 'mgalankov@4274').
Click "Buy" on any product, paste the token from the bot on the next page.
A transfer form opens with pre-filled fields for FLAG_SHOP + PIN request.
We don't know mgalankov's PIN. And in this version, skip_pin=1 no longer leaves a signature in the DB — the v1 path is closed. We go a different route.

## Step 6. In parallel, extract a "legitimate" (timestamp, signature) pair from our own account

Open a second browser window (or second profile), log in under the regular user registered in step 1. The PIN is ours — we know it.
Make a "standard" transfer between our own accounts (e.g. transfer 1 ruble from ACC003 to ACC001 or any other existing account) up to the PIN entry point. Turn on interception in Burp.
The JS in transfer.html first sends an XHR to /api/get_signature with the PIN. We intercept the response:
POST /api/get_signature HTTP/1.1
Cookie: access_token_cookie=<JWT of our own user>
Content-Type: application/json

{"pin_code":"12345678"}
Response:
{
  "date": "2026-04-25",
  "time": "00:11:02",
  "timestamp": 1745532662,
  "signature": "9f3b81c4ea5d6178"
}
This pair timestamp=1745532662, signature=9f3b81c4ea5d6178 is mathematically valid. The server generated it for our user, but in /transfer this binding is not checked. This is the vulnerability.
Note the pair. Continue intercepting — next the JS will assemble a big POST form to /transfer. We don't need to send it — we only needed to intercept the /api/get_signature response. Drop the request.

## Step 7. Confirm the FLAG_SHOP purchase under mgalankov's cookie

Return to the window/tab with the forged JWT. We assemble the needed POST manually in Burp Repeater:
POST /transfer HTTP/1.1
Host: target
Cookie: access_token_cookie=<forged JWT as mgalankov>
Content-Type: application/x-www-form-urlencoded

to_account=FLAG_SHOP
&amount=1000.00
&description=%D0%9F%D0%BE%D0%BA%D1%83%D0%BF%D0%BA%D0%B0%3A+%D0%A4%D0%BB%D0%B0%D0%B3+%D0%BE%D1%82+CTF+%D0%B7%D0%B0%D0%B4%D0%B0%D0%BD%D0%B8%D1%8F
&product_id=1
&token=t_8a3f...
&transaction_date=2026-04-25
&transaction_time=00:11:02
&transaction_timestamp=1745532662
&transaction_signature=9f3b81c4ea5d6178

The key thing — skip_pin=1 must NOT be present (otherwise it takes a different branch), and both transaction_timestamp + transaction_signature fields must be present, taken from our legitimate /api/get_signature (Step 6).

Hit Send. The server:
1. Verifies we're mgalankov@4274 (we are, because of the forged JWT).
2. Takes transaction_timestamp = 1745532662, recalculates the signature for this timestamp — gets the same 9f3b81c4ea5d6178.
3. Compares: transaction_signature == verification_signature — yes.
4. No check for "who was this signature issued to" — this is where security breaks down.
5. For to_account=FLAG_SHOP, the server shifts the date by +7 days and recalculates the signature for the new timestamp, stores the transaction as is_verified=True.
6. Triggers the Telegram bot /api/approve_purchase — the flag arrives in TG.

The response shows a redirect to /flag_shop and a green banner "Purchase confirmed! Flag sent to Telegram bot."

Alternative — even simpler:
For FLAG_SHOP specifically, the server overwrites transaction_signature with its own calculation for t+7d anyway. So in this branch, the signature value is not actually checked — as long as the field exists.
If you're too lazy to extract a legitimate signature from your session, you can send:
transaction_timestamp=1745532662
transaction_signature=0000000000000000
...and the FLAG_SHOP branch will work the same way. But the "proper" bug demonstration is injecting someone else's valid signature: in the general case (not FLAG_SHOP), this vulnerability allows making any transfers from mgalankov's account without knowing his PIN — which is the core risk.

Summary — why this works:
- JWT secret is still dictionary-based (ifeveryonecared3), from rockyou.
- In /transfer (the transaction_signature branch), the server-side binding of the issued signature to the user and parameters is gone — any valid (timestamp, sig) pair is accepted.
- We easily obtain our own valid pair via /api/get_signature on our own account (our PIN) and inject it into the request under mgalankov's forged JWT.

Mitigation:
- Bind issued signatures to (user_id, to_account, amount, description) in a one-time whitelist (as done in signature_session.py v1, but for some reason removed in v2).
- At the business logic level, FLAG_SHOP should not "replace" the signature with a server-side one — instead, provide the correct timestamp to the client in advance and verify the signature honestly.
- JWT/Flask secrets — long random values, via env, no dictionary words.
