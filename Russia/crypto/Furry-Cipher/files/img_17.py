import string


def encrypt_custom(text):
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
    char_map = {ch: i for i, ch in enumerate(alphabet)}
    num_map = {i: ch for i, ch in enumerate(alphabet)}

    result = []
    for char in text:
        if char in '()_':
            result.append(char)
        elif char in char_map:
            num = char_map[char]
            encrypted_num = (num * 13 + 7) % 62
            result.append(num_map[encrypted_num])
        else:
            result.append(char)

    return ''.join(result)


def decrypt_custom(text):
    inverse = 29

    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
    char_map = {ch: i for i, ch in enumerate(alphabet)}
    num_map = {i: ch for i, ch in enumerate(alphabet)}

    result = []
    for char in text:
        if char in '()_':
            result.append(char)
        elif char in char_map:
            enc_num = char_map[char]
            original_num = ((enc_num - 7) * inverse) % 62
            result.append(num_map[original_num])
        else:
            result.append(char)

    return ''.join(result)