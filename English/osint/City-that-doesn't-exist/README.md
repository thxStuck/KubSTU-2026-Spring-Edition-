# [osint] City that doesn't exist

> **Category:** `osint`  
> **CTF:** KubSTU CTF 2026 Spring

In one of the largest shopping centers in southern Russia, there was a children's themed park — a licensed clone of a foreign concept. In 2019, the park suddenly changed its name. No official statements were made. 

Your task is to identify the legal entity that managed the clone and find the latest date of trademark registration submission through the Register of Intellectual Property of the Russian Federation.  

Flag: KubSTU{INN_of_management_company_date_of_trademark_submission_in_Rospatent}  Format example: `KubSTU{1234567890_01.01.2000}`    

---

In one of the largest shopping centers in southern Russia, there was a children's themed park — a licensed clone of a foreign concept. In 2019, the park suddenly changed its name. No official statements were made.  

Your task is to identify the legal entity that managed the clone and find the latest date of trademark registration submission through the Register of Intellectual Property of the Russian Federation.  

Flag: KubSTU{INN_of_management_company_date_of_trademark_submission_in_Rospatent}  Format example: `KubSTU{1234567890_01.01.2000}`

---

Initial data: the largest shopping center in southern Russia + children's themed park

1. Google/Yandex → "Krasnodar Krylataya 2 children's park" → ZkidZ City → searching for historical information → Minopolis
2. [Biglion.ru](http://Biglion.ru) → ZkidZ City coupon → in the terms there's a link to a PDF with visitation rules ([st.biglion.ru/upload/2019/pravila_parka_zkidz_city.pdf](http://st.biglion.ru/upload/2019/pravila_parka_zkidz_city.pdf)). In the document header: "Approved by Order No. 03 dated 09.01.2019 by LLC 'S A Ricci Yug'". But we dig deeper.
3. EGRUL ([egrul.nalog.ru](http://egrul.nalog.ru)) → search by address 350040, Krasnodar, Krylataya, 2 → LLC "Detstvo +" (Childhood +) INN 2312206762. Primary OKVED: 93.29 — recreation and entertainment. 127 employees (2018). Director: Zakhrabyan R.A.
4. [Rusprofile.ru](http://Rusprofile.ru) → LLC "Detstvo +" → founder LLC "Massmarket" (INN 7701722800, Moscow, Leningradsky Prospekt, 37 bld. 9).
5. [fips.ru](http://fips.ru) → trademark register → search "MINOPOLIS" → find application 2018756480, registration 723853, rights holder: Minopolis Worldwide Edutainment LLC, application date: 20.12.2018.
6. In the same register: search by certificate number 723853 in the "agreements" section → licensee LLC "Detstvo +", agreement registration date matches the trademark application date.

Flag - `KubSTU{2312206762_20.12.2018}`