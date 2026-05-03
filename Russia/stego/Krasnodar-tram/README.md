# [stego] Krasnodar tram

> **Категория:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

---

Мне очень нравятся трамваи в Краснодаре. Это очень удобно, быстро и недорого. Проникнись трамвайным вайбом и найди моё послание.

Начинаем решение с просмотра метаданных.
PS S:\CTF\steg> exiftool 267.jpg
ExifTool Version Number         : 13.45
File Name                       : 267.jpg
Directory                       : .
File Size                       : 491 kB
File Modification Date/Time     : 2026:03:20 11:41:38+03:00
File Access Date/Time           : 2026:03:20 11:41:47+03:00
File Creation Date/Time         : 2026:03:20 11:39:55+03:00
File Permissions                : -rw-rw-rw-
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
Exif Byte Order                 : Big-endian (Motorola, MM)
Software                        : Adobe Photoshop 25.0
Y Cb Cr Positioning             : Centered
XP Keywords                     : Ly9r=
XP Subject                      : wb=135|b20v
Current IPTC Digest             : 33d0317331e9fa7b6be97c6535ab0b74
Object Name                     : exp=85|ZWJp
Source                          : iso=200|Q3N2
Application Record Version      : 4
Keywords                        : aHR0=, dHUu=, cy0x=
Caption-Abstract                : cy0x=
XMP Toolkit                     : Image::ExifTool 13.45
Description                     : dHUu=
Subject                         : Ly9r=
Credit                          : exp=50|Ly9w
Headline                        : wb=35|aHR0
Label                           : recovery fragments
Nickname                        : aHR0=
DCT Encode Version              : 100
APP14 Flags 0                   : [14]
APP14 Flags 1                   : (none)
Color Transform                 : YCbCr
Comment                         : VISIBLE CACHE:.aHR0=.Ly9r=.dHUu=.cy0x=
Image Width                     : 1500
Image Height                    : 1000
Encoding Process                : Baseline DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:4:4 (1 1)
Image Size                      : 1500x1000
Megapixels                      : 1.5

ExifTool Version Number         : 13.45
File Name                       : 678.jpg
Directory                       : .
File Size                       : 709 kB
File Modification Date/Time     : 2026:03:20 11:41:39+03:00
File Access Date/Time           : 2026:03:20 11:41:47+03:00
File Creation Date/Time         : 2026:03:20 11:39:55+03:00
File Permissions                : -rw-rw-rw-
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
Exif Byte Order                 : Big-endian (Motorola, MM)
Software                        : Adobe Photoshop 25.0
Y Cb Cr Positioning             : Centered
XP Keywords                     : cHM6=
Current IPTC Digest             : 96af56f5483fe7a0bf425675e771ca21
Object Name                     : exp=35|cHM6
By-line                         : f=50|YXN0
Source                          : Archive
Application Record Version      : 4
Keywords                        : dWJz=, Njk==
Caption-Abstract                : cnUv=
XMP Toolkit                     : Image::ExifTool 13.45
Description                     : f=135|U3VC
Subject                         : cHM6=, cnUv=
Instructions                    : dWJz=
Label                           : recovery fragments
Nickname                        : exp=85|bi5j
DCT Encode Version              : 100
APP14 Flags 0                   : [14], Encoded with Blend=1 downsampling
APP14 Flags 1                   : (none)
Color Transform                 : YCbCr
Comment                         : VISIBLE CACHE:.cHM6=.dWJz=.cnUv=.Njk==
Image Width                     : 1400
Image Height                    : 960
Encoding Process                : Progressive DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:4:4 (1 1)
Image Size                      : 1400x960
Megapixels                      : 1.3
В метаданных обеих фотографий видны блоки по 4 символа и = в конце. Можно предположить, что это всё принадлежит одной b64 строке. Выписываем все блоки и просим нейросеть поиграться с блоками и найти рабочую строку.
import base64

# Блоки из 267.jpg (нечётные позиции)
blocks_267 = ['Ly9r=', 'aHR0=', 'dHUu=', 'cy0x=', 'cy0x=', 'dHUu=', 'Ly9r=', 'aHR0=', 'aHR0=', 'Ly9r=', 'dHUu=', 'cy0x=']

# Блоки из 678.jpg (чётные позиции)
blocks_678 = ['cHM6=', 'dWJz=', 'Njk==', 'cnUv=', 'cHM6=', 'cnUv=', 'dWJz=', 'cHM6=', 'dWJz=', 'cnUv=', 'Njk==']

print("Декодирование блоков из 267.jpg:")
for i, block in enumerate(blocks_267, 1):
    try:
        decoded = base64.b64decode(block).decode('utf-8', errors='replace')
        print(f"  {i:2d}. {block:8s} -> {repr(decoded)}")
    except Exception as e:
        print(f"  {i:2d}. {block:8s} -> Ошибка: {e}")

print("\nДекодирование блоков из 678.jpg:")
for i, block in enumerate(blocks_678, 1):
    try:
        decoded = base64.b64decode(block).decode('utf-8', errors='replace')
        print(f"  {i:2d}. {block:8s} -> {repr(decoded)}")
    except Exception as e:
        print(f"  {i:2d}. {block:8s} -> Ошибка: {e}")

# Теперь чередуем ихprint("\n\nЧередование блоков (267 нечётные, 678 чётные):")
interleaved = []
max_len = max(len(blocks_267), len(blocks_678))

for i in range(max_len):
    if i < len(blocks_267):
        interleaved.append(('267', blocks_267[i]))
    if i < len(blocks_678):
        interleaved.append(('678', blocks_678[i]))

# Декодируем чередующуюся последовательностьprint("\nПоследовательное декодирование:")
full_string = ""for source, block in interleaved:
    try:
        decoded = base64.b64decode(block).decode('utf-8', errors='replace')
        full_string += decoded
        print(f"{source}: {block:8s} -> {repr(decoded):15s} | Накоплено: {repr(full_string)}")
    except Exception as e:
        print(f"{source}: {block:8s} -> Ошибка: {e}")

print(f"\n\nИТОГОВАЯ СТРОКА: {repr(full_string)}")

По итогу скрипт выдаёт вот такой результат: //kps:httubstu.69s-1ru/s-1ps:tu.ru///kubshttps:httubs//kru/tu.69s-1
Также можно дополнительно использовать скрипт, который попробует найти валидную ссылку в получившейся строке.
result = "//kps:httubstu.69s-1ru/s-1ps:tu.ru///kubshttps:httubs//kru/tu.69s-1"# Попробую найти URL паттерныimport re

# Ищем возможные URL# Вижу: kubs, tu, ru, http, ps (https), s-1, 69# Попробую разбить на частиparts = [
    "//k", "ps:", "htt", "ubs", "tu.", "69", "s-1", "ru/",
    "s-1", "ps:", "tu.", "ru/",
    "//", "kubs", "https:", "htt", "ubs", "//", "k", "ru/",
    "tu.", "69", "s-1"]

# Попробую сгруппировать иначе - может быть это несколько URL# kubstu.ru - это КубГТУ (Кубанский государственный технологический университет)print("Возможные URL:")
print("1. https://kubstu.ru/")
print("2. https://s-1.kubstu.ru/")
print("3. http://s-1.kubstu.ru/")
print("4. https://kubs69.ru/")

# Попробую извлечь URL из строкиurl_pattern = r'(https?://[^\s/]+)'# Но в строке всё перемешано...# Давайте попробуем другой подход - ищем повторяющиеся паттерныprint("\nАнализ строки:")
print(f"kubs встречается: {result.count('kubs')} раз")
print(f"tu встречается: {result.count('tu')} раз")
print(f"ru встречается: {result.count('ru')} раз")
print(f"http встречается: {result.count('http')} раз")
print(f"ps: встречается: {result.count('ps:')} раз")
print(f"s-1 встречается: {result.count('s-1')} раз")
print(f"69 встречается: {result.count('69')} раз")

# Попробую восстановить URLprint("\nВозможная расшифровка:")
# Если ps: = https: (ps это часть https без http)# Тогда может быть:urls = [
    "https://kubstu.ru/",
    "https://s-1.kubstu.ru/",
    "https://kubs69.ru/"]

for url in urls:
    print(f"  {url}")

Если присмотреться к строке, то можно увидеть, что здесь есть https:, //kubs, tu.ru, s-1, 69.  Собираем это воедино и получаем https://kubstu.ru/s-169.  Переходим по ссылке и видим страницу нашей замечательной кафедры Кибербезопасности и защиты информации. После делаем вывод что мы пришли куда-то не туда(
Возвращаемся на шаг с просмотром метаданных и видим, что есть ещё одни, до боли похожие, блоки следующего формата: iso=200|Q3N2, wb=135|b20v.
 Снова идём по метаданным, собираем все блоки в кучу и начинаем с ними играться в поисках рабочей ссылки
import base64
import itertools

# Блоки из файлов
blocks_267 = ['b20v', 'ZWJp', 'Q3N2', 'Ly9w', 'aHR0']
blocks_678 = ['cHM6', 'YXN0', 'U3VC', 'bi5j', 'cEs=']

print("=== Декодирование каждого блока отдельно ===\n")

print("Из 267.jpg:")
decoded_267 = []
for block in blocks_267:
    try:
        # Добавляем padding если нужно        padded = block + '=' * (4 - len(block) % 4) if len(block) % 4 else block
        decoded = base64.b64decode(padded).decode('utf-8', errors='replace')
        decoded_267.append(decoded)
        print(f"  {block:8s} -> {repr(decoded)}")
    except Exception as e:
        print(f"  {block:8s} -> Ошибка: {e}")

print("\nИз 678.jpg:")
decoded_678 = []
for block in blocks_678:
    try:
        padded = block + '=' * (4 - len(block) % 4) if len(block) % 4 else block
        decoded = base64.b64decode(padded).decode('utf-8', errors='replace')
        decoded_678.append(decoded)
        print(f"  {block:8s} -> {repr(decoded)}")
    except Exception as e:
        print(f"  {block:8s} -> Ошибка: {e}")

print("\n=== Пробуем разные комбинации ===\n")

# Все блоки вместеall_blocks = blocks_267 + blocks_678
all_decoded = decoded_267 + decoded_678

# 1. Простая конкатенация decoded версийprint("1. Простая конкатенация декодированных блоков:")
candidate = ''.join(all_decoded)
print(f"   {repr(candidate)}")

# 2. Конкатенация base64 блоков потом декодированиеprint("\n2. Конкатенация base64 блоков потом декодирование:")
combined_b64 = ''.join(all_blocks)
try:
    padded = combined_b64 + '=' * (4 - len(combined_b64) % 4) if len(combined_b64) % 4 else combined_b64
    decoded = base64.b64decode(padded).decode('utf-8', errors='replace')
    print(f"   {repr(decoded)}")
except Exception as e:
    print(f"   Ошибка: {e}")

# 3. Чередование блоков (267, 678, 267, 678...)print("\n3. Чередование блоков (267, 678, 267, 678...):")
interleaved = []
for i in range(max(len(blocks_267), len(blocks_678))):
    if i < len(blocks_267):
        interleaved.append(blocks_267[i])
    if i < len(blocks_678):
        interleaved.append(blocks_678[i])

combined_interleaved = ''.join(interleaved)
try:
    padded = combined_interleaved + '=' * (4 - len(combined_interleaved) % 4) if len(combined_interleaved) % 4 else combined_interleaved
    decoded = base64.b64decode(padded).decode('utf-8', errors='replace')
    print(f"   {repr(decoded)}")
except Exception as e:
    print(f"   Ошибка: {e}")

# 4. Сначала все из 267, потом все из 678 (уже было в пункте 2)# 5. Реверс порядкаprint("\n4. Реверс порядка блоков:")
reversed_blocks = all_blocks[::-1]
combined_reversed = ''.join(reversed_blocks)
try:
    padded = combined_reversed + '=' * (4 - len(combined_reversed) % 4) if len(combined_reversed) % 4 else combined_reversed
    decoded = base64.b64decode(padded).decode('utf-8', errors='replace')
    print(f"   {repr(decoded)}")
except Exception as e:
    print(f"   Ошибка: {e}")

# 6. Показываем что получилось из каждого блока для анализаprint("\n=== Анализ для ручной сборки ===")
print("\nДекодированные части:")
for i, (b267, d267, b678, d678) in enumerate(zip(blocks_267, decoded_267, blocks_678, decoded_678)):
    print(f"  {i+1}. 267: {b267} -> {repr(d267):15s} | 678: {b678} -> {repr(d678)}")
Скрипт выдаёт следующее:
=== Декодирование каждого блока отдельно ===
Из 267.jpg: b20v     -> 'om/' ZWJp     -> 'ebi' Q3N2     -> 'Csv' Ly9w     -> '//p' aHR0     -> 'htt'
Из 678.jpg: cHM6     -> 'ps:' YXN0     -> 'ast' U3VC     -> 'SuB' bi5j     -> 'n.c' cEs=     -> 'pK'
=== Пробуем разные комбинации ===
Простая конкатенация декодированных блоков: 'om/ebiCsv//phttps:astSuBn.cpK'
Конкатенация base64 блоков потом декодирование: 'om/ebiCsv//phttps:astSuBn.cpK'
Чередование блоков (267, 678, 267, 678...): 'om/ps:ebiastCsvSuB//pn.chttpK'
Реверс порядка блоков: 'pK'
=== Анализ для ручной сборки ===
Декодированные части:
267: b20v -> 'om/'           | 678: cHM6 -> 'ps:'
267: ZWJp -> 'ebi'           | 678: YXN0 -> 'ast'
267: Q3N2 -> 'Csv'           | 678: U3VC -> 'SuB'
267: Ly9w -> '//p'           | 678: bi5j -> 'n.c'
267: aHR0 -> 'htt'           | 678: cEs= -> 'pK'
Из этого делаем вывод, что здесь есть https://, домен начинается на p и скорее всего заканчивается на n.com/ => можно предположить что это будет ссылка на pastebin.com.

Исходя из этого, далее ищем точный адрес пасты:
import base64
import re
import requests
from itertools import permutations

# Исходные base64 блоки
blocks_267 = ['b20v', 'ZWJp', 'Q3N2', 'Ly9w', 'aHR0']
blocks_678 = ['cHM6', 'YXN0', 'U3VC', 'bi5j', 'cEs=']

![267.jpg](./images/img_1.jpg)

def decode_block(b64):
    """Декодирует base64 блок с авто-паддингом"""
    try:
        padded = b64 + '=' * (4 - len(b64) % 4) if len(b64) % 4 else b64
        return base64.b64decode(padded).decode('utf-8', errors='replace')
    except:
        return ''

![267.jpg](./images/img_2.jpg)

# Декодируем все блоки
decoded_267 = [decode_block(b) for b in blocks_267]
decoded_678 = [decode_block(b) for b in blocks_678]

print("🔓 Декодированные фрагменты:")
print(f"267.jpg: {decoded_267}")
print(f"678.jpg: {decoded_678}")
print()

# Целевой домен для поиска
TARGET = "pastebin.com"

![678.jpg](./images/img_3.jpg)

def score_candidate(s, target):
    """Оценивает, насколько строка похожа на ссылку с target доменом"""
    score = 0
    s_lower = s.lower()

    # Проверка на https://
    if 'https://' in s_lower or 'http://' in s_lower:
        score += 10
    if '://' in s_lower:
        score += 5

    # Проверка на наличие целевого домена
    if target in s_lower:
        score += 50
    # Частичное совпадение домена
    elif all(part in s_lower for part in target.split('.')):
        score += 20

    # Проверка на валидную структуру URL
    if re.match(r'^https?://[a-z0-9.-]+', s_lower):
        score += 15

    return score

![678.jpg](./images/img_4.jpg)

def try_fix_url(candidate, target):
    """Пытается исправить очевидные ошибки в URL"""
    fixes = []

    # Исправляем частые ошибки декодирования
    candidate = candidate.replace('httpK', 'https')
    candidate = candidate.replace('httpS', 'https')
    candidate = candidate.replace('Kttp', 'http')
    candidate = candidate.replace('Ps:', 'ps:')

    # Если есть target, но нет схемы — добавляем
    if target in candidate and '://' not in candidate:
        fixes.append('https://' + candidate)

    # Если схема есть, но домен "сломан" — пробуем вставить точки
    if '://' in candidate and target not in candidate:
        # Пробуем найти части домена и соединить их
        parts = re.findall(r'[a-z]+', candidate.lower())
        for i in range(len(parts)):
            for j in range(i + 1, len(parts) + 1):
                maybe_domain = '.'.join(parts[i:j])
                if target in maybe_domain or maybe_domain in target:
                    fixes.append(candidate.replace(''.join(parts[i:j]), target))

    fixes.append(candidate)  # оригинал тоже пробуем
    return list(set(fixes))

![267.jpg](./images/img_5.jpg)

def is_valid_pastebin_url(url):
    """Проверяет, выглядит ли ссылка как валидная pastebin-ссылка"""
    if not url.startswith(('http://', 'https://')):
        return False
    if TARGET not in url:
        return False
    # Pastebin raw links: pastebin.com/raw/XXXXX или pastebin.com/XXXXX
    pattern = rf'https?://(www\.)?{re.escape(TARGET)}/(raw/)?[A-Za-z0-9]+'
    return bool(re.match(pattern, url))


def download_paste(url):
    """Скачивает содержимое pastebin-страницы"""
    # Конвертируем обычную ссылку в raw, если нужно
    if '/raw/' not in url and TARGET in url:
        raw_url = url.replace(f'://{TARGET}/', f'://{TARGET}/raw/')
    else:
        raw_url = url

    try:
        print(f"⬇️  Скачиваю: {raw_url}")
        response = requests.get(raw_url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"❌ Ошибка загрузки: {e}")
        return None


print("🔍 Поиск рабочей ссылки pastebin.com...\n")

all_decoded = decoded_267 + decoded_678
all_blocks = blocks_267 + blocks_678

best_url = None
best_score = -1

# Стратегия 1: Перебор перестановок декодированных фрагментов
print("1. Перебор перестановок декодированных фрагментов...")
for perm in permutations(all_decoded):
    candidate = ''.join(perm)

    # Пробуем исправить очевидные ошибки
    for fixed in try_fix_url(candidate, TARGET):
        if is_valid_pastebin_url(fixed):
            score = score_candidate(fixed, TARGET)
            if score > best_score:
                best_score = score
                best_url = fixed
                print(f"   ✅ Найдено: {fixed} (score: {score})")

# Стратегия 2: Перебор перестановок base64 блоков -> декодирование
print("\n2. Перебор перестановок base64 блоков с последующим декодированием...")
for perm in permutations(all_blocks):
    combined = ''.join(perm)
    decoded = decode_block(combined)

    for fixed in try_fix_url(decoded, TARGET):
        if is_valid_pastebin_url(fixed):
            score = score_candidate(fixed, TARGET)
            if score > best_score:
                best_score = score
                best_url = fixed
                print(f"   ✅ Найдено: {fixed} (score: {score})")

# Стратегия 3: Чередование блоков (267, 678, 267...)
print("\n3. Проверка чередования блоков...")
interleaved = []
for i in range(max(len(blocks_267), len(blocks_678))):
    if i < len(blocks_267): interleaved.append(blocks_267[i])
    if i < len(blocks_678): interleaved.append(blocks_678[i])

candidate = decode_block(''.join(interleaved))
for fixed in try_fix_url(candidate, TARGET):
    if is_valid_pastebin_url(fixed):
        print(f"   ✅ Найдено: {fixed}")
        if best_score < 50:  # чередование имеет высокий приоритет
            best_url = fixed
            best_score = 50

# Стратегия 4: Ручная реконструкция на основе известных фрагментов
print("\n4. Ручная реконструкция по известным паттернам...")
# Известные фрагменты для pastebin.com:
# htt + ps: + // + p + ast + ebi + n + .c + om + /
manual_parts = {
    'https': ['htt', 'ps:'],  # htt + ps: -> https:
    '://': ['//'],  # //p -> // + p
    'pastebin': ['p', 'ast', 'ebi', 'n'],  # из //p, ast, ebi, n.c
    '.com': ['.c', 'om'],  # из n.c, om/
    '/': ['/']
}

# Собираем https://pastebin.com/
manual_url = "https://pastebin.com/"
if is_valid_pastebin_url(manual_url):
    print(f"   ✅ Реконструировано: {manual_url}")
    best_url = manual_url
    best_score = 100

print(f"\n🎯 Лучшая ссылка: {best_url}")

# Скачиваем содержимое, если ссылка найдена
if best_url and best_score > 30:
    print(f"\n📥 Попытка скачать содержимое...")
    content = download_paste(best_url)

    if content:
        print("\n" + "=" * 60)
        print("📋 СОДЕРЖИМОЕ PASTEBIN:")
        print("=" * 60)
        print(content)
        print("=" * 60)

        # Сохраняем в файл
        with open('pastebin_content.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        print("💾 Сохранено в pastebin_content.txt")
    else:
        print("\n⚠️ Не удалось скачать содержимое. Возможно:")
        print("   • Ссылка требует капчу")
        print("   • Paste удалён или приватный")
        print("   • Нужен User-Agent или cookie")
else:
    print("\n❌ Не удалось найти валидную ссылку pastebin.com")
    print("\n💡 Попробуйте вручную проверить комбинации:")
    print(f"   Фрагменты: {all_decoded}")

Спустя пару минут работы скрипта мы получаем искомую ссылку https://pastebin.com/raw/SuBCsvpK и флаг - KubSTU{g0d_s4v3_7h3_kr45n0d4r_7r4m}
Таска решена)
