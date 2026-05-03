# [osint] 49 days

> **Category:** `osint`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [_Kid's sweet dream.canvas](./files/img_1.canvas) | `canvas` |

</details>

---

Difficulty: nightmare

The international rights holder of a children's themed park brand operated through a chain of legal entities across multiple jurisdictions. The key link in this chain — a Swiss company — was originally created under a different name and subsequently renamed.

Your task:
- Determine the original (pre-rename) name of the Swiss holding company above the rights holder
- Determine the OKFS code of the Russian management company and explain its anomaly with respect to the founders' composition
- Find the full name of the individual who held the position of President in the international rights holder structure from 2009 to 2019, and their previous employer that has a direct office in Moscow

Flag: KubSTU{original_name:OKFS:president_surname:company_with_Moscow_office}
Format example: KubSTU{Some_Name:01:Ivanov:Some_Firm}

STEP 1: Uncovering the LLC
Trademarkia.com → search "Minopolis Worldwide Edutainment LLC"
CTM application 006129035 (EUIPO, 27.08.2007)
Correspondent: Alexander Lederer, Wedertorgasse 12, Wien AT 1010

Observation: LLC is not an Austrian legal form (that would be GmbH).
"Worldwide" in the name + LLC = likely an offshore or US-Delaware entity.
Dr. Sami Hamid's profile: "President of Minopolis Worldwide
Edutainment LLC — operations in Asia, Middle East, Eastern Europe."

Conclusion: The LLC holds the intellectual property rights. The AG is the operational holding. Two separate legal entities in two jurisdictions.

STEP 2: Swiss holding → Pinfarina AG
Search "Minopolis Edutainment AG Switzerland" →
Moneyhouse.ch: CHE-115.593.420, Baar, ZG
Past names: PINFARINA AG (until 28.07.2010)

Cross-verification via SHAB (Schweizer Handelsamtsblatt):
Publication 28.07.2010:
"Pinfarina AG, in Zug → Firma neu: Minopolis Edutainment AG"

Rename date: 30.06.2010 (articles of association) / 28.07.2010 (publication)
Coincides with the announcement of the first international park in Krasnodar (2011).

STEP 3: OKFS anomaly
OOO "Agat Group" INN 7730647650 → EGRUL:
Founders: Ageeva Zilya Khalyafovna (51%), Ageev Rustam (49%)
Both: INN starts with 1657... → Republic of Tatarstan.
Both are Russian citizens.

Statistical codes (Rosstat):
OKFS = 34 = "Joint private and foreign ownership"
OKGU = 4210011 = "Business entities with participation of foreign
          legal entities and/or individuals"

Contradiction: two individuals who are Russian citizens → OKFS 34 = foreign element.
Likely explanation: a foreign participant (Minopolis AG or an affiliated structure) joined at registration in 2011, then exited — but OKFS is assigned at registration and doesn't automatically change when founders change. Alternatively, the Ageevs hold their shares nominally. Agat Group's registration (15.07.2011) occurred 3 weeks after the Minopolis announcement at OZ Mall (June 2011).

STEP 4: President → Ward Howell
LinkedIn: "Sami Hamid President Minopolis"
→ The Org / Signium: "Sami held the position of President at
  Minopolis from January 2009"
→ Before: "Managing Partner at Ward Howell International,
  February 1992 – May 2009"

AESC.org: "Ward Howell co-founded its affiliated firm in Russia
in 1992" → office in Moscow, Mozhaysky Val, 8.

ZoomInfo: Ward Howell — Mozhaysky Val Street Building 8, Moscow.
Company active, 100-249 employees.

Additional pivot:
Dr. Sami Hamid leaves Minopolis AG: 07.05.2019 (SHAB)
Minopolis AG is liquidated: 25.06.2019
Interval: 49 days → Hamid left the ship before it sank.

Assembling the flag:
Component 1: Pinfarina_AG — original AG name
Component 2: 34 — OKFS of Agat Group = foreign element
Component 3: Hamid — surname of President 2009-2019
Component 4: Ward_Howell — company with Moscow office
Flag — KubSTU{Pinfarina_AG:34:Hamid:Ward_Howell}
