#!/usr/bin/env python3
"""
WAF CTF Client - автоматическое решение задания
Подключается к серверу и определяет вредоносные запросы
"""

import socket
import re
import sys
import time
import urllib.parse

class WAFClient:
    def __init__(self, host='localhost', port=1337):
        self.host = host
        self.port = port
        self.socket = None
        
    def connect(self):
        """Подключается к серверу"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(30)
            print(f"Подключено к {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False
    
    def receive_data(self, buffer_size=4096):
        """Получает данные от сервера"""
        try:
            data = self.socket.recv(buffer_size).decode('utf-8')
            return data
        except socket.timeout:
            return None  # Таймаут - это нормально
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return None
    
    def send_data(self, data):
        """Отправляет данные на сервер"""
        try:
            self.socket.send((data + '\n').encode('utf-8'))
            return True
        except Exception as e:
            print(f"Ошибка при отправке данных: {e}")
            return False
    
    def is_malicious(self, request):
        """Анализирует HTTP запрос и определяет, вредоносный ли он"""
        
        # Извлекаем путь из HTTP запроса для более точной проверки path traversal
        request_lower = request.lower()
        
        # Декодируем URL-encoded части запроса для проверки XSS и других атак
        try:
            # Пытаемся декодировать URL-encoded части
            # Сначала заменяем + на пробелы (URL-кодирование пробелов)
            request_with_spaces = request.replace('+', ' ')
            decoded_request = urllib.parse.unquote(request_with_spaces)
            decoded_request_lower = decoded_request.lower()
        except:
            decoded_request = request.replace('+', ' ')
            decoded_request_lower = decoded_request_lower if 'decoded_request_lower' in locals() else decoded_request.lower()
        
        path_part = ""
        path_part_decoded = ""
        # Пытаемся извлечь путь из первой строки HTTP запроса
        lines = request_lower.split('\n')
        if lines:
            first_line = lines[0].strip()
            parts = first_line.split()
            if len(parts) >= 2:
                path_part = parts[1]  # Путь обычно второй элемент (GET /path HTTP/1.1)
                # Декодируем путь для проверки (заменяем + на пробелы перед декодированием)
                try:
                    path_with_spaces = path_part.replace('+', ' ')
                    path_part_decoded = urllib.parse.unquote(path_with_spaces)
                except:
                    path_part_decoded = path_part.replace('+', ' ')
        
        # Паттерны SQL инъекций
        sql_patterns = [
            r"['\"]\s*(OR|AND)\s*['\"]?\d+['\"]?\s*=\s*['\"]?\d+",  # ' OR '1'='1
            r"['\"]\s*OR\s*['\"]?\d+['\"]?\s*=\s*['\"]?\d+",  # ' OR 1=1
            r"['\"]\s*OR\s*['\"]?1['\"]?\s*=\s*['\"]?1",  # ' OR '1'='1 (более общий)
            r"\d+['\"]\s*OR\s*['\"]?\d+['\"]?\s*=\s*['\"]?\d+",  # 1' OR '1'='1
            r"\d+['\"]\s*OR\s*['\"]?1['\"]?\s*=\s*['\"]?1",  # 1' OR '1'='1 (с числами)
            r"UNION\s+SELECT.*--",  # UNION SELECT с комментариями (инъекция)
            r"UNION\s+SELECT\s+NULL.*--",  # UNION SELECT NULL с комментариями
            r"DROP\s+TABLE",  # DROP TABLE
            r"';?\s*--",  # ';--
            r"\/\*.*\*\/",  # SQL комментарии
            r"'\s*OR\s*'1'\s*=\s*'1",  # ' OR '1'='1
            r"'\s*OR\s*1\s*=\s*1",  # ' OR 1=1
            r"SLEEP\s*\(",  # SLEEP(5)
            r"SUBSTRING\s*\(",  # SUBSTRING(@@version,1,1)
            r"@@version",  # @@version
            r"\/\*\s*\/",  # /**/
            r"SELECT\s+\*\s+FROM",  # SELECT * FROM (SQL запросы в параметрах)
            r"WHERE\s+\w+\s*=\s*\d+['\"]\s*OR",  # WHERE id=1' OR
        ]
        
        # Паттерны XSS атак (более специфичные)
        # Проверяем XSS в пути или в контексте, где это явно вредоносно
        xss_patterns = [
            r"<img[^>]*onerror\s*=",  # <img onerror=
            r"<svg[^>]*onload\s*=",  # <svg onload=
            r"onerror\s*=\s*alert",  # onerror=alert
            r"onload\s*=\s*alert",  # onload=alert
            r"javascript:",  # javascript:
            r"<iframe",  # <iframe>
            r"document\.cookie",  # document.cookie
            r"eval\s*\(",  # eval(
            r"<body[^>]*onload",  # <body onload
        ]
        
        # XSS в пути запроса (всегда вредоносный)
        xss_in_path_patterns = [
            r"<script[^>]*>",  # <script> в пути
        ]
        
        # Паттерны Path Traversal
        path_traversal_patterns = [
            r"\.\.\/\.\.\/",  # ../../
            r"\.\.\\\.\.\\",  # ..\..\
            r"\.\.\/\.\.\/\.\.\/",  # ../../../
            r"\.\.\/\.\.\/etc\/passwd",  # ../../etc/passwd
            r"\.\.\/\.\.\/\.\.\/etc\/passwd",  # ../../../etc/passwd
            r"\.\.\/\.\.\/\.\.\/\.\.\/etc\/passwd",  # ../../../../etc/passwd
            r"\.\.\/\.\.\/etc\/shadow",  # ../../etc/shadow
            r"\.\.\/\.\.\/windows\/system32",  # ../../windows/system32
            r"\.\.\/\.\.\/\.\.\/\.\.\/",  # ../../../../ (4 уровня)
            r"\.\.\/\.\.\/\.\.\/\.\.\/\.\.\/",  # ../../../../../ (5 уровней)
            r"\.\.\/.*\.\.\/.*\/etc\/passwd",  # ../something/../etc/passwd (с промежуточными путями)
            r"\.\.\/.*\.\.\/.*\/etc\/shadow",  # ../something/../etc/shadow
            r"\.\.\/.*\.\.\/.*passwd",  # ../something/../passwd
            r"\.\.\/.*\.\.\/.*shadow",  # ../something/../shadow
            r"\/etc\/passwd",  # /etc/passwd (прямой доступ к системным файлам в пути)
            r"\/etc\/shadow",  # /etc/shadow
            r"\/windows\/system32",  # /windows/system32
        ]
        
        # Паттерны Command Injection
        command_injection_patterns = [
            r";\s*(rm|cat|ls|pwd|whoami|id|uname)",  # ; rm -rf
            r"\|\s*(rm|cat|ls|pwd|whoami|id|uname)",  # | rm -rf
            r"&&\s*(rm|cat|ls|pwd|whoami|id|uname)",  # && rm -rf
            r"`.*(rm|cat|ls|pwd|whoami|id|uname)",  # `rm -rf`
            r"\$\(.*(rm|cat|ls|pwd|whoami|id|uname)",  # $(rm -rf)
            r"rm\s+-rf",  # rm -rf
            r"cat\s+\/etc\/passwd",  # cat /etc/passwd
            r"system\s*\(",  # system(
            r"exec\s*\(",  # exec(
            r"shell_exec",  # shell_exec
            r"passthru",  # passthru
            r"proc_open",  # proc_open
        ]
        
        # Паттерны XXE атак
        xxe_patterns = [
            r"<!ENTITY.*SYSTEM",  # <!ENTITY xxe SYSTEM
            r"file:///",  # file:///
            r"<!DOCTYPE.*\[",  # <!DOCTYPE foo [
            r"&[a-zA-Z]+;",  # &xxe;
        ]
        
        # Паттерны Template Injection
        template_injection_patterns = [
            r"\{\{.*\}\}",  # {{...}}
            r"#\{.*\}",  # #{...}
            r"\$\{.*\}",  # ${...}
            r"\{\%.*\%\}",  # {%...%}
            r"constructor\.constructor",  # constructor.constructor
            r"process\.mainModule",  # process.mainModule
            r"require\s*\(['\"]child_process['\"]\)",  # require('child_process')
        ]
        
        # Паттерны Code Injection
        code_injection_patterns = [
            r"require\s*\(['\"]child_process['\"]\)\.exec",  # require('child_process').exec
            r"eval\s*\(['\"].*['\"]\)",  # eval('...')
            r"Function\s*\(",  # Function(
            r"new Function",  # new Function
            r"setTimeout\s*\(['\"].*['\"]\)",  # setTimeout('...')
            r"setInterval\s*\(['\"].*['\"]\)",  # setInterval('...')
        ]
        
        # Паттерны PHP Shell Upload
        php_shell_patterns = [
            r"<\?php.*system",  # <?php system
            r"<\?php.*exec",  # <?php exec
            r"<\?php.*shell_exec",  # <?php shell_exec
            r"<\?php.*\$_GET",  # <?php $_GET
            r"<\?php.*\$_POST",  # <?php $_POST
            r"filename.*\.php",  # filename="shell.php"
        ]
        
        # Паттерны XPath Injection
        xpath_injection_patterns = [
            r"\[.*or.*\]",  # [username='admin' or '1'='1']
            r"\[.*'1'='1'\]",  # ['1'='1']
            r"\[.*or.*'1'='1'\]",  # [or '1'='1']
        ]
        
        # Объединяем все паттерны (без xss_in_path_patterns - они проверяются отдельно)
        all_patterns = (
            sql_patterns + 
            xss_patterns + 
            path_traversal_patterns + 
            command_injection_patterns + 
            xxe_patterns + 
            template_injection_patterns + 
            code_injection_patterns + 
            php_shell_patterns + 
            xpath_injection_patterns
        )
        
        # Сначала проверяем параметризованные SQL запросы - они безопасны
        # Если это JSON с параметризованным SQL запросом - это безопасно
        skip_sql_patterns = False
        if re.search(r"application/json", request_lower, re.IGNORECASE):
            if re.search(r'"sql"\s*:', decoded_request_lower, re.IGNORECASE):
                # Проверяем наличие параметров отдельно
                if re.search(r'"params"\s*:\s*\[', decoded_request_lower, re.IGNORECASE):
                    # Извлекаем SQL запрос
                    sql_match = re.search(r'"sql"\s*:\s*"([^"]+)"', decoded_request_lower, re.IGNORECASE)
                    if sql_match:
                        sql_query = sql_match.group(1)
                        # Если SQL содержит параметризацию (?) - это безопасно
                        if re.search(r"\?", sql_query, re.IGNORECASE):
                            # Но проверяем, нет ли SQL инъекции в самом запросе
                            # Если есть OR '1'='1 или другие инъекции в SQL - вредоносно
                            if not re.search(r"['\"]\s*OR\s*['\"]?1['\"]?\s*=\s*['\"]?1", sql_query, re.IGNORECASE) and \
                               not re.search(r"UNION\s+SELECT", sql_query, re.IGNORECASE) and \
                               not re.search(r"DROP\s+TABLE", sql_query, re.IGNORECASE):
                                # Это безопасный параметризованный запрос
                                # Пропускаем SQL паттерны, но проверяем другие типы атак
                                skip_sql_patterns = True
                            else:
                                # SQL содержит инъекцию - вредоносно
                                return True
        
        # Проверяем запрос на наличие вредоносных паттернов (в оригинале и декодированном виде)
        # Разделяем SQL паттерны и остальные
        sql_patterns_only = sql_patterns
        other_patterns = xss_patterns + path_traversal_patterns + command_injection_patterns + \
                        xxe_patterns + template_injection_patterns + code_injection_patterns + \
                        php_shell_patterns + xpath_injection_patterns
        
        # Проверяем SQL паттерны только если это не параметризованный запрос
        if not skip_sql_patterns:
            for pattern in sql_patterns_only:
                if re.search(pattern, request_lower, re.IGNORECASE | re.DOTALL):
                    return True
                if re.search(pattern, decoded_request_lower, re.IGNORECASE | re.DOTALL):
                    return True
        
        # Проверяем остальные паттерны (всегда)
        for pattern in other_patterns:
            if re.search(pattern, request_lower, re.IGNORECASE | re.DOTALL):
                return True
            if re.search(pattern, decoded_request_lower, re.IGNORECASE | re.DOTALL):
                return True
        
        # Дополнительная проверка: простые SQL-подобные запросы без признаков инъекции - безопасны
        # Проверяем только если это в параметрах запроса (может быть поисковым запросом или тестовым endpoint)
        if path_part:
            path_to_check = path_part_decoded if path_part_decoded else path_part
            if '?' in path_to_check:
                path_only = path_to_check.split('?')[0]
                params = path_to_check.split('?', 1)[1]
                
                # Если это API endpoint с параметром query/search/filter - проверяем на безопасные запросы
                if re.search(r"^/api/", path_only, re.IGNORECASE):
                    # Проверяем параметры query, search, filter, test
                    param_name_match = re.search(r"^(query|search|filter|q|test|id)=(.+)", params, re.IGNORECASE)
                    if param_name_match:
                        param_name = param_name_match.group(1).lower()
                        param_value = param_name_match.group(2)
                        
                        # Для query/search/filter/test - SQL-подобные запросы могут быть легитимными
                        if param_name in ['query', 'search', 'filter', 'q', 'test']:
                            # Проверяем, нет ли признаков реальной SQL инъекции
                            has_injection_signs = re.search(r"['\"]\s*OR\s*['\"]?1['\"]?\s*=\s*['\"]?1", param_value, re.IGNORECASE) or \
                                                re.search(r"--", param_value) or \
                                                re.search(r";", param_value) or \
                                                re.search(r"UNION\s+SELECT.*FROM", param_value, re.IGNORECASE) or \
                                                re.search(r"DROP\s+TABLE", param_value, re.IGNORECASE)
                            
                            if not has_injection_signs:
                                # Это легитимный поисковый/тестовый запрос - безопасно
                                # Но проверяем другие типы атак (XSS, path traversal и т.д.)
                                pass
                        # Для test endpoint даже SQL инъекции могут быть легитимными (тестовые данные)
                        elif param_name == 'test' or re.search(r"/test", path_only, re.IGNORECASE):
                            # Тестовые endpoints могут принимать любые данные
                            # Но проверяем другие типы атак
                            pass
        
        # Специальная проверка XSS: <script> теги в пути запроса - всегда вредоносны
        # Но в параметрах API запросов могут быть безопасными (легитимное использование)
        if path_part:
            path_to_check = path_part_decoded if path_part_decoded else path_part
            # Разделяем путь и параметры
            if '?' in path_to_check:
                path_only = path_to_check.split('?')[0]
                params = path_to_check.split('?', 1)[1]
            else:
                path_only = path_to_check
                params = ""
            
            # Проверяем <script> в пути (до знака ?) - всегда вредоносно
            for pattern in xss_in_path_patterns:
                if re.search(pattern, path_only, re.IGNORECASE):
                    return True
            
            # Если это API endpoint и <script> только в параметрах - это может быть безопасно
            # Но проверяем другие опасные паттерны в параметрах
            if re.search(r"^/api/", path_only, re.IGNORECASE):
                # Для API endpoints, <script> в параметрах может быть легитимным
                # Но проверяем другие XSS паттерны (onerror, onload и т.д.)
                pass  # Пропускаем проверку <script> в параметрах API
            else:
                # Для не-API endpoints, <script> в параметрах тоже подозрительно
                for pattern in xss_in_path_patterns:
                    if re.search(pattern, params, re.IGNORECASE):
                        return True
        
        # Дополнительная проверка path traversal в пути (более точная)
        if path_part:
            # Проверяем path traversal в пути запроса (оригинал и декодированный)
            path_to_check = path_part_decoded if path_part_decoded else path_part
            if re.search(r"\.\.\/", path_to_check) or re.search(r"\.\.\\", path_to_check):
                # Если в пути есть системные файлы - это атака
                if re.search(r"\/etc\/passwd|\/etc\/shadow|\/windows\/system32|passwd|shadow", path_to_check):
                    return True
                # Если есть два или более ../ в пути - подозрительно
                dot_dot_count = len(re.findall(r"\.\.\/", path_to_check)) + len(re.findall(r"\.\.\\", path_to_check))
                if dot_dot_count >= 2:
                    # Блокируем если есть системные файлы или много уровней вверх
                    if re.search(r"\/etc\/|\/windows\/|passwd|shadow|system32", path_to_check):
                        return True
        
        # Дополнительные проверки для сложных случаев
        
        # Проверка на SQL инъекцию в параметрах запросов (даже для API endpoints)
        # SQL инъекция в параметрах - всегда вредоносна, даже если это API
        # НО: простые поисковые запросы с SQL-ключевыми словами безопасны
        if path_part:
            path_to_check = path_part_decoded if path_part_decoded else path_part
            if '?' in path_to_check:
                params = path_to_check.split('?', 1)[1]
                # Проверяем SQL паттерны в параметрах - только реальные инъекции
                # НО: для query/search/filter/test параметров в API - даже SQL инъекции могут быть легитимными
                path_only = path_to_check.split('?')[0] if '?' in path_to_check else path_to_check
                is_api_query_param = False
                is_test_endpoint = False
                
                # Проверяем, является ли это параметром query/search/filter/test в API
                param_name_match = re.search(r"^(query|search|filter|q|test|id)=(.+)", params, re.IGNORECASE)
                if param_name_match and re.search(r"^/api/", path_only, re.IGNORECASE):
                    param_name = param_name_match.group(1).lower()
                    if param_name in ['query', 'search', 'filter', 'q']:
                        # Для query/search/filter - даже SQL инъекции могут быть легитимными поисковыми запросами
                        is_api_query_param = True
                    elif param_name in ['test', 'id'] and (re.search(r"/test", path_only, re.IGNORECASE) or re.search(r"/filter", path_only, re.IGNORECASE)):
                        # Для test и filter endpoints - даже SQL инъекции могут быть легитимными
                        is_api_query_param = True
                
                # Для тестовых endpoints - даже SQL инъекции могут быть легитимными
                if re.search(r"/test|/filter", path_only, re.IGNORECASE):
                    is_test_endpoint = True
                
                # Для всех filter endpoints с любым параметром - SQL запросы безопасны
                if re.search(r"/filter", path_only, re.IGNORECASE):
                    is_api_query_param = True
                
                # Проверяем SQL паттерны только если это не API query/search/filter/test endpoint
                if not is_api_query_param and not is_test_endpoint:
                    sql_in_params_patterns = [
                        r"['\"]\s*OR\s*['\"]?1['\"]?\s*=\s*['\"]?1",  # ' OR '1'='1
                        r"\d+['\"]\s*OR\s*['\"]?1['\"]?\s*=\s*['\"]?1",  # 1' OR '1'='1
                        r"UNION\s+SELECT.*--",  # UNION SELECT с комментариями
                        r"WHERE\s+.*OR\s+['\"]?1['\"]?\s*=\s*['\"]?1",  # WHERE ... OR '1'='1
                        r"UNION\s+SELECT\s+NULL.*--",  # UNION SELECT NULL с комментариями
                        r"';?\s*--",  # ';-- SQL инъекция
                    ]
                    for pattern in sql_in_params_patterns:
                        if re.search(pattern, params, re.IGNORECASE):
                            return True
                # UNION SELECT может быть инъекцией только если есть признаки SQL синтаксиса
                # Простой поиск "union select" без кавычек и комментариев - безопасен
                if re.search(r"UNION\s+SELECT", params, re.IGNORECASE):
                    # Проверяем признаки реальной SQL инъекции
                    has_sql_injection_signs = re.search(r"['\"]", params, re.IGNORECASE) or \
                                            re.search(r"--", params) or \
                                            re.search(r";", params) or \
                                            re.search(r"WHERE.*OR", params, re.IGNORECASE)
                    if has_sql_injection_signs:
                        return True
                # SELECT * в параметрах может быть вредоносным, но только если нет параметризации
                if re.search(r"SELECT\s+\*", params, re.IGNORECASE):
                    # Проверяем, нет ли признаков параметризованного запроса
                    if not re.search(r"\?", params, re.IGNORECASE):
                        # Проверяем признаки SQL инъекции
                        if re.search(r"['\"]", params, re.IGNORECASE) or re.search(r"FROM\s+\w+.*WHERE", params, re.IGNORECASE):
                            return True
        
        # Проверка на SQL инъекцию с комментариями между ключевыми словами
        if re.search(r"union.*select", decoded_request_lower, re.IGNORECASE):
            if re.search(r"\/\*|\*\/|--", decoded_request_lower):
                return True
        
        # Проверка на SQL инъекцию с URL-encoded пробелами (+)
        # Декодированная версия уже проверяется, но добавим специфичные паттерны
        # НО: пропускаем параметризованные запросы (они уже проверены выше)
        # Эта проверка только для случаев, когда параметризованный запрос не был обнаружен
        if re.search(r"SELECT\s+\*|\+FROM", decoded_request_lower, re.IGNORECASE):
            # Проверяем, не является ли это параметризованным запросом
            is_parameterized = re.search(r"id\s*=\s*\?", decoded_request_lower, re.IGNORECASE) or \
                              re.search(r'"params"\s*:\s*\[', decoded_request_lower, re.IGNORECASE) or \
                              re.search(r"params\s*=\s*\[", decoded_request_lower, re.IGNORECASE)
            
            if not is_parameterized:
                if re.search(r"['\"]\s*OR\s*['\"]?1['\"]?\s*=\s*['\"]?1", decoded_request_lower, re.IGNORECASE):
                    return True
        
        
        # Проверка на замаскированный path traversal (....//....//)
        if re.search(r"\.\.\.\.\/\/", request_lower) or re.search(r"\.\.\.\.\\\\", request_lower):
            return True
        
        # Проверка на path traversal с системными файлами (используем извлеченный путь)
        if path_part:
            path_to_check = path_part_decoded if path_part_decoded else path_part
            # Проверяем наличие ../ в пути
            has_dot_dot = re.search(r"\.\.\/", path_to_check) or re.search(r"\.\.\\", path_to_check)
            if has_dot_dot:
                # Если есть path traversal И системные файлы в пути - это атака
                if re.search(r"\/etc\/passwd|\/etc\/shadow|\/windows\/system32", path_to_check):
                    return True
                # Если есть два или более уровня вверх (../..) И системные файлы - это атака
                dot_dot_count = len(re.findall(r"\.\.\/", path_to_check)) + len(re.findall(r"\.\.\\", path_to_check))
                if dot_dot_count >= 2:
                    # Проверяем наличие системных файлов в пути
                    if re.search(r"passwd|shadow|system32", path_to_check):
                        return True
                    # Если много уровней вверх без явного API endpoint - подозрительно
                    # Но разрешаем если это явно API endpoint типа /api/load?file=...
                    if not re.search(r"\/api\/[^\/]+\?.*file=", path_to_check):
                        # Если есть /etc/ или /windows/ в пути с path traversal - блокируем
                        if re.search(r"\/etc\/|\/windows\/", path_to_check):
                            return True
        
        # Дополнительная проверка на URL-encoded XSS атаки
        # Проверяем декодированную версию на XSS паттерны
        xss_patterns_decoded = [
            r"<svg[^>]*onload",  # <svg onload
            r"<img[^>]*onerror",  # <img onerror
            r"onload\s*=\s*alert",  # onload=alert
            r"onerror\s*=\s*alert",  # onerror=alert
        ]
        for pattern in xss_patterns_decoded:
            if re.search(pattern, decoded_request_lower, re.IGNORECASE):
                return True
        
        # Проверка <script> в декодированной версии уже выполнена выше
        # Дополнительная проверка для случаев без явного пути
        if not path_part:
            # Если нет пути, проверяем весь запрос, но только если это не явно API
            if not re.search(r"/api/", decoded_request_lower, re.IGNORECASE):
                if re.search(r"<script", decoded_request_lower, re.IGNORECASE):
                    return True
        
        # Проверка на опасные команды в параметрах или теле запроса
        dangerous_commands = [
            'rm -rf', 'cat /etc/passwd', 'system(', 'exec(', 'eval(',
            'child_process', 'shell_exec', 'passthru', 'proc_open',
            'file_get_contents', 'readfile', 'fopen'
        ]
        for cmd in dangerous_commands:
            if cmd in request_lower:
                return True
        
        # Проверка на PHP код в запросе
        if re.search(r"<\?php", request_lower) or re.search(r"<\?", request_lower):
            if re.search(r"(system|exec|shell_exec|passthru|eval|base64_decode)", request_lower):
                return True
        
        # Проверка на опасные функции в JavaScript/Node.js
        if re.search(r"require\s*\(['\"]child_process['\"]\)", request_lower):
            return True
        
        # Проверка на template injection с опасными конструкциями
        if re.search(r"constructor\.constructor", request_lower):
            if re.search(r"process|require|eval", request_lower):
                return True
        
        # Проверка на XXE с внешними сущностями
        if re.search(r"<!ENTITY", request_lower):
            if re.search(r"SYSTEM|file://|http://", request_lower):
                return True
        
        # Проверка на XPath injection
        if re.search(r"\[.*or.*'1'='1'\]", request_lower) or re.search(r"\[.*or.*1=1\]", request_lower):
            return True
        
        # Проверка на замаскированные SQL инъекции (с пробелами замененными на комментарии)
        if re.search(r"\/\*\s*\/", request_lower):
            if re.search(r"(union|select|or|and)", request_lower):
                return True
        
        # Если ничего не найдено - запрос безопасный
        return False
    
    def extract_request(self, data):
        """Извлекает HTTP запрос из полученных данных"""
        # Ищем паттерн начала запроса (--- Request X/100 ---)
        request_start_marker = re.search(r'--- Request \d+/\d+ ---', data)
        if request_start_marker:
            start_pos = request_start_marker.end()
        else:
            # Если маркера нет, ищем начало HTTP запроса
            http_match = re.search(r'(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+', data, re.IGNORECASE)
            if http_match:
                start_pos = http_match.start()
            else:
                return None
        
        # Ищем конец запроса (строка "Your answer" или "Block/Allow")
        answer_marker = data.find('Your answer', start_pos)
        if answer_marker == -1:
            answer_marker = data.find('Block/Allow', start_pos)
        if answer_marker == -1:
            answer_marker = data.find('(Block/Allow)', start_pos)
        
        if answer_marker != -1:
            request_text = data[start_pos:answer_marker].strip()
        else:
            # Если маркера ответа нет, берем до конца данных, но не более 2000 символов
            request_text = data[start_pos:start_pos+2000].strip()
        
        # Убираем лишние пробелы и переносы строк в начале/конце
        request_text = request_text.strip()
        
        # Проверяем, что это действительно HTTP запрос
        if not re.match(r'(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+', request_text, re.IGNORECASE):
            return None
        
        return request_text if request_text else None
    
    def solve(self):
        """Решает задание"""
        if not self.connect():
            return False
        
        # Получаем приветствие
        welcome = self.receive_data()
        print("=== Приветствие ===")
        print(welcome)
        
        # Отправляем Start
        print("\nОтправляем 'Start'...")
        self.send_data("Start")
        
        question_count = 0
        correct_count = 0
        buffer = ""
        
        # Устанавливаем таймаут для получения данных
        self.socket.settimeout(5)
        
        while question_count < 100:
            # Получаем данные
            data = self.receive_data(8192)
            if data:
                buffer += data
            
            # Проверяем, есть ли в буфере флаг или финальное сообщение
            if "Flag:" in buffer or "flag:" in buffer.lower() or question_count >= 100:
                if question_count >= 100:
                    # Получаем оставшиеся данные от сервера
                    for _ in range(5):  # Делаем несколько попыток получить оставшиеся данные
                        time.sleep(0.2)
                        try:
                            data = self.receive_data(8192)
                            if data:
                                buffer += data
                            else:
                                break
                        except:
                            break
                
                print("\n" + "="*50)
                print("РЕЗУЛЬТАТ:")
                print("="*50)
                # Выводим все что сервер написал
                print(buffer)
                
                flag_match = re.search(r'Flag:\s*([^\s\n]+)', buffer, re.IGNORECASE)
                if flag_match:
                    print("\n" + "="*50)
                    print("ФЛАГ ПОЛУЧЕН!")
                    print("="*50)
                    print(f"Flag: {flag_match.group(1)}")
                elif "flag:" in buffer.lower():
                    flag_pos = buffer.lower().find('flag:')
                    if flag_pos != -1:
                        print("\n" + "="*50)
                        print("ФЛАГ ПОЛУЧЕН!")
                        print("="*50)
                        print(buffer[max(0, flag_pos-50):flag_pos+100])
                
                if question_count >= 100:
                    break
            
            # Проверяем на ошибку
            if "Wrong" in buffer or ("failed" in buffer.lower() and "Challenge failed" in buffer):
                print("\n❌ Ошибка! Задание провалено.")
                wrong_pos = buffer.find('Wrong')
                if wrong_pos != -1:
                    print(buffer[max(0, wrong_pos-100):wrong_pos+200])
                break
            
            # Сначала обрабатываем ответы о правильности (если есть)
            while "Correct!" in buffer:
                correct_match = re.search(r'Correct!\s*\((\d+)/100\)', buffer)
                if correct_match:
                    new_correct_count = int(correct_match.group(1))
                    if new_correct_count > correct_count:
                        correct_count = new_correct_count
                        print(f"✓ Правильно! ({correct_count}/100)")
                
                # Удаляем сообщение "Correct!" из буфера
                correct_pos = buffer.find('Correct!')
                if correct_pos != -1:
                    # Удаляем до конца строки
                    end_pos = buffer.find('\n', correct_pos)
                    if end_pos != -1:
                        buffer = buffer[:correct_pos] + buffer[end_pos+1:]
                    else:
                        buffer = buffer[:correct_pos]
            
            # Извлекаем HTTP запрос из буфера
            request_text = self.extract_request(buffer)
            
            if request_text:
                # Анализируем запрос
                is_malicious = self.is_malicious(request_text)
                
                question_count += 1
                answer = "Block" if is_malicious else "Allow"
                
                print(f"\n{'='*60}")
                print(f"Вопрос {question_count}/100:")
                print(f"{'='*60}")
                display_request = request_text[:400] + "\n..." if len(request_text) > 400 else request_text
                print(f"Запрос:\n{display_request}")
                print(f"\nАнализ: {'🔴 ВРЕДОНОСНЫЙ' if is_malicious else '🟢 БЕЗОПАСНЫЙ'}")
                print(f"Ответ: {answer}")
                
                # Отправляем ответ
                self.send_data(answer)
                
                # Удаляем обработанный запрос из буфера
                # Ищем начало запроса в буфере
                request_start = buffer.find(request_text[:50])
                if request_start != -1:
                    # Ищем маркер "Your answer" после запроса
                    answer_marker = buffer.find('Your answer', request_start)
                    if answer_marker != -1:
                        # Удаляем все до маркера включительно
                        buffer = buffer[answer_marker + len('Your answer'):]
                    else:
                        # Если маркера нет, удаляем сам запрос
                        buffer = buffer[:request_start] + buffer[request_start + len(request_text):]
                
                time.sleep(0.15)  # Небольшая задержка
            
            # Если буфер слишком большой, очищаем старые данные
            elif len(buffer) > 5000:
                # Оставляем последние 2000 символов
                buffer = buffer[-2000:]
            
            # Если нет данных и нет запроса в буфере, небольшая пауза
            if not data and not request_text:
                time.sleep(0.1)
        
        # Если дошли до конца цикла, получаем финальное сообщение от сервера
        if question_count >= 100:
            final_buffer = ""
            for _ in range(5):  # Делаем несколько попыток получить финальное сообщение
                time.sleep(0.2)
                try:
                    data = self.receive_data(8192)
                    if data:
                        final_buffer += data
                    else:
                        break
                except:
                    break
            
            if final_buffer:
                print("\n" + "="*50)
                print("ФИНАЛЬНОЕ СООБЩЕНИЕ ОТ СЕРВЕРА:")
                print("="*50)
                print(final_buffer)
                
                flag_match = re.search(r'Flag:\s*([^\s\n]+)', final_buffer, re.IGNORECASE)
                if flag_match:
                    print("\n" + "="*50)
                    print("ФЛАГ ПОЛУЧЕН!")
                    print("="*50)
                    print(f"Flag: {flag_match.group(1)}")
        
        self.socket.close()
        return True

def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='WAF CTF Client - автоматическое решение')
    parser.add_argument('--host', default='localhost', help='Хост сервера (по умолчанию: localhost)')
    parser.add_argument('--port', type=int, default=1337, help='Порт сервера (по умолчанию: 1337)')
    
    args = parser.parse_args()
    
    print("="*50)
    print("WAF CTF Client - Автоматическое решение")
    print("="*50)
    
    client = WAFClient(host=args.host, port=args.port)
    client.solve()

if __name__ == "__main__":
    main()
