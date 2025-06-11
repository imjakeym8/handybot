from telethon.sync import TelegramClient
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()
dk = os.getenv("DKEY")
f = Fernet(dk)

t1 = os.getenv('TELETHON_1')
api_id = f.decrypt(t1).decode()
t2 = os.getenv('TELETHON_2')
api_hash = f.decrypt(t2).decode()
session_name = 'local_session' 
tt = os.getenv('HANDYBOT')
tg_token = f.decrypt(tt).decode()

with TelegramClient(session_name, api_id, api_hash) as client:
    me = client.get_me()
    print(f"Logged in as: {me.first_name} (@{me.username}) | ID: {me.id}")

#from telegram import Update
#from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
#
#async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): # My IP address was blocked, bot is working on Davao
#    await update.message.reply_text("Hello!")
#
#if __name__ == '__main__':
#    app = ApplicationBuilder().token(tg_token).build()
#    app.add_handler(CommandHandler("start", start))
#
#    print("Running now... ✅")
#    app.run_polling()