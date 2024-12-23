from cryptography.fernet import Fernet
def generate_key():
    return Fernet.generate_key()

key = generate_key()
print(f"key: {key}")