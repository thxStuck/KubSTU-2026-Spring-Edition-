# [osint] 49 days

> **Category:** `osint`  
> **CTF:** KubSTU CTF 2026 Spring

Difficulty: nightmare


The international rights holder of a children's themed park brand operated through a chain of legal entities across multiple jurisdictions. The key link in this chain — a Swiss company — was originally created under a different name and later renamed.

Your task:

1. Identify the original (pre-renaming) name of the Swiss holding company above the rights holder
2. Identify the OKFS code of the Russian management company and explain its anomaly in relation to the composition of founders
3. Find the full name of the individual who held the position of President in the international rights holder structure from 2009 to 2019, and their previous employer that has a direct office in Moscow

Flag: KubSTU{original_name:OKFS:president_surname:company_with_moscow_office}

Format example: `KubSTU{Some_Name:01:Ivanov:Some_Firm}`

---

## STEP 1: Uncovering the LLC

Trademarkia.com → search "Minopolis Worldwide Edutainment LLC"

> CTM application 006129035 (EUIPO, 27.08.2007)
>
> Correspondent: Alexander Lederer, Wedertorgasse 12, Wien AT 1010


Observation: **LLC is not an Austrian legal form (there it's GmbH)**.

"Worldwide" in the name + LLC = likely offshore or US-Delaware.

Dr. Sami Hamid profile: "President of Minopolis Worldwide 

> Edutainment LLC — operations in Asia, Middle East, Eastern Europe."


Conclusion: LLC is the intellectual property holder. AG is the operational holding.

> Two separate legal entities in two jurisdictions.

---

## STEP 2: Swiss Holding → Pinfarina AG

Search "Minopolis Edutainment AG Switzerland" →

Moneyhouse.ch: CHE-115.593.420, Baar, ZG

> Past names: PINFARINA AG (until 28.07.2010)


Cross-verification via SHAB (Swiss Official Gazette of Commerce):

Publication 28.07.2010:

> "Pinfarina AG, in Zug → Firma neu: Minopolis Edutainment AG"


Renaming date: `30.06.2010 (charter date)` / `28.07.2010 (publication)`

Coincides with the announcement of the first international park in Krasnodar (2011).

---

## STEP 3: OKFS Anomaly

LLC "Agat Group" INN 7730647650 → EGRUL:

Founders: Ageeva Zilya Khalyafovna (51%), Ageev Rustam (49%)

Both: INN starts with 1657... → Republic of Tatarstan.

Both are citizens of the Russian Federation.


Statistics codes (Rosstat):

OKFS = 34 = "Joint private and foreign ownership"

OKOGU = 4210011 = "Business entities with participation of foreign

          legal and/or natural persons"


Contradiction: two RF individuals → OKFS 34 = foreign element.

Likely explanation: a foreign participant (Minopolis AG or an affiliated 

entity) joined at the time of registration in 2011, then later exited — 

but OKFS is assigned at registration and does not change 

automatically when founders change. Or the Ageevs hold their share 

nominally. Registration of Agat Group (15.07.2011) took place 

3 weeks after the Minopolis announcement at OZ Mall (June 2011).

---

## STEP 4: President → Ward Howell

LinkedIn: "Sami Hamid President Minopolis"

→ The Org / Signium: "Sami held the position of President at 

  Minopolis from January 2009"

→ Before: "Managing Partner at Ward Howell International, 

  February 1992 – May 2009"


AESC.org: "Ward Howell co-founded its affiliated firm in Russia 

in 1992" → office in Moscow, Mozhaysky Val, 8.


ZoomInfo: Ward Howell — Mozhaysky Val Street Building 8, Moscow.

Company is active, 100-249 employees.


Additional pivot:

Dr. Sami Hamid leaves Minopolis AG: 07.05.2019 (SHAB)

Minopolis AG is liquidated: 25.06.2019

Interval: 49 days → Hamid left the ship before it sank.

---

## Assembling the Flag

Component 1: Pinfarina_AG — original name of the AG

Component 2: 34 — OKFS of Agat Group = foreign element

Component 3: Hamid — surname of President 2009-2019

Component 4: Ward_Howell — company with Moscow office

---

Flag - `KubSTU{Pinfarina_AG:34:Hamid:Ward_Howell}`


