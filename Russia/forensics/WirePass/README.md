# [forensics] WirePass

> **Категория:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

---

Арктическая разведка засекла аномальную активность в секретной сети Пингвиньего Командования. По агентурным данным, между двумя узлами полевой инфраструктуры велась передача оперативных документов, связанных с военной операцией против Капибаровска.

Нашим аналитикам удалось перехватить сетевой дамп, но обнаружилось, что оперативники не так просты: данные передавались по зашифрованному каналу с использованием собственного протокола.


[challenge.pcap](./files/challenge.pcap)

---

## Обзор

Дан pcap-файл с сетевым трафиком между двумя узлами (172.20.0.2 и 172.20.0.3). Среди большого количества шумового трафика (HTTP, DNS, FTP, ICMP, SYN-сканирование, TLS-хэндшейки, случайные TCP/UDP) скрыты два ключевых потока:

1. **Порт 9999** — передача пароля в открытом виде
2. **Порт 31337** — передача зашифрованного ZIP-архива по собственному бинарному протоколу

---

## Шаг 1: Разведка трафика

Открываем `challenge.pcap` в Wireshark. Видим \~1500 пакетов разных протоколов.

Начинаем с анализа TCP-потоков. В меню Wireshark: **Statistics → Conversations → TCP**.

Среди множества соединений находим два интересных на нестандартных портах:

- Соединение на **порт 9999** (небольшой объём данных)
- Соединение на **порт 31337** (заметный объём бинарных данных)

### Фильтрация

```
tcp.port == 9999
```

---

## Шаг 2: Извлечение пароля

Применяем фильтр `tcp.port == 9999` и открываем TCP-поток (**Follow → TCP Stream**).

Видим:

```
PASS:IcyFl1pp3r$2026
ACK:OK
```

**Пароль:** `IcyFl1pp3r$2026`

> **Примечание:** В трафике есть FTP-сессии с другими паролями (`p@ssw0rd123`, `f1sh_l0ver` и т.д.) — это ложные следы. Настоящий пароль передаётся на порту 9999.

---

## Шаг 3: Анализ бинарного протокола

Фильтруем трафик на порт 31337:

```
tcp.port == 31337
```

Открываем TCP-поток (**Follow → TCP Stream**, показать как **Raw/Hex**).

Видим структуру данных:

| Смещение | Размер | Поле | Значение |
|----|----|----|----|
| 0 | 4 | Магия | `58 46 45 52` ("XFER") |
| 4 | 16 | XOR-ключ | `4a 7f 2b 91 de 33 a8 5c e1 6d f0 19 87 c4 55 3e` |
| 20 | 4 | Длина данных (BE) | Размер зашифрованных данных |
| 24 | N | Данные | XOR-зашифрованный ZIP-архив |

---

## Шаг 4: Извлечение и расшифровка

### Вариант A: Ручной (Python)

```python
import io
import struct
import pyzipper
from scapy.all import rdpcap, TCP, Raw

packets = rdpcap("challenge.pcap")

# Собираем TCP-поток на порт 31337 (данные от клиента)
segments = []
for pkt in packets:
    if pkt.haslayer(TCP) and pkt.haslayer(Raw) and pkt[TCP].dport == 31337:
        segments.append((pkt[TCP].seq, bytes(pkt[Raw].load)))

segments.sort(key=lambda x: x[0])
seen = set()
stream = b""
for seq, data in segments:
    if seq not in seen:
        seen.add(seq)
        stream += data

# Парсим заголовок
magic = stream[:4]        # b"XFER"
xor_key = stream[4:20]    # 16-байтный XOR-ключ
data_len = struct.unpack(">I", stream[20:24])[0]
encrypted = stream[24:24 + data_len]

# XOR-расшифровка
decrypted = bytes([b ^ xor_key[i % 16] for i, b in enumerate(encrypted)])

# Извлечение из ZIP
buf = io.BytesIO(decrypted)
with pyzipper.AESZipFile(buf, 'r') as zf:
    zf.setpassword(b"IcyFl1pp3r$2026")
    for name in zf.namelist():
        print(f"--- {name} ---")
        print(zf.read(name).decode("utf-8"))
```

### Вариант B: Wireshark + CyberChef

1. В Wireshark: **Follow TCP Stream** (порт 31337), формат **Raw**, сохранить как файл `raw_stream.bin`
2. Отрезать первые 4 байта (магия "XFER")
3. Взять байты 4–19 — это XOR-ключ
4. Взять байты 20–23 — длина (big-endian)
5. Взять данные с байта 24 — зашифрованный архив
6. В CyberChef: **XOR** с ключом → скачать результат как `.zip`
7. Распаковать с паролем `IcyFl1pp3r$2026`

---

## Шаг 5: Получение флага

В архиве находится файл `mission_report.txt` — рапорт пингвиньего командования о захвате Капибаровска. В конце документа:

```
СЕКРЕТНЫЙ КОД ОПЕРАЦИИ: KubSTU{p1ngu1n_0p_k4p1b4r0v5k_f4ll5}
```

---

## Флаг

```
KubSTU{p1ngu1n_0p_k4p1b4r0v5k_f4ll5}
```


