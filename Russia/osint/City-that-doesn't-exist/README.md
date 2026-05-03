# [osint] City that doesn't exist

> **Категория:** `osint`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Файлы к заданию</summary>

| Файл | Тип |
|------|-----|
| [_Kid's sweet dream.canvas](./files/img_1.canvas) | `canvas` |

</details>

---

В одном из крупнейших торговых центров юга России работал детский тематический парк - лицензионный клон иностранной концепции. В 2019 году парк внезапно сменил название. Официальных заявлений не последовало.
Твоя задача - установить юридическое лицо, которое управляло клоном, и найти крайнюю дату подачи заявки на регистрацию товарного знака через реестр интеллектуальной собственности РФ.
Флаг: KubSTU{ИНН_управляющей_компании_дата_подачи_товарного_знака_в_Роспатент}  Пример формата: KubSTU{1234567890_01.01.2000}
In one of the largest shopping centers in southern Russia, there was a children's themed park — a licensed clone of a foreign concept. In 2019, the park suddenly changed its name. No official statements were made.
Your task is to identify the legal entity that managed the clone and find the latest date of trademark registration submission through the Register of Intellectual Property of the Russian Federation.

## 🚩 Флаг

```
KubSTU{INN_of_managment_company_date_of_trademark_submission_in_Rospatent}
```
Исходные данные: крупнейший ТЦ на юге России + детский тематический парк
Google/Яндекс → «Краснодар Крылатая 2 детский парк» → ZkidZ City → поиск исторической информации → Minopolis
Biglion.ru → купон ZkidZ City → в условиях ссылка на PDF правил посещения (st.biglion.ru/upload/2019/pravila_parka_zkidz_city.pdf). В шапке документа: «Утверждено Приказом № 03 от 09.01.2019 г. ООО «Эс Эй Риччи Юг»». Но ищем глубже.
ЕГРЮЛ (egrul.nalog.ru) → поиск по адресу 350040, Краснодар, Крылатая, 2 → ООО «Детство +» ИНН 2312206762. Основной ОКВЭД: 93.29 — отдых и развлечения. 127 сотрудников (2018). Директор: Захрабян Р.А.
Rusprofile.ru → ООО «Детство +» → учредитель ООО «Массмаркет» (ИНН 7701722800, Москва, Ленинградский пр-кт, 37 к.9).
fips.ru → реестр товарных знаков → поиск «MINOPOLIS» → находим заявку 2018756480, регистрация 723853, правообладатель: Минополис Уорлдуайд Эдьютейнмент ЛЛК, дата подачи заявки: 20.12.2018.
В том же реестре: поиск по номеру свидетельства 723853 в разделе «договоры» → лицензиат ООО «Детство +», дата регистрации договора совпадает с датой подачи заявки на знак.
Флаг - KubSTU{2312206762_20.12.2018}
