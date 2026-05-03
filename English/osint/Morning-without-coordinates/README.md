# [osint] Morning without coordinates

> **Category:** `osint`  
> **CTF:** KubSTU CTF 2026 Spring

---

Difficulty: medium

Exams are over — a rare moment when you can breathe. In the evening we decided to celebrate finishing exams and, as often happens, slightly overestimated our abilities.

In the morning, it turned out that one of our group went missing. The last thing everyone remembers is that we were somewhere on Krasnoarmeyskaya street. After that — a blackout.

In the afternoon, the missing person gets in touch and sends a photo with a message:
"Seems like everything's fine. Smells like the sea, no idea where I am. Send me money, I'll try to get home."

The phone is on its last breath, GPS is jammed, and everyone's head is still heavy.

All hope rests on you — the only one who kept a clear head. Determine the city and exact address where the photo was taken.

Flag format — KubSTU{CityName_StreetName_BuildingNumber}

Determining the search area:
We start with the simplest thing — carefully look at the photo and recall the context from the story.
According to the legend, we're still in Krasnodar Krai, plus the missing person's message contains a big hint:
"Smells like the sea"
And mountains are clearly visible in the background of the photo. In Krasnodar Krai, this significantly narrows the search area: mountains + sea = coastline.
Effectively, only the strip from Sochi to Novorossiysk remains.

Finding the city:
Next, we move to the details in the image itself. In the background, a large building with distinctive architecture and a sign is clearly visible — it looks like a bus station. This is already an excellent lead, because:
- there aren't that many bus stations,
- they often have photos in open sources.

We try a simple and logical approach: pick the largest cities and google queries like "bus station <city>" and look at the images.
On the query "bus station Gelendzhik", we quickly find a building that fully matches what's in the photo: the shape, number of floors, facade — everything is a perfect match.

The missing person is found:
Now that the city is identified, all that's left is to determine the exact shooting location.
We open maps, find Gelendzhik's bus station, and enable street view. Then — a bit of patience: we look around, move along the road, check bus stops and viewing angles.
Eventually, the spot is found:
- the bus stop opposite the bus station,
- the angle matches the photo,
- the position of buildings and the road align.

Hooray, the finale!

## 🚩 Flag

```
KubSTU{Gelendzhik_Obezdnaya_3}
```
