# [crypto] Strange sequence of numbers

> **Категория:** `crypto`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Файлы к заданию</summary>

| Файл | Тип |
|------|-----|
| [Strange sequence of numbers.py](./files/img_1.py) | `text/x-python` |
| [strange_sequence_of_numbers.txt](./files/img_4.txt) | `text/plain` |

</details>

---

Получил странный документ с числами внутри, что это может значить?Формат флага KubSTU()
Решение:Видим последовательность чисел они довольно разные но можем но некоторые из них повторяются (пример число 99)это может навести на мысль что этими кодами стоит какой-то специальный символ, а также все числа разделены пробеламиПробуем расшифровать это как ascii коды

![image.png](./images/img_2.png)

Флаг: KubSTU(asc11_c0d3s_ar3_an_1nteresting_w4y_to_ge7_into_cryp70graphy)
