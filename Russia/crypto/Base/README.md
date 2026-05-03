# [crypto] Base

> **Категория:** `crypto`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Файлы к заданию</summary>

| Файл | Тип |
|------|-----|
| [Base.py](./files/img_1.py) | `text/x-python` |
| [Base.txt](./files/img_4.txt) | `text/plain` |
| [Base.txt](./files/img_5.txt) | `text/plain` |

</details>

---

Мы перехватили странное сообщение.  Кажется, оно закодировано популярным методом. Помоги понять, что там написано.  Формат флага KubSTU()
Решение:Структура строки и само название задание прям кричит о том, что это base кодировка, осталось перепробовать её вариации.Валидным оказывается только base64

![image.png](./images/img_2.png)

Флаг: KubSTU(b4s3_64_1s_the_ba5i5)
