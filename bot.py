import asyncio
import os
import threading
from flask import Flask
from pyrogram import Client, filters

# 1. Initialize a tiny Flask app to satisfy Render's port requirement (Free)
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot is alive and running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

# 2. Event loop initialization fix for newer Python versions
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# 3. Initialize Pyrogram client
app = Client(
    "movie_bot",
    api_id=int(os.environ.get("API_ID", 0)),
    api_hash=os.environ.get("API_HASH", ""),
    bot_token=os.environ.get("BOT_TOKEN", "")
)

DB_CHANNEL = -1004402060167

@app.on_message(filters.text)
async def movie_search(client, message):
    # Your bot handler logic goes here
    pass

if __name__ == "__main__":
    # Run the web server in a background thread so it doesn't block the bot
    web_thread = threading.Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()

    # Run the Telegram bot
    app.run()
