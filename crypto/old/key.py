from cryptography.fernet import Fernet

def encrypt(pwd):
    pw = pwd.encode()
    f = Fernet.generate_key()
    f2 = Fernet(f)
    encrypted = f2.encrypt(pw)
    return [encrypted, f]

def decrypt(key, password):
    f1 = Fernet(key)
    decrypted = f1.decrypt(password).decode()
    return decrypted
'''enc = encrypt("hkshls")

print(Fernet(enc[1]).decrypt(enc[0]).decode())'''