from telethon import TelegramClient
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

import os
from dotenv import load_dotenv

from pymongo import MongoClient
import gspread

import requests
from datetime import datetime
import re

load_dotenv()
gc = gspread.service_account(filename='C:/Users/ACER/OneDrive/Documents/GitHub/handybot/mysa.json')
api_id = os.getenv('TELETHON_API')
api_hash = os.getenv('TELETHON_HASH')
tg_token = os.getenv('DREW_HANDYBOT_TG')
mongo_uri = os.getenv('MONGODB_URI')
combotapi = os.getenv('COMBOT_SHAMAEPH_API')
client = MongoClient(mongo_uri)
db = client.Metrics
coll = db.Projects

client = TelegramClient("session", api_id, api_hash)

async def post_metrics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not client.is_connected():
        await client.connect()

    if context.args and update.effective_chat.type == "private":
        document = coll.find_one({"handle":context.args[0]})
        if not document:
            await update.message.reply_text(f"Error: No document found for handle '{context.args[0]}'")
            return

        sht = gc.open(document["sheet"])
        worksheet = sht.worksheet("Telegram")

        url = 'https://api.combot.org/v2/a/g/'
        params = {}
        jan1 = 1735689600
        params["chat_id"] = document["chat_id"]
        params["api_key"] = combotapi
        if document["last_updated"] < jan1: #Jan. 1, 2025 0:00 UTC
            params["from"] = jan1
            params["to"] = jan1 + 604799
        else:
            params["from"] = document["last_updated"]            
            params["to"] = document["last_updated"] + 604799

        next_week = params["to"] + 1
        response = requests.get(url,params=params)
        combotdata = response.json()

        result = []
        days = ['Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday'] # Start from January 1 which is Wednesday

        #Date
        frmtd_from = datetime.utcfromtimestamp(params["from"]).strftime("%b %d")
        frmtd_to = datetime.utcfromtimestamp(params["to"]).strftime("%b %d")
        date_range = f"{frmtd_from} - {frmtd_to}"
        result.append(date_range)

        #Messages
        weekly_messages = [each[1] for each in combotdata[0]["messages"]]
        messages = sum(weekly_messages)
        result.append(messages)

        #ADM
        adm = round(messages / 7)
        result.append(adm)

        #Active Users
        weekly_active_users = [each[1] for each in combotdata[0]["active_users"]]
        active_users = sum(weekly_active_users)
        result.append(active_users)

        #DAU
        dau = round(active_users / 7)
        result.append(dau)

        #Active Hour
        hours = [each[2] for each in combotdata[0]["hours"]]
        hourly_messages = [sum(hours[i::23]) for i in range(24)]
        active_hour = max(hourly_messages)
        hour_indexes = f", ".join(f"{i}:00" for i,v in enumerate(hourly_messages) if v == active_hour)

        if hour_indexes.count(",") == 23: #In case there's no data, insert space
            hour_indexes = " "
        result.append(hour_indexes)

        #Active Day
        active_day = max(weekly_messages)
        day_indexes = f", ".join(days[i] for i,v in enumerate(weekly_messages) if v == active_day)

        if day_indexes.count(",") == 6: #In case there's no data, insert space
            day_indexes = " "
        result.append(day_indexes)

        #Members
        group = await client.get_entity(f"https://t.me/{context.args[0]}")
        member_count = await client.get_participants(group, limit=0)
        result.append(member_count.total)

        #FINAL 
        old_row = document["last_rows"]
        row = re.sub(r'\d+', lambda x: str(int(x.group()) + 1), old_row)
        try:
            worksheet.update([result], row)
            coll.update_one({"handle":context.args[0]},{'$push':{"results.weekly":{result[0]:{"messages":result[1],"adm":result[2],"active_users":result[3],"dau":result[4],"active_hour":result[5],"active_day":result[6],"members":result[7]}}},'$set':{"last_updated":next_week,"last_rows":row}})
            await update.message.reply_text("Metrics sent ✅")
        except Exception as e:
            print(f"Update failed: {e}")
    else:
        return

async def get_member_count(update: Update, context: ContextTypes.DEFAULT_TYPE): # It's now working!
    try:
        if update.effective_chat.type != "private":
            return
        if not client.is_connected():
            await client.connect()

        group = await client.get_entity('https://t.me/aitechagentchat')
        member_count = await client.get_participants(group, limit=0)
        print(f"Total members:{member_count.total}")
        await update.message.reply_text(f"{member_count.total}")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        print(f"Error: {e}")

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_chat.type != "private":
            return
        if not client.is_connected():
            await client.connect()

        await client.log_out()  # It logs out and deletes the session file!
        await update.message.reply_text("✅ Successfully logged out.")
        print("✅ Logged out and session deleted.")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        print(f"Error: {e}")
    
if __name__ == '__main__':
        app = ApplicationBuilder().token(tg_token).build()
        logout_handler = CommandHandler('mustlogout', logout)
        get_member_count_handler = CommandHandler('get_member_count', get_member_count)
        post_metrics_handler = CommandHandler('post_metrics', post_metrics)
        app.add_handler(post_metrics_handler)
        app.add_handler(logout_handler)
        app.add_handler(get_member_count_handler)

        print("Running now... ✅")
        app.run_polling()