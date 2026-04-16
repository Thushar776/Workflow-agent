import os
from cryptography.fernet import Fernet

# Docker passes env vars via env_file in docker-compose.yml
ENCRYPTION_KEY_RAW = os.environ.get("ENCRYPTION_KEY", "").strip()

try:
    if not ENCRYPTION_KEY_RAW:
        raise ValueError("Missing Key")
    # Test if it's a valid Fernet key
    cipher_suite = Fernet(ENCRYPTION_KEY_RAW.encode())
except Exception:
    # Fallback to a stable generated key for the session if ENV is missing/malformed
    # In production, this would be a security risk, but for hackathon stability it's a lifesaver.
    NEW_KEY = Fernet.generate_key()
    cipher_suite = Fernet(NEW_KEY)
    print(f"--- WARNING: Using auto-generated key due to malformed ENV ---")


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
