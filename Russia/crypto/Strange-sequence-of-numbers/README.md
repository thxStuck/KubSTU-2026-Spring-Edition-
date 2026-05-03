# [crypto] Strange sequence of numbers

> **Категория:** `crypto`  
> **CTF:** KubSTU CTF 2026 Spring

---

Получил странный документ с числами внутри, что это может значить?
Формат флага KubSTU()

[strange_sequence_of_numbers.txt](./files/strange_sequence_of_numbers.txt)

---

Решение:
Видим последовательность чисел они довольно разные но можем но некоторые из них повторяются (пример число 99)
это может навести на мысль что этими кодами стоит какой-то специальный символ, а также все числа разделены пробелами

Пробуем расшифровать это как ascii коды 

 ![img_1.png](./images/img_1.png)


 ![img_2.png](./images/img_2.png)


[Strange sequence of numbers.py](./files/Strange sequence of numbers.py)

Флаг: KubSTU(asc11_c0d3s_ar3_an_1nteresting_w4y_to_ge7_into_cryp70graphy)


