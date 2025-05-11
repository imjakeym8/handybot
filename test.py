from telethon import TelegramClient
from telethon.tl.types import InputPeerChannel
from telethon.tl.functions.messages import GetMessageReactionsListRequest
import os
from dotenv import load_dotenv
import asyncio
import json

load_dotenv()

api_id = os.getenv('TELETHON_API')
api_hash = os.getenv('TELETHON_HASH')


client = TelegramClient("new_session", api_id, api_hash)

import base64
from datetime import datetime

def make_json_safe(obj):
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_safe(v) for v in obj]
    elif isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')  # encode bytes as base64 string
    elif isinstance(obj, datetime):
        return obj.isoformat()  # convert datetime to string
    else:
        return obj

async def main():
    if not client.is_connected():
        await client.connect()

    async with client:
        # If private group siya.
        group = InputPeerChannel(channel_id=##,access_hash=##)
        message = 13613
        stats = await client(GetMessageReactionsListRequest(peer=group,id=message,limit=100))
        print(stats)

        # If public group siya.
        #group = await client.get_entity('https://t.me/')
        #
        #message = 412003
        #stats = await client(GetMessagesReactionsRequest(peer=group,id=[message]))
        #print(stats)
        cleaned_data = make_json_safe(stats.to_dict())
        with open('message.json', 'w') as file:
            json.dump(cleaned_data,file,indent=4)

async def beta():
    if not client.is_connected():
        await client.connect()

    async with client:
        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            print("Group Title:", entity.title)
            print("ID:", entity.id)
            print("Access Hash:", entity.access_hash)

async def charlie():
    if not client.is_connected():
        await client.connect()

    async with client:
        pass
#with open('message.json', 'r') as file:
#    data = json.load(file)
#    result = [ each["username"] for each in data["users"]]
#    print(result)

asyncio.run(beta())


