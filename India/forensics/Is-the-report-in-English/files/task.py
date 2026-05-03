#!/usr/bin/env python3
import base64
import re
import sys
import subprocess
import string

def extract_strings_from_pdf(pdf_file):
    """Извлекает все строки из PDF файла"""
    print(f"[*] Extracting strings from {pdf_file}...")
    try:
        result = subprocess.run(['strings', pdf_file], 
                              capture_output=True, text=True, timeout=30)
        return result.stdout.split('\n')
    except Exception as e:
        print(f"[!] Error extracting strings: {e}")
        # Альтернативный метод если strings недоступен
        try:
            with open(pdf_file, 'rb') as f:
                data = f.read()
            # Простая эмуляция strings - ищем печатные символы
            text = ''.join(chr(b) if 32 <= b < 127 else '\n' for b in data)
            return [line.strip() for line in text.split('\n') if line.strip()]
        except:
            return []

def is_likely_base64(text):
    """Проверяет, похожа ли строка на base64"""
    if not text:
        return False
    
    # Base64 состоит из A-Z, a-z, 0-9, +, /, =
    allowed_chars = set(string.ascii_letters + string.digits + '+/=' + ' \t\n\r')
    
    # Проверяем что все символы разрешены
    for char in text:
        if char not in allowed_chars:
            return False
    
    # Длина должна быть хотя бы 20 символов для base64
    if len(text.strip()) < 20:
        return False
    
    # Base64 часто заканчивается на = или ==
    stripped = text.strip()
    if stripped.endswith('=') or stripped.endswith('=='):
        return True
    
    # Проверяем примерное распределение символов
    # Base64 содержит много букв и цифр
    letter_digit_count = sum(1 for c in stripped if c.isalnum())
    if letter_digit_count / len(stripped) > 0.7:  # Более 70% букв/цифр
        return True
    
    return False

def extract_base64_candidates(line):
    """Извлекает возможные base64 строки из строки"""
    candidates = []
    
    # Убираем начальные/конечные пробелы
    line = line.strip()
    
    # Паттерн 1: ключ=base64 (самый вероятный)
    if '=' in line:
        parts = line.split('=', 1)
        if len(parts) == 2:
            key, value = parts
            if is_likely_base64(value):
                candidates.append(('key=value', key, value))
    
    # Паттерн 2: ключ:base64
    if ':' in line and '=' not in line:
        parts = line.split(':', 1)
        if len(parts) == 2:
            key, value = parts
            if is_likely_base64(value):
                candidates.append(('key:value', key, value))
    
    # Паттерн 3: просто длинная base64-подобная строка
    if is_likely_base64(line) and len(line) > 40:
        candidates.append(('raw', '', line))
    
    # Паттерн 4: base64 в кавычках или скобках
    patterns = [
        r'"([A-Za-z0-9+/=\s]{20,})"',
        r"'([A-Za-z0-9+/=\s]{20,})'",
        r'<[^>]+>([A-Za-z0-9+/=\s]{20,})</[^>]+>',
        r'{([A-Za-z0-9+/=\s]{20,})}'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, line)
        for match in matches:
            if is_likely_base64(match):
                candidates.append(('quoted', '', match))
    
    return candidates

def decode_and_analyze(base64_str):
    """Декодирует base64 и анализирует результат"""
    try:
        decoded_bytes = base64.b64decode(base64_str, validate=True)
        
        # Пробуем разные кодировки
        encodings = ['utf-8', 'latin-1', 'cp1251', 'ascii']
        decoded_text = None
        
        for encoding in encodings:
            try:
                decoded_text = decoded_bytes.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if decoded_text is None:
            # Если не декодируется как текст, может быть бинарными данными
            return {
                'success': True,
                'is_text': False,
                'length': len(decoded_bytes),
                'hex_preview': decoded_bytes[:20].hex()[:40] + '...' if len(decoded_bytes) > 20 else decoded_bytes.hex(),
                'text': None
            }
        
        # Анализируем декодированный текст
        is_printable = all(32 <= ord(c) < 127 for c in decoded_text)
        
        return {
            'success': True,
            'is_text': True,
            'is_printable': is_printable,
            'length': len(decoded_text),
            'text': decoded_text,
            'first_chars': decoded_text[:100] + '...' if len(decoded_text) > 100 else decoded_text
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def analyze_strings(strings_list):
    """Анализирует все строки на наличие base64"""
    print("[*] Analyzing strings for base64 patterns...")
    
    suspicious_strings = []
    base64_candidates_count = 0
    
    for line_num, line in enumerate(strings_list, 1):
        if not line.strip():
            continue
        
        # Извлекаем кандидатов на base64
        candidates = extract_base64_candidates(line)
        
        for candidate_type, key, value in candidates:
            base64_candidates_count += 1
            
            # Анализируем base64
            analysis = decode_and_analyze(value)
            
            if analysis['success']:
                if analysis['is_text'] and analysis['is_printable']:
                    decoded = analysis['text']
                    
                    # Ищем интересные паттерны в декодированном тексте
                    interesting_patterns = []
                    
                    # CTF флаги обычно в формате {FLAG_PREFIX{...}}
                    flag_patterns = [
                        r'\{[A-Za-z0-9_]{4,}\{[^\}]+\}\}',  # {SOMETHING{...}}
                        r'[A-Za-z0-9_]{4,}\{[^\}]+\}',     # SOMETHING{...}
                        r'flag[^:]*:[^:]+',                # flag: ...
                        r'FLAG[^:]*:[^:]+',                # FLAG: ...
                    ]
                    
                    for pattern in flag_patterns:
                        if re.search(pattern, decoded, re.IGNORECASE):
                            interesting_patterns.append("FLAG_FORMAT")
                    
                    # Ищем что-то похожее на текст
                    if len(decoded) > 10 and any(c.isalpha() for c in decoded):
                        word_like = sum(1 for c in decoded if c.isalpha() or c.isspace()) / len(decoded) > 0.5
                        if word_like:
                            interesting_patterns.append("TEXT_LIKE")
                    
                    # Если есть интересные паттерны, сохраняем для анализа
                    if interesting_patterns:
                        suspicious_strings.append({
                            'line_num': line_num,
                            'line': line[:100] + '...' if len(line) > 100 else line,
                            'candidate_type': candidate_type,
                            'key': key,
                            'base64_preview': value[:50] + '...' if len(value) > 50 else value,
                            'decoded_preview': decoded[:100] + '...' if len(decoded) > 100 else decoded,
                            'patterns': interesting_patterns,
                            'full_decoded': decoded
                        })
    
    print(f"[*] Found {base64_candidates_count} base64 candidates")
    print(f"[*] Found {len(suspicious_strings)} suspicious strings")
    
    return suspicious_strings

def manual_investigation_mode(strings_list):
    """Режим ручного расследования - показывает подозрительные строки"""
    print("\n" + "="*60)
    print("MANUAL INVESTIGATION MODE")
    print("="*60)
    
    print("\n[*] Looking for strings with '=' (key=value pattern)...")
    key_value_lines = []
    for line_num, line in enumerate(strings_list, 1):
        if '=' in line and len(line) > 40:
            key_value_lines.append((line_num, line))
    
    print(f"[*] Found {len(key_value_lines)} key=value lines")
    
    # Показываем самые интересные
    print("\n[!] Most interesting key=value lines (sorted by length):")
    key_value_lines.sort(key=lambda x: len(x[1]), reverse=True)
    
    for i, (line_num, line) in enumerate(key_value_lines[:20], 1):
        print(f"\n{i}. Line {line_num} (length: {len(line)}):")
        print(f"   {line[:120]}{'...' if len(line) > 120 else ''}")
        
        # Показываем часть после '='
        if '=' in line:
            parts = line.split('=', 1)
            value = parts[1]
            print(f"   Value after '=' (first 60 chars): {value[:60]}{'...' if len(value) > 60 else ''}")
            
            # Проверяем если похоже на base64
            if is_likely_base64(value):
                print(f"   [!] Looks like base64! Try decoding with: echo '{value[:100]}...' | base64 -d")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 forensic_analyzer.py <pdf_file>")
        print("Example: python3 forensic_analyzer.py document.pdf")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    print("="*60)
    print("PDF FORENSIC ANALYZER")
    print("="*60)
    
    # 1. Извлекаем строки
    strings_list = extract_strings_from_pdf(pdf_file)
    if not strings_list:
        print("[!] Failed to extract strings from PDF")
        sys.exit(1)
    
    print(f"[*] Extracted {len(strings_list)} strings")
    
    # 2. Автоматический анализ
    suspicious = analyze_strings(strings_list)
    
    if suspicious:
        print(f"\n[!] FOUND {len(suspicious)} SUSPICIOUS STRINGS:")
        for i, item in enumerate(suspicious, 1):
            print(f"\n{i}. Line {item['line_num']}:")
            print(f"   Original: {item['line']}")
            print(f"   Pattern: {item['candidate_type']}")
            if item['key']:
                print(f"   Key: {item['key']}")
            print(f"   Base64: {item['base64_preview']}")
            print(f"   Decoded: {item['decoded_preview']}")
            print(f"   Patterns detected: {', '.join(item['patterns'])}")
            
            # Если похоже на флаг, предлагаем проверить
            if "FLAG_FORMAT" in item['patterns']:
                print(f"   [!] POSSIBLE FLAG DETECTED!")
                print(f"   [!] Full decoded text: {item['full_decoded']}")
    else:
        print("\n[-] No automatically detected suspicious strings.")
        print("    Switching to manual investigation mode...")
        manual_investigation_mode(strings_list)
    
    print("\n" + "="*60)
    print("INVESTIGATION TIPS:")
    print("="*60)
    print("""
1. Look for strings with '=' character (key=value pattern)
2. The value after '=' might be base64 encoded
3. Common CTF flag formats:
   - FLAG{...}
   - flag{...} 
   - {SOMETHING{...}}
   - Sometimes just plain text starting with organization name

4. To decode base64 manually:
   echo "BASE64_STRING" | base64 -d

5. Check PDF metadata:
   exiftool document.pdf

6. Look for embedded files:
   binwalk -e document.pdf
   pdf-parser.py --search embedded document.pdf
""")

if __name__ == "__main__":
    main()
