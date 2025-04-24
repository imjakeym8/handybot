import requests
from time import localtime, strftime, sleep
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='/home/cloudshell-user/.env')
bot_token = os.getenv("TG_MODWATCHER")
jayceeph = os.getenv("TG_JAYCEEPH")

def escape_markdown_v2(text):
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{char}" if char in escape_chars else char for char in text)

geturl = f"https://api.telegram.org/bot{bot_token}/getUpdates"
posturl = f"https://api.telegram.org/bot{bot_token}/sendMessage"
offset = None

print("Bot is running.")
while True:
    params = {"offset": offset, "timeout": 50, "allowed_updates": ["message"]}

    response = requests.get(geturl, params=params)
    updates = response.json().get("result", [])

    for each_update in updates:
        present_data = {"groupusername":None,"groupname":None,"chat_id":None,"message_id":None,"date":None,"user":None,"user_id":None,"username":None,"text":None}
        each_message = each_update["message"]
        if each_message["chat"]["type"] == "supergroup" and each_message["from"].get("username", "").endswith('ph'):
            present_data["groupusername"] = each_message["chat"]["username"]
            present_data["groupname"] = each_message["chat"]["title"] #chat required
            present_data["chat_id"] = each_message["chat"]["id"] #chat,id required
            present_data["message_id"] = each_message["message_id"] #required
            present_data["date"] = strftime("%I:%M%p %m/%d/%y", localtime(each_message["date"])) #required
            present_data["user"] = each_message["from"]["first_name"] #first_name required
            present_data["user_id"] = each_message["from"]["id"] #id required
            present_data["username"] = each_message["from"]["username"] #already guarantees i have the username
            present_data["text"] = each_message["text"] if each_message.get("text") else "This user must have only sent a Sticker, GIF, an image/video or any file\\._" 
            offset = each_update["update_id"] + 1
        
            msg_user_display = f"[__{escape_markdown_v2(present_data['user'])}__](https://t\\.me/{escape_markdown_v2(present_data['username'])})" if present_data.get("username") else escape_markdown_v2(present_data["user"])
            msg = (
                f"*Chat:* [__{escape_markdown_v2(present_data['groupname'])}__](https://t\\.me/{escape_markdown_v2(present_data['groupusername'])}) \\(ID:{escape_markdown_v2(str(present_data['chat_id']))}\\)\n"
                f"*User:* {msg_user_display} \\(ID:{escape_markdown_v2(str(present_data['user_id']))}\\)\n"
                f"*Time:* {escape_markdown_v2(present_data['date'])}\n"
                f"[*Message:*](https://t\\.me/{escape_markdown_v2(present_data['groupusername'])}/{escape_markdown_v2(str(present_data['message_id']))})\n"
                f"{escape_markdown_v2(present_data['text'])}"
                )

            payload = {
                "chat_id": jayceeph,
                "text": msg,
                "parse_mode": "MarkdownV2",
                "disable_web_page_preview": True
            }
            post_response = requests.post(posturl, data=payload)

            if post_response.ok:
                print("Message sent successfully!")
            else:
                print("Failed to send message:", post_response.text)

        else:
            pass
    
    sleep(5)