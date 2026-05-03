# [osint] City that doesn't exist

> **Category:** `osint`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [_Kid's sweet dream.canvas](./files/img_1.canvas) | `canvas` |

</details>

---

In one of the largest shopping centers in southern Russia, there was a children's themed park — a licensed clone of a foreign concept. In 2019, the park suddenly changed its name. No official statements were made.

Your task is to identify the legal entity that managed the clone and find the latest date of trademark registration submission through the Register of Intellectual Property of the Russian Federation.

Flag: KubSTU{INN_of_management_company_date_of_trademark_submission_in_Rospatent}
Format example: KubSTU{1234567890_01.01.2000}

## 🚩 Flag

```
KubSTU{INN_of_managment_company_date_of_trademark_submission_in_Rospatent}
```

Initial data: largest shopping center in southern Russia + children's themed park
Google/Yandex → "Krasnodar Krylataya 2 children's park" → ZkidZ City → searching for historical information → Minopolis.

Biglion.ru → ZkidZ City coupon → in the terms there's a link to a PDF with visitation rules (st.biglion.ru/upload/2019/pravila_parka_zkidz_city.pdf). The document header reads: "Approved by Order No. 03 dated 09.01.2019, OOO 'S A Richie Yug'". But we dig deeper.

EGRUL (egrul.nalog.ru) → search by address 350040, Krasnodar, Krylataya, 2 → OOO "Detstvo +" INN 2312206762. Primary OKVED: 93.29 — leisure and entertainment. 127 employees (2018). Director: Zakhrabyan R.A.

Rusprofile.ru → OOO "Detstvo +" → founder OOO "Massmarket" (INN 7701722800, Moscow, Leningradsky pr-kt, 37 bld. 9).

fips.ru → trademark register → search "MINOPOLIS" → find application 2018756480, registration 723853, rights holder: Minopolis Worldwide Edutainment LLC, application filing date: 20.12.2018.

In the same register: search by certificate number 723853 in the "contracts" section → licensee OOO "Detstvo +", contract registration date matches the trademark application filing date.

Flag — KubSTU{2312206762_20.12.2018}
