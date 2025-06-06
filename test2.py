import re
from datetime import datetime, timedelta, timezone

async def track_message(update: Update, context: ContextTypes.DEFAULT_TYPE, link:str): #update: Update, context: ContextTypes.DEFAULT_TYPE
    patt = r"^(?:https?://)?t\.me/(?:c/)?(?:(?P<handle>[a-zA-Z0-9_]+)|(?P<group_id>\d+))(?:/\d+)?/(?P<msg_id>\d+)/?$" # Caters to Private="https://t.me/c/1234/1/1234" and Public="t.me/handle/1234"
    match = re.match(patt, link)
    if match:
        if match.group("handle"):
            handle = match.group("handle") 
        elif match.group("group_id"):
            group_id = match.group("group_id")  # Group ID
        else:
            return "Error: Invalid link format"
        message_id = match.group("msg_id")  # Message ID
    else:
        return "Invalid link format"
    
    async with client:
        if handle:
            identifier = handle
            group = await client.get_entity(identifier)
        elif group_id:
            identifier = group_id
            group = await client.get_input_entity(identifier)

        raw_stats = await client(GetMessageReactionsListRequest(peer=group, id=message_id, limit=100)) #Count
        stats = raw_stats.to_dict()    
        raw_message = await client.get_messages(group, ids=message_id)
        message = raw_message.to_dict()        

        #Reactions
        reactions = list({each["reaction"]["emoticon"] for each in stats["reactions"]})

        #Reactors
        reactors = []
        for each in stats["users"]:
            result = {"user_id":each["id"],"username":each["username"]}
            if result not in reactors:
                reactions.append(result)

        #Time Posted
        utc8_datetime = message["date"] + timedelta(hours=8)
        time_posted = utc8_datetime.strftime("%m/%d/%y %I:%M")

        #Deadline (let's say 24 hours)
        utc8add24 = message["date"] + timedelta(hours=32)
        deadline = utc8add24.strftime("%m/%d/%y %I:%M")

        if handle:
            admincoll.update_one({"handle": handle},{'$push':{"results.message_stats":{"link":link,"reactions":reactions,"count":stats["count"],"reactors":reactors,"time_posted":time_posted,"deadline":deadline}}})            
        elif group_id:
            admincoll.update_one({"group_id":group_id},{'$push':{"results.message_stats":{"link":link,"reactions":reactions,"count":stats["count"],"reactors":reactors,"time_posted":time_posted,"deadline":deadline}}})