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


@app.on_message(filters.command("start"))
async def start_handler(client, message):
  await message.reply(
      "Hey there! 👋 I'm **Better Call Saf**, your go-to movie search"
      " assistant. Type any movie name to get started!"
  )


@app.on_message(filters.text & ~filters.command(["start"]))
async def movie_search(client, message):
  query = message.text.lower()
  searching_msg = await message.reply("🔍 Searching for your movie...")

  try:
    found = False
    # Iterate through recent channel messages instead of using restricted search API
    async for msg in client.get_chat_history(DB_CHANNEL, limit=50):
      # Check if message has caption or text matching the query
      text_content = (
          msg.caption
          if msg.caption
          else (msg.text if msg.text else "")
      )
      if query in text_content.lower():
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
    await searching_msg.edit_text(f"Error: {str(e)}")


if __name__ == "__main__":
  web_thread = threading.Thread(target=run_web)
  web_thread.daemon = True
  web_thread.start()

  app.run()
