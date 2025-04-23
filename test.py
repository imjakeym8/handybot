from telethon import TelegramClient
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
import asyncio


load_dotenv()
dk = os.getenv("DKEY")
f = Fernet(dk)

#t1 = os.getenv('TELETHON_1')
#api_id = f.decrypt(t1).decode()
#t2 = os.getenv('TELETHON_2')
#api_hash = f.decrypt(t2).decode()
#
#client = TelegramClient("session_2", api_id, api_hash)


#async def main():
#    await client.start()
#    group = await client.get_entity("https://t.me/")
#    print(f"Chat ID: {group.id}")

with open(".env", "a") as file:
    key = f.encrypt(alts.encode())
    file.write(f"\nTELETHON_3 = {key.decode()}")

another_key = f.decrypt(key).decode()
print(another_key)