# [forensics] Vanilla raw

> **Category:** `forensics`  
> **CTF:** KubSTU CTF 2026 Spring

---

We received a RAM dump, but for some reason we can't analyze it — help us out.

[memory.rar](./files/memory.rar)

Strings analysis gives us nothing. Grep by pattern also yields nothing. Although the dump is 2 GB, so there must be something in there.
When analyzing entropy and the hex dump, we see:


 ![img_1.png](./images/img_1.png)



 ![img_2.png](./images/img_2.png)

We conclude that most of the memory is zeros, but there are non-zero values. Let's find their positions. We craft a script that will trigger on the first non-zero byte.


 ![img_3.png](./images/img_3.png)

Let's examine the surrounding area.

 ![img_4.png](./images/img_4.png)

At first glance this doesn't give us anything, but we can notice a possible 4-byte offset. We know the pattern KubSTU{…}. Searching by pattern apparently doesn't make sense, so we need to look character by character. Let's look for the character K.

 ![img_5.png](./images/img_5.png)

We see that this character is present at several offsets. Let's examine all of them, and at a certain offset the flag pattern starts to emerge.

 ![img_6.png](./images/img_6.png)

Let's create a script that will fully extract the flag.


 ![img_7.png](./images/img_7.png)

Flag: 

```javascript
KubSTU{m3m0ry_unl1nk3d_tmpfs_f0r3ns1cs}
```


