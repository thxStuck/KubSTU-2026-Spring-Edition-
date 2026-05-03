def decode_ascii_simple(ascii_codes):
    """Простой декодировщик ASCII кодов"""
    # Разбиваем строку на числа
    codes = ascii_codes.split()

    # Преобразуем каждое число в символ
    flag_chars = [chr(int(code)) for code in codes]

    # Собираем строку
    flag = ''.join(flag_chars)

    return flag


# Код из задания
ascii_sequence = "75 117 98 83 84 85 40 97 115 99 49 49 95 99 48 100 51 115 95 97 114 51 95 97 110 95 49 110 116 101 114 101 115 116 105 110 103 95 119 52 121 95 116 111 95 103 101 55 95 105 110 116 111 95 99 114 121 112 55 48 103 114 97 112 104 121 41"

# Декодируем
flag = decode_ascii_simple(ascii_sequence)
print(f"Флаг: {flag}")