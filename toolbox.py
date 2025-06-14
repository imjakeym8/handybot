from telethon import TelegramClient
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from cryptography.fernet import Fernet

import os
from dotenv import load_dotenv

from pymongo import MongoClient

from datetime import datetime, timedelta
import re


load_dotenv()

dk = os.getenv("DKEY")
f = Fernet(dk)

t1 = os.getenv('TELETHON_1')
api_id = f.decrypt(t1).decode()
t2 = os.getenv('TELETHON_2')
api_hash = f.decrypt(t2).decode()
tt = os.getenv('TOOLBOT')
tg_token = f.decrypt(tt).decode()

mongo_uri = os.getenv('MONGODB_URI')
mongo_client = MongoClient(mongo_uri)

db = mongo_client.Metrics
admincoll = db.AdminMetrics

client = TelegramClient("local_session", api_id, api_hash)

async def track_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not client.is_connected():
        await client.connect()

    handle = None
    group_id = None

    try:
        if context.args:
            link = context.args[0]
            patt = r"^(?:https?://)?t\.me/(?:c/)?(?:(?P<group_id>\d+)|(?P<handle>[a-zA-Z0-9_]+))(?:/\d+)?/(?P<msg_id>\d+)/?$" # Caters to Private="https://t.me/c/1234/1/1234" and Public="t.me/handle/1234"
            match = re.match(patt, link)
        else:
            await update.message.reply_text("Please provide a proper message link.")
            return
            
        if match:
            if match.group("handle"):
                handle = match.group("handle") 
            elif match.group("group_id"):
                group_id = match.group("group_id")  # Group ID
            else:
                await update.message.reply_text("Invalid link format (1)")
                return
            message_id = match.group("msg_id")  # Message ID
        else:
            await update.message.reply_text("Invalid link format (2)")
            return 

        async with client:
            if handle is not None:
                identifier = handle
                group = await client.get_entity(identifier)
            elif group_id is not None:
                identifier = int(group_id)
                group = await client.get_input_entity(identifier)
            else:
                await update.message.reply_text("Invalid link format (3)")
                return 

            raw_stats = await client(GetMessageReactionsListRequest(peer=group, id=int(message_id), limit=100)) #Count
            stats = raw_stats.to_dict()    
            raw_message = await client.get_messages(group, ids=int(message_id))
            message = raw_message.to_dict()        

            #Reactions
            reactions = list({each["reaction"]["emoticon"] for each in stats["reactions"]})

            #Reactors
            reactors = []
            for each in stats["users"]:
                result = {"user_id":each["id"],"username":each["username"]}
                if result not in reactors:
                    reactors.append(result)

            #Time Posted
            utc8_datetime = message["date"] + timedelta(hours=8)
            time_posted = utc8_datetime.strftime("%m/%d/%y %I:%M")

            #Deadline (let's say 24 hours)
            utc8add24 = message["date"] + timedelta(hours=32)
            deadline = utc8add24.strftime("%m/%d/%y %I:%M")

            if handle is not None:
                admincoll.update_one({"handle": handle},{'$push':{"results.message_stats":{"link":link,"reactions":reactions,"count":stats["count"],"reactors":reactors,"time_posted":time_posted,"deadline":deadline}}})            
            elif group_id is not None:
                admincoll.update_one({"group_id":int(group_id)},{'$push':{"results.message_stats":{"link":link,"reactions":reactions,"count":stats["count"],"reactors":reactors,"time_posted":time_posted,"deadline":deadline}}})
            else:
                await update.message.reply_text("Invalid link format (4)")
                return

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")



if __name__ == '__main__':
    app = ApplicationBuilder().token(tg_token).build()
    track_message_handler = CommandHandler('track_message', track_message)
    app.add_handler(track_message_handler)

    print("Running now... ✅")
    app.run_polling()