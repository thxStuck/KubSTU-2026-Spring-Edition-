# [stego] Capybara in Nightmare Land

> **Категория:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

---

**Категория:** Steganography
**Автор:** KubSTU CTF Team
**Формат флага:** `KubSTU{...}`
📝 Описание задания
Капибара из КубГТУ заснула на лекции по информационной безопасности и попала в странный кошмарный сон...
В этом сне она оставила секретное послание. Сможешь ли ты найти его?
Подсказка: Не всё то, чем кажется. Загляни глубже. 🔍
 Файлы
Файл
Описание
capybara_nightmare.png
Изображение для анализа
🎯 Цель
Найти скрытый флаг внутри изображения.

## Решение

## Шаг 1: Анализ файла

Первым делом проанализируем файл с помощью стандартных инструментов:
file capybara_nightmare.png
# Output: PNG image data, 1024 x 1024, 8-bit/color RGB

binwalk capybara_nightmare.png
# Output покажет, что внутри есть ZIP архив!
Инструмент binwalk обнаруживает ZIP-архив внутри PNG файла. Это признак polyglot-файла — файла, который является одновременно валидным PNG и ZIP.

## Шаг 2: Извлечение ZIP архива

PNG+ZIP polyglot работает потому, что:
PNG читается от начала файла до IEND chunk
ZIP читается от конца файла (ищет End of Central Directory)
Извлекаем архив:
# Способ 1: просто разархивировать
unzip capybara_nightmare.png -d extracted/

# Способ 2: через binwalk
binwalk -e capybara_nightmare.png
Внутри архива находим:
README.txt — подсказка
encrypted_flag.bin — зашифрованный флаг

## Шаг 3: Анализ README.txt

╔══════════════════════════════════════════════════════════════╗
║           🦫 CAPYBARA'S ENCRYPTED SECRET 🦫                  ║
╠══════════════════════════════════════════════════════════════╣
║  The flag is XOR encrypted.                                  ║
║  The key is hidden in the original image...                  ║
║  Look closer at the pixels! 🔍                               ║
║                                                              ║
║  Hint: LSB (Least Significant Bit)                           ║
║  Password length: 19 characters                              ║
╚══════════════════════════════════════════════════════════════╝
Подсказки говорят нам:
Флаг зашифрован XOR
Ключ спрятан в изображении
Используется LSB стеганография
Длина пароля: 19 символов

## Шаг 4: Извлечение LSB

LSB (Least Significant Bit) — техника стеганографии, где данные прячутся в младших битах пикселей изображения. Изменение младшего бита практически незаметно для глаза.
Напишем скрипт для извлечения:
from PIL import Image
import numpy as np

def extract_lsb(image_path):
    img = Image.open(image_path).convert('RGB')
    pixels = np.array(img).flatten()

    bits = ''
    chars = []

    for pixel in pixels:
        bits += str(pixel & 1)  # Извлекаем младший бит

        if len(bits) == 8:
            char = chr(int(bits, 2))
            chars.append(char)
            bits = ''

            # Ищем маркер конца
            text = ''.join(chars)
            if 'END_LSB' in text:
                return text.split('\x00')[0]

    return ''.join(chars[:100])

password = extract_lsb("capybara_nightmare.png")
print(f"Password: {password}")
# Output: N1ghtm4r3_C4py_2026
Извлечённый пароль: N1ghtm4r3_C4py_2026

## Шаг 5: Расшифровка флага

Теперь используем найденный пароль для XOR-расшифровки:
def xor_decrypt(encrypted: bytes, key: str) -> str:
    key_bytes = key.encode('utf-8')
    result = []
    for i, byte in enumerate(encrypted):
        result.append(chr(byte ^ key_bytes[i % len(key_bytes)]))
    return ''.join(result)

# Читаем зашифрованный флаг
with open("encrypted_flag.bin", "rb") as f:
    encrypted = f.read()

password = "N1ghtm4r3_C4py_2026"
flag = xor_decrypt(encrypted, password)
print(f"Flag: {flag}")

## 🚩 Флаг

```
KubSTU{H0ly_M0ly_CapyHaCk1r}
```
Используемые инструменты
Инструмент
Назначение
file
Определение типа файла
binwalk
Анализ и извлечение встроенных данных
unzip
Распаковка ZIP архива
Python + PIL
Извлечение LSB
Python
XOR расшифровка
Альтернативные инструменты
zsteg — автоматическое обнаружение LSB стеганографии
stegsolve — визуальный анализ LSB слоёв
010 Editor — hex-редактор для анализа polyglot
Краткий алгоритм решения
┌─────────────────────────────────────┐
│  capybara_nightmare.png             │
│  (PNG + ZIP polyglot)               │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌────────────┐      ┌────────────────┐
│  Как PNG   │      │    Как ZIP     │
│  (LSB)     │      │                │
└─────┬──────┘      └───────┬────────┘
      │                     │
      ▼                     ▼
┌────────────┐      ┌────────────────┐
│  Password: │      │ encrypted_flag │
│  N1ghtm4r3 │      │     .bin       │
│  _C4py_    │      └───────┬────────┘
│  2026      │              │
└─────┬──────┘              │
      │                     │
      └─────────┬───────────┘
                │
                ▼
        ┌──────────────┐
        │  XOR Decrypt │
        └──────┬───────┘
               │
               ▼
    ┌─────────────────────────┐
    │ KubSTU{H0ly_M0ly_       │
    │        CapyHaCk1r}      │
    └─────────────────────────┘
Защита от автоматических решателей
Данный таск использует несколько уровней защиты:
Polyglot-файл — не все инструменты автоматически обнаруживают
Кастомный маркер LSB — END_LSB вместо стандартных маркеров
XOR шифрование — требует найти ключ, простой brute-force невозможен без знания длины и формата ключа
Автор
Создано для CTF-соревнований КубГТУ.
