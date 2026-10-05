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

# Use string format or integer for the channel
DB_CHANNEL = -1004402060167


@app.on_message(filters.command("start"))
async def start_handler(client, message):
  await message.reply(
      "Hey there! 👋 I'm **Better Call Saf**, your go-to movie search"
      " assistant. Type any movie name to get started!"
  )


@app.on_message(filters.text & ~filters.command(["start"]))
async def movie_search(client, message):
  query = message.text
  searching_msg = await message.reply("🔍 Searching for your movie...")

  try:
    # Resolve chat using the peer object directly
    chat_id = int(DB_CHANNEL)
    found = False

    async for msg in client.search_messages(chat_id, query=query, limit=1):
      found = True
      await msg.copy(chat_id=message.chat.id)
      await searching_msg.delete()
      break

    if not found:
      await searching_msg.edit_text(
          "Sorry, I couldn't find that movie in the database! 😢 Try searching"
          " another title."
      )
  except Exception as e:
    # Fallback to export link or get chat
    try:
      chat = await client.get_chat(DB_CHANNEL)
      async for msg in client.search_messages(chat.id, query=query, limit=1):
        await msg.copy(chat_id=message.chat.id)
        await searching_msg.delete()
        return
      await searching_msg.edit_text("Movie not found in database channel.")
    except Exception as err:
      await searching_msg.edit_text(
          f"Database Error: {str(err)}\n\nTip: Make sure the bot is an admin in"
          " your database channel!"
      )


if __name__ == "__main__":
  web_thread = threading.Thread(target=run_web)
  web_thread.daemon = True
  web_thread.start()

  app.run()
