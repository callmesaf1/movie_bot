import os
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# 1. Initialize Flask web server
app_web = Flask(__name__)


@app_web.route("/")
def home():
  return "Streaming Bot is alive and running!"


def run_web():
  port = int(os.environ.get("PORT", 10000))
  app_web.run(host="0.0.0.0", port=port)


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
      "Hey there! 👋 I'm your Multi-Source Streaming Assistant.\nType any movie"
      " name to get streaming links from all platforms!"
  )


@app.on_message(filters.text & ~filters.command(["start"]))
async def movie_search(client, message):
  query = message.text.strip()
  if not query:
    return

  # Multiple streaming platform buttons
  keyboard = InlineKeyboardMarkup([
      [
          InlineKeyboardButton(
              "🎬 Watch on Bingebox", url="https://bingebox.ac/"
          )
      ],
      [
          InlineKeyboardButton(
              "🍿 Watch on Popcorn Movies", url="https://popcornmovies.ac/"
          )
      ],
      [
          InlineKeyboardButton(
              "🌐 Watch on Vivarium", url="https://vivarium.su/"
          )
      ],
  ])

  await message.reply(
      f"🎬 **Movie Found:** `{query}`\n\nChoose your preferred streaming"
      " platform below:",
      reply_markup=keyboard,
  )


if __name__ == "__main__":
  app.run()
