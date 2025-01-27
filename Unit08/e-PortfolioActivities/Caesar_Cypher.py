import os

def caesar_cipher_encrypt(text, shift):
    """
    Encrypts text using Caesar Cipher with a given shift.
    :param text: The plain text to encrypt.
    :param shift: Number of positions to shift the alphabet.
    :return: Encrypted text.
    """
    encrypted_text = ""
    for char in text:
        if char.isalpha():
            start = ord('A') if char.isupper() else ord('a')
            encrypted_text += chr((ord(char) - start + shift) % 26 + start)
        else:
            encrypted_text += char
    return encrypted_text


def encrypt_file(input_file, output_file, shift):
    """
    Encrypts the contents of a file and saves the encrypted version.
    :param input_file: Path to the input text file.
    :param output_file: Path to save the encrypted file.
    :param shift: Shift value for Caesar Cipher.
    """
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return
    
    with open(input_file, 'r') as file:
        plaintext = file.read()
    
    encrypted_text = caesar_cipher_encrypt(plaintext, shift)
    
    with open(output_file, 'w') as file:
        file.write(encrypted_text)
    
    print(f"Encrypted text saved to {output_file}")


# Example usage
if __name__ == "__main__":
    print("Caesar Cipher Encryption")
    
    # Encrypt user-provided text
    sample_text = input("Enter the text to encrypt: ")
    shift_value = int(input("Enter the shift value (integer): "))
    encrypted = caesar_cipher_encrypt(sample_text, shift_value)
    print(f"Encrypted Text: {encrypted}")
    
    # Encrypt a file
    input_path = "sample.txt"  # Replace with your text file path
    output_path = "encrypted_sample.txt"  # Output file
    encrypt_file(input_path, output_path, shift_value)
