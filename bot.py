import os
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# 1. Initialize Flask web server for Render keep-alive
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
    "streaming_bot_v6",
    api_id=int(os.environ.get("API_ID", 0)),
    api_hash=os.environ.get("API_HASH", ""),
    bot_token=os.environ.get("BOT_TOKEN", ""),
)


@app.on_message(filters.command("start"))
async def start_handler(client, message):
  await message.reply(
      "🎬 **Welcome to Universal Streaming Bot!**\n\nType *any* movie name, and I"
      " will generate direct playback links for the best recommended"
      " platforms!"
  )


@app.on_message(filters.text & ~filters.command(["start"]))
async def movie_search(client, message):
  try:
    query = message.text.strip()
    if not query:
      return

    search_q = query.lower().replace(" ", "+")

    # The 2 perfectly working recommended sites
    popcorn_url = f"https://popcornmovies.ac/search?q={search_q}"
    zoryva_url = f"https://zoryva.me/search?q={search_q}"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⭐🍿 Popcorn Movies (Recommended)", url=popcorn_url
            )
        ],
        [InlineKeyboardButton("⭐🌐 Zoryva (Recommended)", url=zoryva_url)],
    ])

    await message.reply(
        f"🎯 **Movie Requested:** `{query.title()}`\n\nChoose your recommended"
        " platform below:",
        reply_markup=keyboard,
    )
  except Exception as e:
    print(f"Search Error: {e}")


if __name__ == "__main__":
  app.run()
