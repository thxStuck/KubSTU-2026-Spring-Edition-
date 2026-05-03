#!/usr/bin/env python3


import base64

def decode_ascii85_from_pdf():
    print("=" * 70)
    print("СКРИПТ 1: ДЕКОДИРОВАНИЕ ASCII85 ИЗ PDF")
    print("=" * 70)
    
    # Читаем PDF файл
    pdf_file = "crypto_history_challenge.pdf"
    print(f"\n1. Читаем файл: {pdf_file}")
    
    with open(pdf_file, "rb") as f:
        data = f.read()
    
    # Находим объект 5
    print("\n2. Ищем объект 5...")
    obj5_start = data.find(b'5 0 obj')
    if obj5_start == -1:
        print("  Объект 5 не найден!")
        return
    
    print(f"   Объект 5 найден на позиции: {obj5_start}")
    
    # Находим stream внутри объекта 5
    print("\n3. Ищем stream в объекте 5...")
    stream_start = data.find(b'stream', obj5_start) + 6
    stream_end = data.find(b'endstream', stream_start)
    
    if stream_start == -1 or stream_end == -1:
        print("   Stream не найден!")
        return
    
    print(f"   Stream найден")
    print(f"   Начало stream: {stream_start}")
    print(f"   Конец stream: {stream_end}")
    
    # Извлекаем данные
    stream_data = data[stream_start:stream_end].strip()
    print(f"\n4. Извлечены данные из stream:")
    print(f"   Длина: {len(stream_data)} байт")
    print(f"   Начало: {stream_data[:100]}")
    print(f"   Конец: {stream_data[-100:]}")
    
    # Находим маркер ~>
    print("\n5. Ищем маркер конца ASCII85 (~>)...")
    real_end = stream_data.find(b'~>')
    if real_end == -1:
        print("   Маркер ~> не найден!")
        return
    
    print(f"   Маркер ~> найден на позиции: {real_end}")
    
    # Очищаем данные от пробелов
    print("\n6. Очищаем данные от пробелов...")
    clean_data = b"".join(stream_data[:real_end+2].split())
    print(f"   Длина очищенных данных: {len(clean_data)} байт")
    print(f"   Начало: {clean_data[:100]}")
    print(f"   Конец: {clean_data[-100:]}")
    
    # Декодируем ASCII85
    print("\n7. Декодируем ASCII85...")
    try:
        decoded = base64.a85decode(clean_data, adobe=True)
        print(f"   Декодирование успешно!")
        print(f"   Длина после декодирования: {len(decoded)} байт")
        print(f"   Первые 50 байт: {decoded[:50]}")
        print(f"   Последние 50 байт: {decoded[-50:]}")
        
        # Проверяем сигнатуру
        if decoded[:2] == b'x\x9c':
            print(f"\nОбнаружена сигнатура zlib: {decoded[:2]}")
            print("   Это сжатые данные, которые нужно распаковать во втором скрипте")
        else:
            print(f"\n   Сигнатура: {decoded[:2]} (не zlib)")
        
        # Сохраняем в файл
        output_file = "decoded_ascii85.bin"
        print(f"\n8. Сохраняем декодированные данные в файл: {output_file}")
        with open(output_file, "wb") as f:
            f.write(decoded)
        
        print(f"   Файл сохранен: {output_file}")
        print(f"   Размер файла: {len(decoded)} байт")
        
        # Показываем информацию о файле
        print("\n" + "=" * 70)
        print("ИНФОРМАЦИЯ О СОХРАНЕННОМ ФАЙЛЕ:")
        print("=" * 70)
        print(f"Имя файла: {output_file}")
        print(f"Размер: {len(decoded)} байт")
        print(f"Тип: Сжатые данные (zlib)")
        print(f"Сигнатура: {decoded[:2]}")
        print("\nСледующий шаг: запустить скрипт 2 для распаковки zlib")
        
    except Exception as e:
        print(f"   Ошибка декодирования: {e}")
        return

if __name__ == "__main__":
    decode_ascii85_from_pdf()
