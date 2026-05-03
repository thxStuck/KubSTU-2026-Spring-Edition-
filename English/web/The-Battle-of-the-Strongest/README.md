# [web] The Battle of the Strongest

> **Category:** `web`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [The_Battle_of_the_Strongest.rar](./files/img_1.rar) | `application/x-compressed` |

</details>

---

Lore:

Every semester, capybara students argue about which faculty is better, who's stronger in academics, who's more active in student life.

This year, enthusiast capybaras decided to take the rivalry digital and created an innovative service **"The Battle of the Strongest"**. Only it seems like it's not the most secure service.

Challenge files:
We go to the service and register. We get transferred to the main page.

![image.png](./images/img_2.png)

The challenge is that several teams join and can choose the number of likes that will be counted at the end of the round.

I set 12.
We go and see 0.

If we press like:

and the button turns red.
If we press to remove — it goes to -1.
OK. Let's catch the request.

![image.png](./images/img_3.png)

We notice that if we send it a second time — the server accepts it. The check is only on the client side.

![image.png](./images/img_4.png)

We spam until we reach the needed number, which is 12.

![image.png](./images/img_5.png)

We overdid it, try to decrease.

We try.

And we get 12.

We wait for the time to end and make sure the like count stays at the required number. In practice, at the start of the CTF there will naturally be competition, and logic and good botnets will win.

We go to our profile.

KubSTU(Y0u_ar3_champ10n)
