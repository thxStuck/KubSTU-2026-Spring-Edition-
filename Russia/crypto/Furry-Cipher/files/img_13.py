import string


def encrypt_custom(plaintext, key_values):
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
    char_map = {ch: i for i, ch in enumerate(alphabet)}
    num_map = {i: ch for i, ch in enumerate(alphabet)}

    result = []

    for i, char in enumerate(plaintext):
        if char in '()_':
            result.append(char)
        elif char in char_map:
            num = char_map[char]
            key_val = key_values[i % 3]

            if i % 3 == 0:
                encrypted = (num * 13 + key_val * 7) % 62
            elif i % 3 == 1:
                encrypted = (num * 17 + key_val * 3 + 11) % 62
            else:
                encrypted = (num * 19 + (key_val ^ 42) + 23) % 62

            result.append(num_map[encrypted])
        else:
            result.append(char)

    return ''.join(result)



if __name__ == "__main__":
    example_text = "Test123"
    example_key = [1, 2, 3]
    encrypted_example = encrypt_custom(example_text, example_key)
    print(f"'{example_text}' -> '{encrypted_example}'")