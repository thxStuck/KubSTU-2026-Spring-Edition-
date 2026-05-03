# [web] Bank 2

> **Category:** `web`  
> **CTF:** KubSTU CTF 2026 Spring

  

Thank you so much for the analysis of Mikhail's case. The development team carefully fixed everything based on your report, ran regression tests, QA signed off — no one will exploit that hole again.

But the problem is that reports keep coming in. This week — three more cases, and again from our premium clients, and again the same pattern: unauthorized transfer to the same shop, signature is valid, no outsider knew the PIN, logs are clean. Apparently, we only closed one door, and the attacker found the adjacent one.

We've redeployed the test segment with a fresh, already patched build. Conditions are the same: the victim is Mikhail Galankov, mgalankov@4274.

**Category:** Web · JWT · Parameter Tampering · Broken Signature Binding 

---

## What the challenge description tells us

Same as v1: the target is `mgalankov@4274`, `user_id = 10` (actually `4` in the fresh seeded DB).

In v2, the developers "tightened" two things:

- In unconfirmed transactions (`skip_pin=1`), the `signature` field is now `None` — you can't peek anything from the receipt.
- `/receipt/<id>` redirects unconfirmed transactions to `/verify_transaction/<id>`.

However, **signature binding to the user disappeared** in the `/transfer` endpoint. This is how the new exploit works — **injecting someone else's valid** `transaction_timestamp + transaction_signature` pair into the FLAG_SHOP purchase confirmation form.

---

## Step 1. Register as a regular client (we actually need TWO accounts)

Register the **first** account — this will be the "victim" (more precisely, our "signature donor"). Remember the login/password/PIN. The PIN is ours, we set it ourselves — we'll need it.

Log in, open Burp, intercept the cookie with the JWT.

---

## Step 2. Brute-force the JWT secret

Put the JWT in `jwt.txt`:

```bash
hashcat -a 0 -m 16500 jwt.txt /usr/share/wordlists/rockyou.txt
```

After a few seconds the secret is `ifeveryonecared3` (also from rockyou, v2 changed the dictionary word but not the concept itself).

---

## Step 3. Forge a JWT for `mgalankov@4274` on [jwt.io](http://jwt.io)

On **[jwt.io](http://jwt.io)**:

1. On the left — our current JWT.
2. At the bottom in **VERIFY SIGNATURE → secret** enter `ifeveryonecared3`, you'll see green "Signature Verified".
3. In the payload change `"sub"` to `"10"`, `"username"` to `"mgalankov@4274"`. Optionally — push `exp` further out.
4. On the left you get the new token.

In Burp — Match & Replace by cookie, or manually in Repeater:

```
Cookie: access_token_cookie=<forged JWT for mgalankov>
```

Request `GET /dashboard` — the response shows mgalankov's account (balance 1.5M, history of seven transfers). We're in.

---

## Step 4. Get the token from the Telegram bot

Command `/token` to the bot → copy the token string.

---

## Step 5. Go to the shop and initiate a purchase

With the forged cookie:

1. `/partners` → link "Flag Shop" (it's already accessible since the server sees `username == 'mgalankov@4274'`).
2. Click "Buy" on any product, on the next page paste the token from the bot.
3. A transfer form opens with pre-filled fields for FLAG_SHOP + PIN request.

We don't know mgalankov's PIN. But in this version `skip_pin=1` no longer leaves a signature in the DB — the v1 path is closed. We go a different route.

---

## Step 6. In parallel, extract a "legitimate" `(timestamp, signature)` pair

## from our own account

Open a **second** browser window (or second profile), log in **under the regular user** registered in step 1. The PIN is ours — we know it.

Make a "normal" transfer between your own accounts (e.g., transfer 1 ruble from `ACC003` to `ACC001` or to any other existing account) up to the point of PIN entry. Enable interception in Burp.

The JS in `transfer.html` first sends an XHR to `/api/get_signature` with the PIN. Intercept the response:

```http
POST /api/get_signature HTTP/1.1
Cookie: access_token_cookie=<JWT of our own user>
Content-Type: application/json

{"pin_code":"12345678"}
```

Response:

```json
{
  "date": "2026-04-25",
  "time": "00:11:02",
  "timestamp": 1745532662,
  "signature": "9f3b81c4ea5d6178"
}
```

This pair `timestamp=1745532662, signature=9f3b81c4ea5d6178` is **mathematically valid**. The server generated it specifically for our user, but in `/transfer` this binding **is not verified**. This is the vulnerability.

Save the pair, continue intercepting — next the JS will assemble a large POST form to `/transfer`. We **don't need to send** that one, we only needed to intercept the `/api/get_signature` response. Drop the request.

---

## Step 7. Confirm the FLAG_SHOP purchase under mgalankov's cookie

Switch back to the window/tab with the forged JWT. Open the FLAG_SHOP transfer form (step 5). In Burp catch the **first step** (POST to `/transfer`, the one that `pinForm` sends via XHR to `/api/get_signature`) — actually it's easier to catch the second POST after PIN entry. But we don't know the PIN.

### Solution: assemble the needed POST manually in Burp Repeater

Take the template of a regular `/transfer` submission and manually fill in the fields:

```http
POST /transfer HTTP/1.1
Host: target
Cookie: access_token_cookie=<forged JWT for mgalankov>
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
```

The key thing — there **must not be** `skip_pin=1` (otherwise it goes to the other branch), and both fields `transaction_timestamp` + `transaction_signature` must be present, taken from our legitimate `/api/get_signature` (Step 6).

Click **Send**.

The server does:

1. Checks that we are `mgalankov@4274` (we are, because of the forged JWT).
2. Takes `transaction_timestamp = 1745532662`, recalculates the signature from this timestamp — gets the same `9f3b81c4ea5d6178`.
3. Compares: `transaction_signature == verification_signature` — yes.
4. There's no check for "who was this signature issued to" — this is where security breaks down.
5. For `to_account=FLAG_SHOP`, the server itself shifts the date by +7 days and recalculates the signature with the new timestamp, stores the transaction as `is_verified=True`.
6. Calls the Telegram bot `/api/approve_purchase` — the flag arrives in TG.

In the response you see a redirect to `/flag_shop` and a green banner "Purchase confirmed! Flag sent to the Telegram bot."

---

## Alternative — even simpler

Specifically for `FLAG_SHOP`, the server will overwrite `transaction_signature` with its own calculation for `t+7d` anyway. That is, in this branch **the signature value is effectively not verified** — as long as the field is present.

If you're too lazy to extract a legitimate signature from your own session, you can send:

```
transaction_timestamp=1745532662
transaction_signature=0000000000000000
```

…and the FLAG_SHOP branch will work exactly the same way. But the "proper" demonstration of the bug is precisely injecting someone else's valid signature: in the general case (not FLAG_SHOP), this vulnerability allows making **any transfers from mgalankov's account without knowing his PIN** — which is the main risk.

---

## Summary — why this works

1. The JWT secret is still a dictionary word (`ifeveryonecared3`), taken from rockyou.
2. In `/transfer` (the `transaction_signature` branch), the server-side binding of the issued signature to the user and parameters is missing — any valid `(timestamp, sig)` pair is accepted.
3. Your own valid pair is easily obtained via `/api/get_signature` on your own account (your PIN) and injected into the request under mgalankov's forged JWT.

---

## Mitigation

- Bind the issued signature to `(user_id, to_account, amount, description)` in a one-time whitelist (as done in `signature_session.py` in v1, but for some reason removed in v2).
- At the business logic level, FLAG_SHOP should not "replace" the signature with a server one, but issue the correct timestamp to the client in advance and verify the signature honestly.
- JWT/Flask secrets — long random strings, via env, no dictionary words.

  