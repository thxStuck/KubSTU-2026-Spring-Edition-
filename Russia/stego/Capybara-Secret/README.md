# [stego] Capybara Secret

> **Категория:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

---

Информация о задании
Категория: Стеганография
Сложность: Medium

## 🚩 Флаг

```
KubSTU{W0W_1ncred1ble_capyba6a}
```

## Шаг 1: Анализ изображения

Получив файл challenge.jpg, первым делом проверяем его на наличие скрытой информации. В стеганографии существует несколько популярных методов:
LSB (Least Significant Bit) — скрытие данных в младших битах пикселей
Метаданные (EXIF) — скрытие в служебной информации файла
Конкатенация файлов — добавление данных в конец файла
И другие...
Начнём с простого — проверим метаданные.

## Шаг 2: Извлечение EXIF-метаданных

Способ 1: ExifTool (рекомендуется)
exiftool challenge.jpg
Вывод покажет множество полей. Обращаем внимание на поле XP Comment:
XP Comment                      : XhoFGH{J0J_1aperq1oyr_pnclon6n}
Способ 2: Python + Pillow
from PIL import Image
from PIL.ExifTags import TAGS

img = Image.open('challenge.jpg')
exif_data = img._getexif()

for tag_id, value in exif_data.items():
    tag = TAGS.get(tag_id, tag_id)
    print(f"{tag}: {value}")
Способ 3: Онлайн-сервисы
Можно использовать онлайн EXIF viewer:
https://exifinfo.org/
https://www.metadata2go.com/

## Шаг 3: Анализ найденной строки

Найденная строка: XhoFGH{J0J_1aperq1oyr_pnclon6n}
Эта строка:
Похожа на формат флага (структура XXXXX{...})
Содержит нечитаемый текст
Вероятно, зашифрована простым шифром
Формат флага KubSTU{...}, а мы видим XhoFGH{...}.
Проверим гипотезу о шифре ROT13:
K → X (смещение на 13)
u → h (смещение на 13)
b → o (смещение на 13)
...
Паттерн совпадает — это ROT13!

## Шаг 4: Дешифровка ROT13

Способ 1: Онлайн декодер
Используйте любой ROT13 декодер: https://rot13.com/
Способ 2: Python
import codecs

encrypted = "XhoFGH{J0J_1aperq1oyr_pnclon6n}"
decrypted = codecs.decode(encrypted, 'rot_13')
print(decrypted)
Способ 3: Linux/Bash
echo "XhoFGH{J0J_1aperq1oyr_pnclon6n}" | tr 'A-Za-z' 'N-ZA-Mn-za-m'
Способ 4: CyberChef
Используйте CyberChef с рецептом "ROT13": https://gchq.github.io/CyberChef/#recipe=ROT13(true,true,false,13)

## Решение

После применения ROT13 получаем флаг:
```
KubSTU{W0W_1ncred1ble_capyba6a}
```
Что нужно было знать для решения
EXIF метаданные — изображения JPEG содержат метаданные, включая нестандартные поля вроде XPComment, XPKeywords (специфичные для Windows)
Инструменты для работы с EXIF — exiftool, Python библиотеки, онлайн-сервисы
Шифр ROT13 — простой шифр замены, где каждая буква заменяется на букву, отстоящую на 13 позиций в алфавите. ROT13 является собственной инверсией (применение дважды возвращает исходный текст)
Внимательность — не всё, что выглядит как мусор, является мусором. Зашифрованные данные могут выглядеть нечитаемо, но иметь определённую структуру
Альтернативный автоматизированный решатель
import struct
import codecs

def extract_xp_comment(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()

    pos = 2
    while pos < len(data) - 1:
        if data[pos] != 0xff:
            pos += 1
            continue
        marker = data[pos + 1]
        if marker == 0xe1:
            length = struct.unpack('>H', data[pos+2:pos+4])[0]
            segment = data[pos+4:pos+2+length]
            if segment[:6] == b'Exif\x00\x00':
                tiff = segment[6:]
                endian = '<' if tiff[:2] == b'II' else '>'
                ifd_off = struct.unpack(endian + 'I', tiff[4:8])[0]
                n = struct.unpack(endian + 'H', tiff[ifd_off:ifd_off+2])[0]
                for i in range(n):
                    e = ifd_off + 2 + i * 12
                    tag = struct.unpack(endian + 'H', tiff[e:e+2])[0]
                    if tag == 0x9C9C:
                        cnt = struct.unpack(endian + 'I', tiff[e+4:e+8])[0]
                        off = struct.unpack(endian + 'I', tiff[e+8:e+12])[0]
                        return tiff[off:off+cnt].decode('utf-16le').rstrip('\x00')
            pos += 2 + length
        elif 0xe0 <= marker <= 0xef or marker == 0xfe:
            pos += 2 + struct.unpack('>H', data[pos+2:pos+4])[0]
        else:
            break
    return None

encrypted = extract_xp_comment('challenge.jpg')
print(f"Encrypted: {encrypted}")
print(f"Flag: {codecs.decode(encrypted, 'rot_13')}")
```
KubSTU{W0W_1ncred1ble_capyba6a}
```
