import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

# In a real scenario, this should be a strong securely stored key via ENV.
# For hackathon purposes, if not set, we generate a persistent one (but usually we provide a default)
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", Fernet.generate_key().decode())

cipher_suite = Fernet(ENCRYPTION_KEY.encode())

def encrypt_pii(data: str) -> str:
    if not data:
        return data
    return cipher_suite.encrypt(data.encode('utf-8')).decode('utf-8')

def decrypt_pii(encrypted_data: str) -> str:
    if not encrypted_data:
        return encrypted_data
    try:
        return cipher_suite.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')
    except Exception:
        return "Decryption Failed"

def mask_email(email: str) -> str:
    """Masks email for frontend display (e.g. t****@example.com)"""
    if not email or '@' not in email:
        return email
    parts = email.split('@')
    name = parts[0]
    domain = parts[1]
    if len(name) <= 2:
        masked_name = name[0] + "****"
    else:
        masked_name = name[0] + "****" + name[-1]
    return f"{masked_name}@{domain}"
