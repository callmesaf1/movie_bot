import asyncio
import logging
from pyrogram import Client, filters

# Fix for Python 3.14 event loop compatibility
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# Enable logging
logging.basicConfig(level=logging.INFO)

# Your Callmesaf Bot credentials
API_ID = 32201173
API_HASH = "08b194481a7cc668589a34a8089634d3"
BOT_TOKEN = "8302623227:AAENbiMm_BYDKDqXbvZYm5YK91PYgDDZtgE"
DB_CHANNEL = -1004402060167

app = Client(
    "callmesaf_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply_text(
        "**Hey there! 👋 I'm callmesaf, your go-to movie search assistant.**\n\n"
        "Type any movie name, and I'll find the download link for you instantly!"
    )

@app.on_message(filters.text & ~filters.private & ~filters.command)
async def auto_filter(client, message):
    query = message.text
    async for msg in client.search_messages(DB_CHANNEL, query=query):
        await msg.copy(message.chat.id)
        return
    
    await message.reply_text("❌ Movie not found in database. Try another name!")

print("Bot is starting up...")
app.run()
