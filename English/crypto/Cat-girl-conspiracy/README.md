# [crypto] Cat-girl conspiracy

> **Category:** `crypto`  
> **CTF:** KubSTU CTF 2026 Spring

<details>
<summary>📎 Challenge files</summary>

| File | Type |
|------|-----|
| [solve.py](./files/img_2.py) | `text/x-python` |
| [solve.py](./files/img_4.py) | `text/x-python` |
| [64_what_could_this_mean.zip](./files/img_9.zip) | `application/x-zip-compressed` |

</details>

---

Hey, this is a strange archive, and the name is weird too?? Figure this out as soon as you can, please. Flag format KUBSTU{}

Solution: An archive with a bunch of folders and a single text file. By the way, if you look at the names of the archive and the text file, you'll notice they're almost identical — the difference is the number 64 (let's remember that). Let's open it.

What to do with this is unclear for now. Possibly these are just hashes concatenated together. Note the archive name — it contains the number 64, so let's try splitting the text into blocks of 64 characters.

Now let's look at the folders and their contents. There are tons of images and each one has its own hash. Plus, we notice these images are stored in folders with distinctive names. Let's write a script that finds images by the hashes we obtained and checks which folder each image comes from. Let's look at the script output:

Flag: KUBSTU{A7_LE4ST_N0W_Y0U_H4V3_A_BUNCH_0F_P1CTUR3S_OF_C4T_GIRL5}
