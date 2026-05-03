#!/usr/bin/env python3
"""
Скрипт 2: Распаковка zlib
Читает файл, полученный после декодирования ASCII85, и распаковывает zlib
"""

import zlib
import os

def decompress_zlib():
    print("=" * 70)
    print("СКРИПТ 2: РАСПАКОВКА ZLIB")
    print("=" * 70)
    
    # Читаем файл, полученный из первого скрипта
    input_file = "decoded_ascii85.bin"
    print(f"\n1. Читаем файл: {input_file}")
    
    if not os.path.exists(input_file):
        print(f"   ❌ Файл {input_file} не найден!")
        print("   Сначала запустите скрипт 1 для декодирования ASCII85")
        return
    
    with open(input_file, "rb") as f:
        compressed_data = f.read()
    
    print(f"   ✅ Файл прочитан")
    print(f"   Размер: {len(compressed_data)} байт")
    print(f"   Первые 20 байт: {compressed_data[:20]}")
    
    # Проверяем сигнатуру
    if compressed_data[:2] == b'x\x9c':
        print(f"\n   ✅ Обнаружена сигнатура zlib: {compressed_data[:2]}")
        print("   Данные сжаты алгоритмом zlib (FlateDecode)")
    else:
        print(f"\n   ⚠️  Неожиданная сигнатура: {compressed_data[:2]}")
        print("   Возможно, данные уже распакованы или это другой формат")
    
    # Распаковываем zlib
    print("\n2. Распаковываем zlib...")
    try:
        decompressed = zlib.decompress(compressed_data)
        print(f"   ✅ Распаковка успешна!")
        print(f"   Размер после распаковки: {len(decompressed)} байт")
        print(f"   Коэффициент сжатия: {len(compressed_data)/len(decompressed)*100:.1f}%")
        
        # Сохраняем распакованные данные в файл
        output_file = "decompressed_zlib.txt"
        print(f"\n3. Сохраняем распакованные данные в файл: {output_file}")
        
        # Пробуем декодировать как текст
        try:
            text_content = decompressed.decode('latin-1', errors='ignore')
            with open(output_file, "w", encoding='latin-1') as f:
                f.write(text_content)
            print(f"   ✅ Файл сохранен как текст: {output_file}")
            print(f"   Размер файла: {len(text_content)} символов")
        except:
            # Если не получается как текст, сохраняем как бинарный
            with open(output_file.replace('.txt', '.bin'), "wb") as f:
                f.write(decompressed)
            print(f"   ✅ Файл сохранен как бинарный: {output_file.replace('.txt', '.bin')}")
        
        # Показываем содержимое
        print("\n" + "=" * 70)
        print("ПЕРВЫЕ 1500 СИМВОЛОВ РАСПАКОВАННЫХ ДАННЫХ:")
        print("=" * 70)
        
        # Декодируем для отображения
        content = decompressed.decode('latin-1', errors='ignore')
        print(content[:1500])
        
        print("\n" + "=" * 70)
        print("ПОСЛЕДНИЕ 500 СИМВОЛОВ РАСПАКОВАННЫХ ДАННЫХ:")
        print("=" * 70)
        print(content[-500:])
        
        # Показываем статистику
        print("\n" + "=" * 70)
        print("СТАТИСТИКА РАСПАКОВАННЫХ ДАННЫХ:")
        print("=" * 70)
        
        # Считаем количество команд
        import re
        pattern = r'BT 1 0 0 1 [\d\.-]+ [\d\.-]+ Tm \(.*?\) Tj'
        commands = re.findall(pattern, content)
        print(f"Всего PDF команд: {len(commands)}")
        
        # Считаем символы по Y координатам
        coord_pattern = r'BT 1 0 0 1 [\d\.-]+ ([\d\.-]+) Tm \((.*?)\) Tj'
        matches = re.findall(coord_pattern, content)
        
        y_coords = {}
        for y, char in matches:
            if y not in y_coords:
                y_coords[y] = 0
            y_coords[y] += 1
        
        print(f"\nРаспределение символов по Y координатам:")
        for y in sorted(y_coords.keys(), key=float)[:10]:
            print(f"  Y = {y}: {y_coords[y]} символов")
        
        print("\n" + "=" * 70)
        print("ГОТОВО! Теперь вы можете:")
        print("=" * 70)
        print(f"1. Открыть файл {output_file} в текстовом редакторе")
        print("2. Найти все команды с Y=100")
        print("3. Собрать символы по порядку X координат")
        print("4. Получить флаг")
        
    except zlib.error as e:
        print(f"   ❌ Ошибка распаковки: {e}")
        print("   Возможные причины:")
        print("   - Данные не являются сжатыми zlib")
        print("   - Данные повреждены")
        print("   - Неправильный формат данных")
    except Exception as e:
        print(f"   ❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    decompress_zlib()
