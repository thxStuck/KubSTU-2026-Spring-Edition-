# [crypto] Not enough part 2

> **Category:** `crypto`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [output.txt](./files/img_2.txt) | `text/plain` |
| [solve.sage](./files/img_3.sage) | `sage` |
| [solve.py](./files/img_5.py) | `text/x-python` |
| [output.txt](./files/img_10.txt) | `text/plain` |
| [solve.sage](./files/img_12.sage) | `sage` |
| [output.txt](./files/img_15.txt) | `text/plain` |

</details>

---

During an emergency system recovery, only fragments of two ***-keys were saved. From each prime number, only the high bits survived, and the low bits were ??????. After recovering the private parameters, a master secret was formed from them, which was then converted via KDF into a key for something. Flag format KubSTU{} Hint 1: Look more carefully — maybe something else survived.

So this is the second part of the challenge. We immediately read the description and compare it with the first part. We realize this is a harder version of RSA+AES-GCM (confirmation of this specific mode is also found in the description: g-recovery, c-only, m-through). Let's look at the text file — it contains all the data we need to start the recovery (the number of lost bits is hidden in sys info — it's 72 for the first and 80 for the second).

We write a Sage script that recovers p1 and p2 using Coppersmith's method.

Then, knowing p1 and p2, we find q, phi, and d. After that we try to assemble the key for AES-GCM, knowing how it's constructed (by the way, here's another hint — we might need to refer back to part one again^^).

Now, knowing everything, we write the final script.

The challenge is a bit harder than the first part, but still solvable.

Flag: KubSTU{1_h0p3_y0u_solv3d_7hi5_p4rt2_th1s_1s_much_h4rd3r}
