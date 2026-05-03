# [osint] Minute of fame

> **Category:** `osint`  
> **CTF:** KubSTU CTF 2026 Spring

Difficulty: low


Our university's team appeared on regional TV this year, but I forgot where and when the segment was published. Help me find it. Flag format - `KubSTU{TVChannelName_ReleaseDate}`

---

### Step 0. Preparing for the Search

Let's start by carefully reading the problem statement. It contains two important clues:

- the segment was **this year** → we're only interested in **2026**
- the segment aired on **regional TV**


At this stage, the search scope is already significantly narrowed. All that's left is to figure out *where exactly* such things usually surface.

---

### Step 1. Where Does the University Brag About Itself?

Experience tells us: if a university makes it onto TV, it will definitely brag about it. Not just anywhere, but on its official social media. So without overthinking, we take the proven route:

- Telegram: <https://t.me/kubstu_official>
- VK: <https://vk.com/kubstu_official>


Both options work, but Telegram usually reacts faster — let's start there.

---

### Step 2. Some Purposeful Searching

Scrolling through the entire year's feed is a questionable idea. Let's use channel search and try keywords logically associated with TV segments:

- `students`
- `team`
- `information security`
- `cybersecurity`

A couple of minutes in, familiar posts start popping up about the **Capybaras** team and their participation in an international CTF. Among them — news about **2nd place**, interviews, and importantly, posts with media files.

---

### Step 3. That Very Post

One post immediately stands out: it has an attached **video**, not just a photo or text. This is the recording of the TV segment.


We open the video and watch carefully:

- in the corner of the screen, the channel name is clearly visible — **"Russia 1 Kuban"**
- the video duration is 1:02, which roughly corresponds to the challenge name + the air date is confirmed via smotrim.ru

  

Regional channels rarely make their social media managers wait, so everything here is straightforward with no tricks.

---

### Step 4. Assembling the Flag

Now we have everything we need:

- **ChannelName:** `Russia1Kuban`
- **ReleaseDate:** `19.01.2026`


We construct the flag in the required format - `KubSTU{Russia1Kuban_19.01.2026}`