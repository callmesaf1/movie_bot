import asyncio
import os
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# 1. Initialize Flask web server for Render port detection
app_web = Flask(__name__)


@app_web.route("/")
def home():
  return "Streaming Bot is alive and running!"


def run_web():
  port = int(os.environ.get("PORT", 10000))
  app_web.run(host="0.0.0.0", port=port)


# Start Flask web server immediately in a background thread
web_thread = threading.Thread(target=run_web)
web_thread.daemon = True
web_thread.start()

# 2. Initialize Pyrogram Client
app = Client(
    "streaming_bot",
    api_id=int(os.environ.get("API_ID", 0)),
    api_hash=os.environ.get("API_HASH", ""),
    bot_token=os.environ.get("BOT_TOKEN", ""),
)


@app.on_message(filters.command("start"))
async def start_handler(client, message):
  await message.reply(
      "Hey there! 👋 I'm your Instant Streaming Assistant.\nType any movie"
      " name, and I will generate the streaming link for you instantly!"
  )


@app.on_message(filters.text & ~filters.command(["start"]))
async def movie_search(client, message):
  query = message.text.strip()
  if not query:
    return

  # Format the user query into a clean URL search format for bingebox.ac
  # Replace spaces with hyphens or plus signs depending on how the site handles searches
  formatted_query = query.lower().replace(" ", "-")
  streaming_url = f"https://bingebox.ac/search?q={formatted_query}"

  keyboard = InlineKeyboardMarkup([
      [
          InlineKeyboardButton(
              f"🌐 Watch '{query}' Online", url=streaming_url
          )
      ]
  ])

  await message.reply(
      f"🎬 **Results for:** `{query}`\n\nClick the button below to find and"
      " stream your movie:",
      reply_markup=keyboard,
  )


if __name__ == "__main__":
  app.run()
