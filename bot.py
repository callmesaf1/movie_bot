import asyncio
import os
import threading
from flask import Flask
from pyrogram import Client, filters

# 1. Flask web server for Render
app_web = Flask(__name__)


@app_web.route("/")
def home():
  return "Bot is alive and running!"


def run_web():
  port = int(os.environ.get("PORT", 10000))
  app_web.run(host="0.0.0.0", port=port)


# 2. Event loop fix
try:
  asyncio.get_event_loop()
except RuntimeError:
  asyncio.set_event_loop(asyncio.new_event_loop())

# 3. Initialize Pyrogram Client
app = Client(
    "movie_bot",
    api_id=int(os.environ.get("API_ID", 0)),
    api_hash=os.environ.get("API_HASH", ""),
    bot_token=os.environ.get("BOT_TOKEN", ""),
)

DB_CHANNEL = "@BetterCallSafDB"

# In-memory movie database dictionary: { "movie name keyword": message_object }
movie_database = {}


@app.on_message(filters.command("start"))
async def start_handler(client, message):
  await message.reply(
      "Hey there! 👋 I'm **Better Call Saf**, your go-to movie search"
      " assistant. Type any movie name to get started!"
  )


# Automatically index any new file or message posted in the database channel
@app.on_message(filters.chat(DB_CHANNEL))
async def index_channel_messages(client, message):
  text_content = (
      message.caption if message.caption else (message.text if message.text else "")
  )
  if text_content:
    # Store keywords in lowercase for easy matching
    movie_database[text_content.lower().strip()] = message


@app.on_message(filters.text & ~filters.command(["start"]))
async def movie_search(client, message):
  query = message.text.lower().strip()
  searching_msg = await message.reply("🔍 Searching for your movie...")

  found = False
  # Check if the query matches any stored movie key
  for title, db_msg in movie_database.items():
    if query in title or title in query:
      found = True
      await db_msg.copy(chat_id=message.chat.id)
      await searching_msg.delete()
      break

  if not found:
    await searching_msg.edit_text(
        "Sorry, I couldn't find that movie in the database! 😢\n\n*Tip:* Try"
        " forwarding or posting the movie again into your `@BetterCallSafDB`"
        " channel so the bot can index it!"
    )


if __name__ == "__main__":
  web_thread = threading.Thread(target=run_web)
  web_thread.daemon = True
  web_thread.start()

  app.run()
