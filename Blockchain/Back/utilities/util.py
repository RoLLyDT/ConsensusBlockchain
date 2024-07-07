import hashlib

def hash256(s):
    "Double hashing"
    if isinstance(s, str):
        s = s.encode('utf-8')  # Encode the string to bytes if it's Unicode
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()