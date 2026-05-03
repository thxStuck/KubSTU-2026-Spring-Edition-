# [forensics] We have an incident!

> **Category:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [We have an incident.rar](./files/img_2.rar) | `rar` |
| [We have an incident.rar](./files/img_3.rar) | `rar` |

</details>

---

It seems our company had an incident. Nothing is clear yet — we've isolated certain machines to be safe. The response team is working closely with malware analysts. To make their job easier, you need to provide them with the malware you should find. There are also suspicions that data exfiltration occurred. Find out what happened.

Flag format KubSTU{Vulnerability/attack that led to privilege escalation:List of malware including extensions:Exfiltrated data}
Note: List items in order of their launch timestamps (case-sensitive), from earliest to latest. Same for exfiltration.
Example: KubSTU{polkit:PwnKit.exe_revershell.exe_WannaCry.exe:Конфданные.doc:users.db}

Solution:
We have collected artifacts from machines — from each machine we're given artifacts (MFT, Amcache, prefetch, event logs, etc.).

We begin the analysis. We have no information about what happened, when, or why. Let's examine the MFT (there are many paths you can take — your choice).

Throughout the process I'll be using Eric Zimmerman's toolset. We parse the raw MFT, save to CSV, and read it.

We'll see a lot of rows, among which there may be something useful. The MFT file itself is a table containing information about all files on the system, including hidden files, their extensions, as well as modification/creation/access timestamps and so on.

We have the HR machine, so we can assume that work was mostly done with documents. The MFT also has a file extension field.

You can iterate through extensions that might clearly hint that something is off.

The file Резюме.docm has an extension indicating it may contain macros. The directory tells us the file was probably downloaded — but was it actually opened? Let's check.

Whether it was launched can be verified by examining prefetch files. They're created to optimize system performance and contain paths to used resources, as well as a list of files they interacted with. We parse it and see that it was indeed launched.

Let's see what appeared after it in the MFT. Quite a few interesting things show up:

Certify.exe — a tool designed for finding and exploiting misconfigurations in Active Directory Certificate Services (AD CS).
Rubeus.exe — a tool for working with Kerberos and abusing it.

Next we see text files — apparently collected system information as initial reconnaissance.

And what else? Let's see what happened. It's unlikely that this was the full extent of the phishing file's functionality — let's check the event logs (HR\C\Windows\System32\winevt\logs). By the way, if you've already seen Mimikatz in the prefetch at this point, good. It will appear in the MFT a bit further down.

In the Security log you can see these events:

![image.png](./images/img_1.png)

Logon type 3 — network. Account name: HR. Let's assume the attacker gained access. But we need more details. We have event timestamps, file appearance timestamps, and evidence of their execution — let's examine the Windows PowerShell logs. We see an interesting detail: certain PS commands were executed. This file is what enables the attacker to establish a reverse shell. We also have the attacker's IP.

![image.png](./images/img_4.png)

There's data about loading Mimikatz; further on we'll see events from its execution. Let's look even further.

Next you can see the exfiltration of keys extracted using Mimikatz.
Note that Mimikatz was not responsible for privilege escalation — the attempt was made but unsuccessful. However, before the Mimikatz events, you can find Certify at work. It extracted a private key and a vulnerable certificate VulnerableUserSAN by trying to insert a name into the request. The name ends up being substituted in the request. The command:
.\Certify.exe request /ca:DC1.kuban.loc\kuban-DC1-CA /template:VulnerableUserSAN /altname:admin /subject:"CN=admin, CN=Users, DC=kuban, DC=loc"

Then the attacker likely copied the data, generated their own key, transferred it to the machine, and implanted it using Rubeus. This is visible in a couple of events above. The command:
.\Rubeus.exe asktgt /user:admin /certificate:C:\Users\Public\admin.pfx /password:"" /nowrap /ptt"

![image.png](./images/img_5.png)

We see the implantation was successful, meaning the attacker achieved privilege escalation. This attack is ESC1. Let's look further. We see an exfiltration attempt, but it's unsuccessful.

Here's something interesting — an unknown utility. It's actually a Sliver C2 implant.

Later you can see this file was moved to another directory.

That's everything on this machine.
Now let's examine the DC machine. This is the domain controller. We review the PowerShell logs.

We see a reverse shell to the attacker's IP. Then there's something interesting:
Copying the AD database. There's also copying of SYSTEM files.
A bit further we see exfiltration of the already copied files. Only ntds.dit was exfiltrated.

We compose our flag according to the format:

KubSTU{ESC1:Резюме.docm_Certify.exe_Rubeus.exe_mimikatz.exe_wlmss.exe:0-40e10000-admin@krbtgt~kuban.loc-KUBAN.LOC.kirbi_ntds.dit}
