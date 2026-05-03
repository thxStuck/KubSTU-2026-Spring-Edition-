import string


def find_inverse(a, m):
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None


def solve_cipher(ciphertext):
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
    char_map = {ch: i for i, ch in enumerate(alphabet)}
    num_map = {i: ch for i, ch in enumerate(alphabet)}

    inv_13 = find_inverse(13, 62)
    inv_17 = find_inverse(17, 62)
    inv_19 = find_inverse(19, 62)

    known_part = "KubSTU("
    key_values = [None, None, None]

    for i in range(min(len(known_part), len(ciphertext))):
        if ciphertext[i] in '()_':
            continue

        known_char = known_part[i]
        if known_char not in char_map:
            continue

        known_num = char_map[known_char]
        enc_num = char_map[ciphertext[i]]

        for key_val in range(62):
            if i % 3 == 0:
                test = (known_num * 13 + key_val * 7) % 62
                if test == enc_num:
                    key_values[0] = key_val
                    break
            elif i % 3 == 1:
                test = (known_num * 17 + key_val * 3 + 11) % 62
                if test == enc_num:
                    key_values[1] = key_val
                    break
            else:
                test = (known_num * 19 + (key_val ^ 42) + 23) % 62
                if test == enc_num:
                    key_values[2] = key_val
                    break

    result = []
    for i, char in enumerate(ciphertext):
        if char in '()_':
            result.append(char)
        elif char in char_map:
            enc_num = char_map[char]
            key_val = key_values[i % 3]

            if i % 3 == 0:
                orig = ((enc_num - key_val * 7) * inv_13) % 62
            elif i % 3 == 1:
                orig = ((enc_num - key_val * 3 - 11) * inv_17) % 62
            else:
                orig = ((enc_num - (key_val ^ 42) - 23) * inv_19) % 62

            result.append(num_map[orig])
        else:
            result.append(char)

    return ''.join(result)


encrypted_flag = "XiEDJ5(9tV_qY3_v43_t9B3_o9vo_ESM_YR_YA_t_S5t8v_XYL4jt)"
flag = solve_cipher(encrypted_flag)
print(f"Флаг: {flag}")