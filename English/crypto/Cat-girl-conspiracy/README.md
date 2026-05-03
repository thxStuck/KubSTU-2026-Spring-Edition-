# [crypto] Cat-girl conspiracy

> **Category:** `crypto`  
> **CTF:** KubSTU CTF 2026 Spring

---

Hey, this is a strange archive, and what's with that weird name??
Figure this out as soon as you can, please.
Flag format KUBSTU{}

[64_what_could_this_mean.zip](./files/64_what_could_this_mean.zip)

---

Solution:
An archive with a bunch of folders and a single text file.
By the way, if you look at the names of the archive and the text file, you'll notice they're almost identical — the difference is the number 64 (let's remember that).

Let's open it.

 ![img_1.png](./images/img_1.png)

It's not clear what to do with this yet.
These might be hashes simply concatenated together.
Let's pay attention to the archive name — it contains the number 64, so let's try splitting this text into 64-character blocks.

 ![img_2.png](./images/img_2.png)


 ![img_3.png](./images/img_3.png)

 ![img_4.png](./images/img_4.png)


Now let's look at the folders and their contents.
There are lots of images, each with its own hash, and we notice that these images are stored in folders with specific names.

Let's try writing a script that finds images by the hashes we obtained and checks which folder each image comes from.

[solve.py](./files/solve.py)

Let's look at the script output:


 ![img_5.png](./images/img_5.png)


Flag: KUBSTU{A7_LE4ST_N0W_Y0U_H4V3_A_BUNCH_0F_P1CTUR3S_OF_C4T_GIRL5}


