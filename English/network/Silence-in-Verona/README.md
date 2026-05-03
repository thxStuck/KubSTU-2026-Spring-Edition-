# [network] Silence in Verona

> **Category:** `network`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [3 in 1 .pkt](./files/img_1.pkt) | `pkt` |

</details>

---

You are a senior network engineer. The chief network architect has left the company, leaving the DD LAB infrastructure in lockdown mode. Before departing, he split the Master Recovery Key into three fragments and hid them within the network itself: in port logic, in workstation system logs, and in visual topology artifacts. The former architect was quite an eccentric person — colleagues often called him a geek — but as a specialist he was damn good.

Your task is to perform an audit, collect all key parts, and restore access to the core before the system goes into full reset. Get to work.

Writeup:
1. Search all text files on the computers.
2. You'll find a file called BorringNovel.txt. It's actually code in the esoteric programming language SPL (Shakespeare Programming Language).
3. Paste the code into any suitable compiler and get the flag KubSTU(Mellin_The_Hunter).
