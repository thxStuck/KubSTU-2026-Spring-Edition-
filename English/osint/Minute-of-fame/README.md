# [osint] Minute of fame

> **Category:** `osint`  
> **CTF:** KubSTU CTF 2026 Spring

---

Difficulty: low

Our university's team was featured on regional TV this year, but I forgot where and when the segment was published. Help me find it. Flag format — KubSTU{TVChannelName_ReleaseDate}

## Step 0. Preparing for the search

Let's start by carefully reading the challenge. It contains two important clues:
- the segment was this year → we're only interested in 2026
- the segment aired on regional TV

At this stage, the search scope is already significantly narrowed. Now we need to figure out where such things usually surface.

## Step 1. Where does the university brag about itself?

Experience suggests: if a university gets on TV — it will definitely brag about it. And not just anywhere, but on its official social media. So we don't think too long and go the proven route:
Telegram: https://t.me/kubstu_official
VK: https://vk.com/kubstu_official

Both options work, but Telegram usually reacts faster — let's start there.

## Step 2. Some intelligent searching

Scrolling through the entire feed for the year is a dubious idea. We use the channel search and try keywords logically related to TV segments:
- students
- team
- information security
- cybersecurity

A couple of minutes — and familiar posts about the Capybaras team and their participation in an international CTF start appearing. Among them — news about 2nd place, interviews, and importantly, posts with media files.

## Step 3. That one post

One post immediately stands out: it has a video attached, not just a photo or text. This is the recording of the TV segment.

We open the video and watch carefully:
- in the corner of the screen, the channel name is clearly visible — "Russia 1 Kuban"
- video length is 1:02, which roughly matches the challenge name + the air date is confirmed via smotrim.ru

Regional channels rarely make their SMM managers wait, so everything here is fair and straightforward.

## Step 4. Assembling the flag

Now we have everything we need:
ChannelName: Russia1Kuban
ReleaseDate: 19.01.2026

We compose the flag in the required format — KubSTU{Russia1Kuban_19.01.2026}
