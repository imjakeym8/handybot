import requests
from datetime import datetime

import gspread
gc = gspread.service_account(filename='C:/Users/ACER/OneDrive/Documents/GitHub/handybot/mysa.json')

import os
from dotenv import load_dotenv
from pymongo import MongoClient

import re

load_dotenv()
mongo_uri = os.getenv('MONGODB_URI')
combotapi = os.getenv('COMBOT_JAYCEEPH_API')
client = MongoClient(mongo_uri)
db = client.Metrics
coll = db.Projects

#To do list:
#add API key to database since I'm not admin to all chats.

#List of commands i want: get_metrics("project"), post_metrics(project="", option="weekly"/"monthly")
def post_metrics(project):
    document = coll.find_one({"handle":project})
    if not document:
        print(f"Error: No document found for handle '{project}'")
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
    result.append(hour_indexes)

    #Active Day
    active_day = max(weekly_messages)
    day_indexes = f", ".join(days[i] for i,v in enumerate(weekly_messages) if v == active_day)
    result.append(day_indexes)

    old_row = document["last_rows"]
    row = re.sub(r'\d+', lambda x: str(int(x.group()) + 1), old_row)
    try:
        worksheet.update([result], row)
        coll.update_one({"handle":project},{'$push':{"results.weekly":{result[0]:{"messages":result[1],"adm":result[2],"active_users":result[3],"dau":result[4],"active_hour":result[5],"active_day":result[6]}}},'$set':{"last_updated":next_week,"last_rows":row}})
    except Exception as e:
        print(f"Update failed: {e}")

post_metrics("cookie_dao")