# [stego] bembembem

> **Category:** `stego`  
> **CTF:** KubSTU CTF 2026 Spring

---

Difficulty: hard
There's definitely a flag here, but you'll have to go through Murino, Molochnoe, and possibly encounter a cat-bone.

## Step 0 — reconnaissance

file bembembem.mp4
ffprobe -v error -show_format -show_streams bembembem.mp4
exiftool bembembem.mp4
strings bembembem.mp4 | grep -iE 'BEM|b3m|flag'
In exiftool/ffprobe, suspicious TikTok tags are immediately noticeable: aigc_info, comment=vid:..., vid_md5=6899efc8f52bffb08c5ac45deee24f64. Noted for now.

## Step 1 — find the custom uuid box

A standard MP4 consists of ftyp, moov, mdat, etc. Any additional uuid atom is a red flag. We parse top-level boxes:
# mp4_walk.py
import struct, sys

![image.png](./images/img_1.png)

def walk(path: str) -> None:
    with open(path, "rb") as f:
        data = f.read()
    total = len(data)
    print(f"file size: {total}")
    print(f"{'offset':>12} {'size':>12}  type")

    pos = 0
    while pos < total:
        if total - pos < 8:
            print(f"  !! trailing {total - pos} bytes at {pos}")
            break
        size  = struct.unpack(">I", data[pos:pos + 4])[0]
        btype = data[pos + 4:pos + 8].decode("ascii", errors="replace")
        if size == 1:
            size = struct.unpack(">Q", data[pos + 8:pos + 16])[0]
        elif size == 0:
            size = total - pos
        print(f"{pos:>12} {size:>12}  {btype}")

        if size <= 0 or pos + size > total:
            print(f"  !! invalid box at {pos}, stopping walk")
            break
        pos += size

![image.png](./images/img_2.png)

if __name__ == "__main__":
    walk(sys.argv[1] if len(sys.argv) > 1 else "bembembem.mp4")

Result:
0          32           b'ftyp'
32         3884477      b'moov'
3884509    8            b'free'
3884517    264587170    b'mdat'
268471687  970          b'uuid'      ← there it is
268472657  ...          junk (not a box)
We read the uuid box contents: 16-byte UUID + payload. The UUID is recognizable: b3eb3eb3eb3eb3eb3eb3eb3eb3eb3eb3 (author's signature).
The payload starts with BEM/v1\n# decode: base64 -> zlib inflate -> utf-8\n — the format is documented in the first line.
import base64, zlib
payload = data[268471687 + 8 + 16 : 268471687 + 970]
lines = payload.strip().split(b"\n")
b64 = b"".join(l for l in lines[1:] if not l.startswith(b"#"))
riddle = zlib.decompress(base64.b64decode(b64)).decode("utf-8")
print(riddle)
We get a riddle in Russian, three stanzas:
I. Listen not with ears — see with the colors of sound (normalcy).
   The forty-second minute, above ten thousand (oh-my-god-ness).
   What the whisper draws in the spectrum — that is the code word.
   (Case matters, exactly 8 characters.)
II. This MP4 has a long tail. The tail is sealed —
   beyond the last atom lies cargo, XORed
   with a repeating key. The key is already in the file's
   metadata, the beast wears it on its forehead: vid_md5 in hex
   (32 ASCII characters).
III. Under the seal — an old chest in PK format.
    Unlock it with what the spectrum whispered.
    Inside: grapes, plums, apples on green, bananas.

## Step 2 — spectrogram at the 42nd minute

ffmpeg -ss 2520 -i bembembem.mp4 -t 4 -vn -ac 1 probe.wav
sox probe.wav -n spectrogram -o spec.png -x 1400 -y 500
We open spec.png — in the ~10.5–14.5 kHz range we can read K0t05t (also visible in Sonic Visualiser / Audacity).
Password found: K0t05t.

## Step 3 — XOR key from metadata

ffprobe -v error -show_entries format_tags=vid_md5 \
  -of default=nk=1:nw=1 bembembem.mp4
# 6899efc8f52bffb08c5ac45deee24f64
The value as an ASCII string (32 characters) — this is the XOR key.

## Step 4 — extract and decrypt the tail

The file tail starts right after the uuid box, at offset 268472657:
KEY = b"6899efc8f52bffb08c5ac45deee24f64"
tail = data[268472657:]
plain = bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(tail))
open("recovered.zip","wb").write(plain)
Check: plain[:4] == b'PK\\x03\\x04' — that's ZIP magic. Excellent.
Alternative approach without knowing the exact offset: sliding window XOR with the key + searching for the PK\\x03\\x04 signature in the decoded buffer. binwalk won't find the ZIP without decryption because XOR breaks the magic — that's the penalty for skipping layer 3.

## Step 5 — open the archive

unzip -P K0t05t recovered.zip
cat flag.txt
# KubSTU{3nj0y_1h_0f_M3ll57r0y_m3m3s}

## 🚩 Flag

```
KubSTU{3nj0y_1h_0f_M3ll57r0y_m3m3s}
```
