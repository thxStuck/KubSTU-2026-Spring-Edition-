import base64

# Закодированная строка из задания
encoded_string = "S3ViU1RVKGI0czNfNjRfMXNfdGhlX2JhNWk1KQ=="

# Декодируем Base64
decoded_bytes = base64.b64decode(encoded_string)

# Преобразуем в строку
flag = decoded_bytes.decode('utf-8')

print(f"Флаг: {flag}")