import sys
import re

def remove_separators(input_file, output_file="cleaned_output.txt"):
    """
    Удаляет все символы-разделители из файла и сохраняет результат
    """
    # Символы-разделители (без скобок)
    separators = '*?&№#"@!=+^\\/|,.<>'

    # Экранируем специальные символы для регулярного выражения
    escaped_separators = re.escape(separators)

    # Регулярное выражение для удаления ВСЕХ разделителей
    pattern = re.compile(f'[{escaped_separators}]')

    print(f"Удаление разделителей из файла {input_file}...")
    print(f"Разделители: {separators}")

    try:
        # Открываем файлы
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:

            total_processed = 0
            chunk_size = 100 * 1024 * 1024  # 100 МБ за раз

            while True:
                # Читаем кусок файла
                chunk = infile.read(chunk_size)
                if not chunk:
                    break

                total_processed += len(chunk)

                # Удаляем все разделители
                cleaned_chunk = pattern.sub('', chunk)

                # Записываем очищенный кусок
                outfile.write(cleaned_chunk)

                # Показываем прогресс
                mb_processed = total_processed / (1024 * 1024)
                print(f"Обработано: {mb_processed:.1f} МБ", end="\r")

        print(f"\n\nГотово! Результат сохранён в {output_file}")
        print(f"Обработано: {total_processed:,} байт")

        # Показываем размер результата
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"Результат: {len(content)} символов")

        return output_file

    except FileNotFoundError:
        print(f"Ошибка: файл '{input_file}' не найден!")
        print("Проверьте правильность пути к файлу.")
        return None
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None

def show_result(filename, num_chars=200):
    """
    Показывает начало и конец очищенного файла
    """
    if not filename:
        return

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"\nСодержимое файла '{filename}':")
        print(f"Всего символов: {len(content)}")

        if len(content) > 0:
            print(f"\nПервые {min(num_chars, len(content))} символов:")
            print("-" * 50)
            print(content[:num_chars])

            print(f"\nПоследние {min(num_chars, len(content))} символов:")
            print("-" * 50)
            print(content[-num_chars:])
        else:
            print("Файл пустой!")

    except Exception as e:
        print(f"Ошибка при чтении результата: {e}")

def main():
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        input_filename = sys.argv[1]
    else:
        # По умолчанию используем этот файл
        input_filename = "Weird_Furry_text.txt"

    # Проверяем существование файла
    import os
    if not os.path.exists(input_filename):
        print(f"Файл '{input_filename}' не найден.")
        print("Укажите правильное имя файла или поместите файл в текущую папку.")
        return

    print("=" * 60)
    print("СИМПЛЫЙ УДАЛИТЕЛЬ РАЗДЕЛИТЕЛЕЙ")
    print("=" * 60)

    # Удаляем разделители
    output_filename = remove_separators(input_filename, "result.txt")

    if output_filename:
        # Показываем результат
        show_result(output_filename, 150)

if __name__ == "__main__":
    main()