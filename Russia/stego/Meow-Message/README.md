# [stego] Meow Message

> **Категория:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

---

Writeup: Meow Message
Категория: СтеганографияСложность: EasyФлаг: KubSTU{wh1t3_sp4c3}
Анализ задачи
Нам дан текстовый файл message.txt с ASCII-артом котика и стишком на русском языке. На первый взгляд — просто милая картинка с текстом.
    /\_____/\
   /  o   o  \
  ( ==  ^  == )
   )         (
  (           )
 ( (  )   (  ) )
(__(__)___(__)__)

  *** MEOW! ***

  Мяу-мяу, человек!
  Я не просто кот,
  Я хранитель тайн.

  В моих лапках есть
  секрет один...
  Но его не видно
  просто так.
  Присмотрись! :3
Подсказка в описании говорит: "Не всё, что кажется пустым, на самом деле пусто" — это намёк на невидимые символы.

## Шаг 1: Обнаружение скрытых данных

Открываем файл в hex-редакторе или используем команду для просмотра непечатаемых символов:
Способ 1: xxd (Linux/Mac)
xxd message.txt | head -20
Способ 2: PowerShell (Windows)
Get-Content message.txt | ForEach-Object {
    $_ -replace ' ', '·' -replace "`t", '→'
}
Способ 3: Python
with open('message.txt', 'r') as f:
    for i, line in enumerate(f):
        visible = line.rstrip('\n').replace(' ', '·').replace('\t', '→')
        print(f"{i+1}: {visible}")
Результат: Мы видим, что в конце каждой строки есть комбинации пробелов (·) и табуляций (→).

## Шаг 2: Понимание кодирования

Это классическая Whitespace-стеганография в стиле SNOW.
Каждая строка содержит 8 невидимых символов в конце
Пробел = 0, Табуляция = 1
8 бит = 1 байт = 1 символ ASCII
Пример первой строки:
         /\_/\[пробел][таб][пробел][пробел][таб][пробел][таб][таб]
Это: 01001011 = 75 в десятичной = символ K

## Шаг 3: Декодирование

Ручной способ
Для каждой строки:
Извлечь trailing whitespace (пробелы и табы после текста)
Преобразовать в бинарный: пробел→0, таб→1
Конвертировать 8 бит в ASCII символ
Автоматический способ (Python)
#!/usr/bin/env python3

def decode_snow(filename):
    flag = ""

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')

            # Находим позицию последнего непробельного символа
            text_end = len(line.rstrip())
            trailing = line[text_end:]

            if len(trailing) >= 8:
                # Берём первые 8 символов whitespace
                bits = ""
                for char in trailing[:8]:
                    if char == ' ':
                        bits += '0'
                    elif char == '\t':
                        bits += '1'

                if len(bits) == 8:
                    ascii_val = int(bits, 2)
                    flag += chr(ascii_val)

    return flag

if __name__ == "__main__":
    flag = decode_snow("../challenge/message.txt")
    print(f"Флаг: {flag}")

## Шаг 4: Получение флага

Запускаем скрипт:
python solve.py
Результат:

## 🚩 Флаг

```
KubSTU{wh1t3_sp4c3}
```
Альтернативные методы решения
1. Использование утилиты SNOW
# Установка
apt install stegsnow

# Декодирование
stegsnow -C message.txt
2. CyberChef
Загрузить файл в CyberChef
Использовать операцию "Extract trailing whitespace"
Применить "From Binary" с делимитером по 8 бит
3. Ручной анализ в Notepad++
Открыть файл
View → Show Symbol → Show All Characters
Записать паттерны пробелов/табов и декодировать вручную
Выводы
Задача демонстрирует базовую технику Whitespace-стеганографии. Ключевые навыки:
Анализ файлов на скрытые данные
Понимание бинарного кодирования
Работа с hex-редакторами и инструментами анализа
```
KubSTU{wh1t3_sp4c3}
```
