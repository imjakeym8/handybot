from telethon import TelegramClient
from telethon.tl.types import InputPeerUser, InputPeerChannel
from telethon.tl.functions.messages import GetMessageReactionsListRequest, GetMessagesReactionsRequest
import os
from dotenv import load_dotenv
import asyncio
import json
import re
import datetime

load_dotenv()

api_id = os.getenv('TELETHON_API')
api_hash = os.getenv('TELETHON_HASH')


client = TelegramClient("new_session", api_id, api_hash)

async def main():
    if not client.is_connected():
        await client.connect()

    async with client:
        # If private group siya.
        group = InputPeerChannel(channel_id=2037518922,access_hash=-7628654646730185520)
        message = 13613
        stats = await client(GetMessageReactionsListRequest(peer=group,id=message,limit=100))
        print(stats)
        #for each in stats.users:
        #    print(each.id)
        #    if each.username:
        #        print(each.username)

        #reactions = []
        #for each in stats.reactions:
        #    result = each.reaction.emoticon
        #    if result not in reactions:
        #        reactions.append(result)
        #print(reactions)
        
        # If public group siya.
        #group = await client.get_entity('https://t.me/cookie_dao')
        #
        #message = 412003
        #stats = await client(GetMessagesReactionsRequest(peer=group,id=[message]))
        #print(stats)

        # If DM siya.
async def beta():
        if not client.is_connected():
            await client.connect()

        async with client:
            group = await client.get_entity('https://t.me/cookie_dao')
            message = 414637
            stats = await client(GetMessagesReactionsRequest(peer=group,id=[message]))
            print(stats)

async def charlie():
    if not client.is_connected():
        await client.connect()

    async with client:
        dialogs = await client.get_dialogs()
        for dialog in dialogs:
            if "moderators monitoring" in dialog.name.lower():
                print(dialog.entity)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        return super().default(obj)

async def delta():
    if not client.is_connected():
        await client.connect()

    async with client:
        entity = await client.get_input_entity(2037518922)
        message = await client.get_messages(entity, ids=13613)
        data = message.to_dict()
    print(message.date)
    #with open('messageupdate.json', 'w', encoding='utf-8') as file:
    #    json.dump(data, file, ensure_ascii=False, indent=4, cls=DateTimeEncoder)
    #result = [ each["username"] for each in data["users"]]
    #print(result)

asyncio.run(delta())