import binascii
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def hex_to_bytes(hexstr):
    """Convert hex string to bytes"""
    return binascii.unhexlify(hexstr)

def pad(data):
    """PKCS7 padding"""
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len] * pad_len)

def unpad(data):
    """Remove PKCS7 padding"""
    pad_len = data[-1]
    return data[:-pad_len]

def encrypt_bytes(data, key):
    """Encrypt bytes with AES-CBC"""
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data))
    return iv + encrypted  # prepend IV for decryption

def decrypt_bytes(data, key):
    """Decrypt bytes with AES-CBC"""
    iv = data[:16]
    encrypted = data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted)
    return unpad(decrypted)

def encrypt_file(filepath, key):
    """Encrypt file in-place"""
    with open(filepath, "rb") as f:
        data = f.read()
    encrypted = encrypt_bytes(data, key)
    with open(filepath, "wb") as f:
        f.write(encrypted)

def decrypt_file(filepath, key, output_path):
    """Decrypt file to a new path"""
    with open(filepath, "rb") as f:
        data = f.read()
    decrypted = decrypt_bytes(data, key)
    with open(output_path, "wb") as f:
        f.write(decrypted)
