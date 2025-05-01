from cryptography.fernet import Fernet

import os
from dotenv import load_dotenv

load_dotenv()
dk = os.getenv("DKEY")
f = Fernet(dk)

encoded = f.encrypt(f"".encode())
decoded = encoded.decode()

print(decoded)