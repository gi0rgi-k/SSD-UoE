import string

def encode_decode():
    """
    Encode or decode a string using a Caesar cipher.

    The user is prompted to choose between encoding or decoding a string,
    then provide the string input. A shift value of 3 is used for the operation.
    """
    shift = 3
    choice = input("Would you like to encode or decode? ").strip().lower()
    word = input("Please enter text: ").strip()

    # Validate choice
    if choice not in {"encode", "decode"}:
        print("Invalid choice. Please enter 'encode' or 'decode'.")
        return

    encoded = ''
    letters = string.ascii_letters + string.punctuation + string.digits

    # Encode or decode based on choice
    for letter in word:
        if letter == ' ':
            encoded += ' '
        elif letter in letters:
            if choice == "encode":
                encoded += letters[(letters.index(letter) + shift) % len(letters)]
            elif choice == "decode":
                encoded += letters[(letters.index(letter) - shift) % len(letters)]
        else:
            print(f"Skipping invalid character: {letter}")

    print(f"Result: {encoded}")


if __name__ == "__main__":
    encode_decode()
