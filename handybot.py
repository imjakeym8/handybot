from telethon import TelegramClient
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telethon.tl.functions.messages import GetMessageReactionsListRequest
from cryptography.fernet import Fernet

import os
from dotenv import load_dotenv

from pymongo import MongoClient
import gspread

import requests
from datetime import datetime, timedelta
import calendar
import re

load_dotenv()
gc = gspread.service_account(filename='C:/Users/ACER/OneDrive/Documents/GitHub/handybot/mysa.json') #must change on Linux Terminal

dk = os.getenv("DKEY")
f = Fernet(dk)

t1 = os.getenv('TELETHON_1')
api_id = f.decrypt(t1).decode()
t2 = os.getenv('TELETHON_2')
api_hash = f.decrypt(t2).decode()
tt = os.getenv('HANDYBOT')
tg_token = f.decrypt(tt).decode()

mongo_uri = os.getenv('MONGODB_URI')
client = MongoClient(mongo_uri)

db = client.Metrics
coll = db.Projects
admincoll = db.AdminMetrics

client = TelegramClient("local_session", api_id, api_hash)

async def post_metrics(update: Update, context: ContextTypes.DEFAULT_TYPE, handle=None):
    if not client.is_connected():
        await client.connect()

    if not context.args and handle is not None: #This is for main.py
        document = coll.find_one({"handle":handle})
        if not document:
            await update.message.reply_text(f"Error: No document found for handle '{handle}'")
            return

        sht = gc.open(document["sheet"])
        worksheet = sht.worksheet("Telegram")

        url = 'https://api.combot.org/v2/a/g/'
        params = {}
        jan1 = 1735689600
        params["chat_id"] = document["chat_id"]
        params["api_key"] = f.decrypt(document["point"]).decode()
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
            hour_indexes = "-"
        result.append(hour_indexes)

        #Active Day
        active_day = max(weekly_messages)
        day_indexes = f", ".join(days[i] for i,v in enumerate(weekly_messages) if v == active_day)

        if day_indexes.count(",") == 6: #In case there's no data, insert space
            day_indexes = "-"
        result.append(day_indexes)

        #Members
        group = await client.get_entity(f"https://t.me/{handle}")
        member_count = await client.get_participants(group, limit=0)
        result.append(member_count.total)

        #FINAL 
        old_row = document["last_rows"]
        row = re.sub(r'\d+', lambda x: str(int(x.group()) + 1), old_row)
        try:
            worksheet.update([result], row)
            coll.update_one({"handle":handle},{'$push':{"results.weekly":{result[0]:{"messages":result[1],"adm":result[2],"active_users":result[3],"dau":result[4],"active_hour":result[5],"active_day":result[6],"members":result[7]}}},'$set':{"last_updated":next_week,"last_rows":row}})
        except Exception as e:
            print(f"Update failed: {e}")

    elif context.args and update.effective_chat.type == "private":
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
        params["api_key"] = f.decrypt(document["point"]).decode()
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
            hour_indexes = "-"
        result.append(hour_indexes)

        #Active Day
        active_day = max(weekly_messages)
        day_indexes = f", ".join(days[i] for i,v in enumerate(weekly_messages) if v == active_day)

        if day_indexes.count(",") == 6: #In case there's no data, insert space
            day_indexes = "-"
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
            try:
                await update.message.reply_text("Metrics sent ✅")
            except Exception as e:
                print(f"There was an error: {e}")
        except Exception as e:
            print(f"Update failed: {e}")

    else:
        print("Failed.")

async def post_monthly_metrics(update: Update, context: ContextTypes.DEFAULT_TYPE, handle=None):
    if not client.is_connected():
        await client.connect()

    if not context.args and handle is not None: #This is for main.py
        document = coll.find_one({"handle":handle})
        if not document:
            await update.message.reply_text(f"Error: No document found for handle '{handle}'")
            return

        sht = gc.open(document["sheet"])
        worksheet = sht.worksheet("Telegram")

        last_month_updated = datetime.utcfromtimestamp(document["last_month_updated"])
        res = calendar.monthrange(last_month_updated.year, last_month_updated.month)
        monthrangeto = res[1] * 24 * 60 * 60 - 1

        url = 'https://api.combot.org/v2/a/g/'
        params = {}
        jan1 = 1735689600
        params["chat_id"] = document["chat_id"]
        params["api_key"] = f.decrypt(document["point"]).decode()
        if document["last_month_updated"] < jan1: #Jan. 1, 2025 0:00 UTC
            params["from"] = jan1
            params["to"] = jan1 + monthrangeto
        else:
            params["from"] = document["last_month_updated"]            
            params["to"] = document["last_month_updated"] + monthrangeto

        next_month = params["to"] + 1
        response = requests.get(url,params=params)
        combotdata = response.json()

        result = []
        days = ['Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday'] # Start from January 1 which is Wednesday

        #Date
        curr_month = datetime.utcfromtimestamp(params["from"]).strftime("%B")
        result.append(curr_month)

        #Messages
        monthly_messages = [each[1] for each in combotdata[0]["messages"]]
        messages = sum(monthly_messages)
        result.append(messages)

        #ADM
        adm = round(messages / res[1])
        result.append(adm)

        #Active Users
        monthly_active_users = [each[1] for each in combotdata[0]["active_users"]]
        active_users = sum(monthly_active_users)
        result.append(active_users)

        #DAU
        dau = round(active_users / res[1])
        result.append(dau)

        #Active Hour
        hours = [each[2] for each in combotdata[0]["hours"]]
        hourly_messages = [sum(hours[i::23]) for i in range(24)]
        active_hour = max(hourly_messages)
        hour_indexes = f", ".join(f"{i}:00" for i,v in enumerate(hourly_messages) if v == active_hour)

        if hour_indexes.count(",") == 23: #In case there's no data, insert space
            hour_indexes = "-"
        result.append(hour_indexes)

        #Active Day
        added_weekly_messages = [sum(monthly_messages[i::7]) for i in range(7)]
        active_day = max(added_weekly_messages)
        day_indexes = ", ".join(days[i] for i,v in enumerate(added_weekly_messages) if v == active_day)

        if day_indexes.count(",") == 6:
            day_indexes = "-"
        result.append(day_indexes)

        #Members ✅
        group = await client.get_entity(f"https://t.me/{handle}")
        member_count = await client.get_participants(group, limit=0)
        result.append(member_count.total)

        #FINAL 
        old_row = document["last_monthly_rows"]
        row = re.sub(r'\d+', lambda x: str(int(x.group()) + 1), old_row)
        try:
            worksheet.update([result[1:]], row) #It will still proceed if nothing was printed, check admin access if service account was added
            coll.update_one({"handle":handle},{'$push':{"results.monthly":{result[0]:{"messages":result[1],"adm":result[2],"active_users":result[3],"dau":result[4],"active_hour":result[5],"active_day":result[6],"members":result[7]}}},'$set':{"last_month_updated":next_month,"last_monthly_rows":row}})
        except Exception as e:
            print(f"Update failed: {e}")    

    elif context.args and update.effective_chat.type == "private":
        document = coll.find_one({"handle":context.args[0]})
        if not document:
            await update.message.reply_text(f"Error: No document found for handle '{context.args[0]}'")
            return

        sht = gc.open(document["sheet"])
        worksheet = sht.worksheet("Telegram")

        last_month_updated = datetime.utcfromtimestamp(document["last_month_updated"])
        res = calendar.monthrange(last_month_updated.year, last_month_updated.month)
        monthrangeto = res[1] * 24 * 60 * 60 - 1

        url = 'https://api.combot.org/v2/a/g/'
        params = {}
        jan1 = 1735689600
        params["chat_id"] = document["chat_id"]
        params["api_key"] = f.decrypt(document["point"]).decode()
        if document["last_month_updated"] < jan1: #Jan. 1, 2025 0:00 UTC
            params["from"] = jan1
            params["to"] = jan1 + monthrangeto
        else:
            params["from"] = document["last_month_updated"]            
            params["to"] = document["last_month_updated"] + monthrangeto

        next_month = params["to"] + 1
        response = requests.get(url,params=params)
        combotdata = response.json()

        result = []
        days = ['Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday', 'Tuesday'] # Start from January 1 which is Wednesday

        #Date
        curr_month = datetime.utcfromtimestamp(params["from"]).strftime("%B")
        result.append(curr_month)

        #Messages
        monthly_messages = [each[1] for each in combotdata[0]["messages"]]
        messages = sum(monthly_messages)
        result.append(messages)

        #ADM
        adm = round(messages / res[1])
        result.append(adm)

        #Active Users
        monthly_active_users = [each[1] for each in combotdata[0]["active_users"]]
        active_users = sum(monthly_active_users)
        result.append(active_users)

        #DAU
        dau = round(active_users / res[1])
        result.append(dau)

        #Active Hour
        hours = [each[2] for each in combotdata[0]["hours"]]
        hourly_messages = [sum(hours[i::23]) for i in range(24)]
        active_hour = max(hourly_messages)
        hour_indexes = f", ".join(f"{i}:00" for i,v in enumerate(hourly_messages) if v == active_hour)

        if hour_indexes.count(",") == 23: #In case there's no data, insert space
            hour_indexes = "-"
        result.append(hour_indexes)

        #Active Day
        added_weekly_messages = [sum(monthly_messages[i::7]) for i in range(7)]
        active_day = max(added_weekly_messages)
        day_indexes = ", ".join(days[i] for i,v in enumerate(added_weekly_messages) if v == active_day)

        if day_indexes.count(",") == 6:
            day_indexes = "-"
        result.append(day_indexes)

        #Members ✅
        group = await client.get_entity(f"https://t.me/{context.args[0]}")
        member_count = await client.get_participants(group, limit=0)
        result.append(member_count.total)

        #FINAL 
        old_row = document["last_monthly_rows"]
        row = re.sub(r'\d+', lambda x: str(int(x.group()) + 1), old_row)
        try:
            worksheet.update([result[1:]], row) #It will still proceed if nothing was printed, check admin access if service account was added
            coll.update_one({"handle":context.args[0]},{'$push':{"results.monthly":{result[0]:{"messages":result[1],"adm":result[2],"active_users":result[3],"dau":result[4],"active_hour":result[5],"active_day":result[6],"members":result[7]}}},'$set':{"last_month_updated":next_month,"last_monthly_rows":row}})
            try:
                await update.message.reply_text("Metrics sent ✅")
            except Exception as e:
                print(f"There was an error: {e}")
        except Exception as e:
            print(f"Update failed: {e}")

    else:
        return

if __name__ == '__main__':
    app = ApplicationBuilder().token(tg_token).build()
    post_metrics_handler = CommandHandler('post_metrics', post_metrics)
    post_monthly_metrics_handler = CommandHandler('post_monthly_metrics', post_monthly_metrics)
    app.add_handler(post_metrics_handler)
    app.add_handler(post_monthly_metrics_handler)

    print("Running now... ✅")
    app.run_polling()