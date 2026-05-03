# [forensics] Tunnel?

> **Категория:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Файлы к заданию</summary>

| Файл | Тип |
|------|-----|
| [Krasnodar.pcap](./files/img_1.pcap) | `pcap` |

</details>

---

Наш отдел ИБ зафиксировал подозрительную активность на одном из рабочих компьютеров. Похоже, злоумышленник смог вынести какие-то данные, используя нестандартный канал связи.

В файле Krasnodar.pcap содержится десятки тысяч пакетов различных протоколов (TCP, UDP, ICMP). Большинство из них — это имитация обычного веб-трафика (HTTP/HTTPS на портах 80, 443, 8080).
При фильтрации по протоколу DNS (dns) можно заметить большое количество запросов к поддоменам exfiltrate.kubstu-ctf.ru.Запросы выглядят как vXX.YYYY.exfiltrate.kubstu-ctf.ru, где:
vXX - порядковый номер пакета (от 00 до 20).
YYYY - hex-кодированные данные.
Извлечение флага:—  Необходимо отфильтровать пакеты с IP 192.168.1.50;— Собрать все hex-значения из поддоменов в правильном порядке (v00, v01, v02...);— Декодировать hex в строку.
Пример команды для извлечения (tshark):
  tshark -r Krasnodar.pcap -Y "dns.qry.name contains exfiltrate.kubstu-ctf.ru" -T fields -e dns.qry.name | grep "^v" | sort -u | cut -d'.' -f2 | tr -d '\n' | xxd -r -p

## 🚩 Флаг

```
KubSTU{d0nt_tru5t_th3_dn5_qu3r135_v1a_h3x}
```
