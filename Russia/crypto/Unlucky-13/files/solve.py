import hashlib

n = 13658633037131788032351618427072247476717954542396408633560773884364554559070511401338131167308785959562652843354491812218130569318378376258845006015571936307529619165627684367938035500689095197148634390329808425228615805061358885887601807910577877331466810636357076781023936730357996997258012513541846157478488478454563307821991031194437503266795021183758263745762989760240683361817082008819321416765453826690538816962208131444601183340450621147225799934380535423737829891317625290259915071423282523846993193854126576514135696151799274710837198613476445017109884172011540789567531049972285279517155764888481047450059
e = 3
c = 58106402945252412885867908042116794819464305744971899578073020304067543548070807457178658563488157040731309267600804875202490191851964629071348907183348604959890636799938893288492152226256276862912678404321252232876509325092153164813635360471085498336853220078206620458027876601442698309483452313201963351276803179820555434275959791505894082437152805771101360567738286600728

def integer_cube_root(n):

    if n < 0:
        return -integer_cube_root(-n)
    if n == 0:
        return 0
    x = n
    y = (2 * x + n // (x * x)) // 3
    while y < x:
        x = y
        y = (2 * x + n // (x * x)) // 3
    return x

m = integer_cube_root(c)


assert m ** 3 == c, "Кубический корень не точный! Возможно, m^3 >= n и нужен другой подход."
print(f"[+] RSA cube root attack successful")
print(f"    m^3 == c: {m**3 == c}")


layer2 = m.to_bytes((m.bit_length() + 7) // 8, "big")
print(f"    layer2 (hex): {layer2.hex()}")


def rc4(key, data):
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    out = []
    for byte in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(byte ^ S[(S[i] + S[j]) % 256])
    return bytes(out)

secret = b"Unlucky" + str(13).encode()
rc4_key = hashlib.sha256(secret).digest()[:16]

layer1 = rc4(rc4_key, layer2)
print(f"\n[+] RC4 decryption done")
print(f"    key: sha256({secret})[:16] = {rc4_key.hex()}")
print(f"    layer1 (hex): {layer1.hex()}")


def cursed_prng(seed, length):
    state = seed
    stream = []
    for _ in range(length):
        state = (state * 1313 + 131313) % (2**32)
        stream.append(state & 0xFF)
    return bytes(stream)

keystream = cursed_prng(13, len(layer1))
flag = bytes(a ^ b for a, b in zip(layer1, keystream))

print(f"\n[+] XOR decryption done")
print(f"    keystream seed: 13")
print(f"\n{'='*50}")
print(f"  FLAG: {flag.decode()}")
print(f"{'='*50}")

