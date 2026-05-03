import string


def solve_cipher(ciphertext):
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
    char_to_num = {ch: i for i, ch in enumerate(alphabet)}
    num_to_char = {i: ch for i, ch in enumerate(alphabet)}

    # Находим обратное к 13 по модулю 62
    for inv in range(62):
        if (13 * inv) % 62 == 1:
            inverse = inv
            break

    result = []
    for char in ciphertext:
        if char in '()_':
            result.append(char)
        elif char in char_to_num:
            enc_num = char_to_num[char]
            orig_num = ((enc_num - 7) * inverse) % 62
            result.append(num_to_char[orig_num])
        else:
            result.append(char)

    return ''.join(result)


# Зашифрованный флаг (полученный из первого скрипта)
encrypted_flag = "Nvw3GT(CBL_MOM_lfv_IZ1M_eCje_wIB_Oi_OV_j_mvIIl_9OsCZI)"
decrypted_flag = solve_cipher(encrypted_flag)
print(f"Флаг: {decrypted_flag}")