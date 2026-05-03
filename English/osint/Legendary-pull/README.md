# [osint] Legendary pull

> **Category:** `osint`  
> **CTF:** KubSTU CTF 2026 Spring

Difficulty: hard


I have too many questions about this situation and no answers. Find the message of the Kuban tourist.

 ![img_1.png](./images/img_1.png)

---

### 1. Initial Visual Analysis

 

First, we analyze the photo itself:

- house architecture,
- neat fences and landscaping,
- road markings,
- style of urban infrastructure,
- appearance of the bus stop.

 

Based on the combination of features, the location looks **not like Krasnodar** and generally **not like Russia**.
 This immediately suggests that the sticker with Khadyzhenskoe beer is **not an indication of the country**, but simply a meme.

 

The most noticeable clue in the photo is precisely the round **"Khadyzhenskoe"** sticker.

 

---

### 2. Determining the Likely Country of the Photo

 

To avoid guessing blindly, you can:

- upload the photo to a visual neural network / image recognition,
- use reverse image / visual search,
- ask a model to determine the most likely country based on architecture and infrastructure.


*The prompt I used: "find all possible geo-references and determine the country/city where the photo was taken"*


The most plausible result is **Italy**.

 

So now we have **two main clues**:

1. **Khadyzhenskoe beer**
2. **Italy** as the likely country of the photo

 

---

### 3. Analyzing the Challenge Title

 

The task name is **Mythical Pull**.

 

This is a reference to the popular meme/Reels format called **"Reel Pull"**, where "pull" means "rare find", "unexpected catch", "weird drop", often featuring absurd or very niche content.

 

In other words, the hint here isn't just about geolocating a photo, but that **this is a frame from a Reel** that can be found by association.

 

---

### 4. Keyword Search

 

Next, we start searching not for the street itself, but for **content** related to this phenomenon.

Useful queries:

- Хадыженское Италия
- Хадыжи Италия
- Хадыженское в Италии
- Khadyzhenskoe Italy
- Khadyzhenskoe beer Italy
- Hadizhenskoe Italy meme
- Italian bus stop Khadyzhenskoe

 

It makes sense to search:

- on Google,
- on Instagram,
- on TikTok,
- in both English and Russian variants.

 

---

### 5. Finding the Original Video

 

If the search is done correctly, it leads to Instagram Reels:

**Source:**
 https://www.instagram.com/reel/DV9U0fZkSnG/

[uploads/6d8404be-e3e6-431d-bbd2-9cbb195bd0f8/ce980d6e-0a1f-463c-bf22-35919e59d65a/Passo%20Campalto%20Orlanda_%D0%A5%D0%B0%D0%B4%D1%8B%D0%B6%D0%B8%20_%D0%98.mp4](video:uploads/6d8404be-e3e6-431d-bbd2-9cbb195bd0f8/ce980d6e-0a1f-463c-bf22-35919e59d65a/Passo%20Campalto%20Orlanda_%D0%A5%D0%B0%D0%B4%D1%8B%D0%B6%D0%B8%20_%D0%98.mp4 "05d858ae5f56:video/mp4:1:")

In this video, the author shows the very same location and explains **where the pole with the sticker is located**.

 

---

### 6. Pinpointing the Exact Location

 

From the video, we get the location:

**Bus stop Passo Campalto Orlanda**

 

Next:

1. open it on the map,
2. compare the surroundings with the photo,
3. confirm that:
   - the pole shape matches,
   - there's a bus shelter nearby,
   - the road surroundings and buildings visually match.

 

---

### 7. Getting the Flag

 

After confirming the location, we go further:

- open the **stop / POI** on maps,
- check **comments / reviews / photos**,
- there we find the **flag**.

  

 ![img_2.png](./images/img_2.png)


Format per the problem statement:

`KubSTU{Dr1nk_r35p0n51bly_t0_4v01d_w4k1n_up_4br04d}`


  


