#Detect month -> assign a unix timestamp to ad to params["to"]
from datetime import datetime
import calendar

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
frmtd_from = datetime.utcfromtimestamp(params["from"]).strftime("%b %d")
frmtd_to = datetime.utcfromtimestamp(params["to"]).strftime("%b %d")
date_range = f"{frmtd_from} - {frmtd_to}"
result.append(date_range)

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
    hour_indexes = " "
result.append(hour_indexes)

#Active Day
active_day = max(monthly_messages)
day_indexes = f", ".join(days[i] for i,v in enumerate(monthly_messages) if v == active_day)

if day_indexes.count(",") == 6: #In case there's no data, insert space
    day_indexes = " "
result.append(day_indexes)

#Members ✅
group = await client.get_entity(f"https://t.me/{context.args[0]}")
member_count = await client.get_participants(group, limit=0)
result.append(member_count.total)

#FINAL 
old_row = document["last_rows"]
row = re.sub(r'\d+', lambda x: str(int(x.group()) + 1), old_row)
try:
    worksheet.update([result], row)
    coll.update_one({"handle":context.args[0]},{'$push':{"results.monthly":{result[0]:{"messages":result[1],"adm":result[2],"active_users":result[3],"dau":result[4],"active_hour":result[5],"active_day":result[6],"members":result[7]}}},'$set':{"last_month_updated":next_month,"last_month_rows":row}})
    await update.message.reply_text("Metrics sent ✅")
    
except Exception as e:
    print(f"Update failed: {e}")