# [web] The Battle of the Strongest

> **Category:** `web`  
> **CTF:** KubSTU CTF 2026 Spring

---

## Legend

  

Every semester, capybara students argue about which faculty is better, who's stronger academically, who's more active in student life.

This year, enthusiast capybaras decided to take the rivalry digital and created an innovative service **"The Battle of the Strongest"**. But it seems like the service isn't the most secure one.


Challenge files

[The_Battle_of_the_Strongest.rar](./files/The_Battle_of_the_Strongest.rar)

---

We go to the service and register.

We're taken to the main page.


 ![img_1.png](./images/img_1.png)


The point of the challenge is that several teams log in and can choose the number of likes that will be at the end of the round.


 ![img_2.png](./images/img_2.png)

I set 12.

We navigate and see 0.


 ![img_3.png](./images/img_3.png)

If we click like:


 ![img_4.png](./images/img_4.png)

The button turns red.

If we click remove, it becomes -1.

Okay. Let's catch the request.


 ![img_5.png](./images/img_5.png)


We notice that if we send it a second time — the server accepts it. The check is only on the client side.


 ![img_6.png](./images/img_6.png)


We spam until the desired number — which is 12 for us.


 ![img_7.png](./images/img_7.png)


We overshot — let's try to decrease.


 ![img_8.png](./images/img_8.png)

Let's try.


 ![img_9.png](./images/img_9.png)

And we get 12.


 ![img_10.png](./images/img_10.png)

We wait for the time to expire and make sure the number of likes stays at the desired amount. 

In practice, at the beginning of the CTF there will naturally be competition, and logic and good botnets will win.


 ![img_11.png](./images/img_11.png)

We go to the profile page.


 ![img_12.png](./images/img_12.png)

---

```javascript
KubSTU(Y0u_ar3_champ10n)
```


