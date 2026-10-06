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
      "Hey there! 👋 I'm your 4-Site Universal Streaming Assistant.\nType *any*"
      " movie name, and I will generate direct search links for all 4"
      " platforms instantly!"
  )


@app.on_message(filters.text & ~filters.command(["start"]))
async def movie_search(client, message):
  try:
    query = message.text.strip()
    if not query:
      return

    search_q = query.lower().replace(" ", "+")

    # Links for all 4 working websites
    popcorn_url = f"https://popcornmovies.ac/search?q={search_q}"
    zoryva_url = f"https://zoryva.me/search?q={search_q}"
    bingebang_url = f"https://bingebang.st/search?q={search_q}"
    stigstream_url = f"https://stigstream.ru/search?q={search_q}"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🍿 Watch on Popcorn Movies", url=popcorn_url)],
        [InlineKeyboardButton("🌐 Watch on Zoryva", url=zoryva_url)],
        [InlineKeyboardButton("⚡ Watch on BingeBang", url=bingebang_url)],
        [InlineKeyboardButton("🚀 Watch on Stigstream", url=stigstream_url)],
    ])

    await message.reply(
        f"🔍 **Search Results for:** `{query.title()}`\n\nChoose your preferred"
        " platform below to open the movie:",
        reply_markup=keyboard,
    )
  except Exception as e:
    print(f"Search Error: {e}")


if __name__ == "__main__":
  app.run()
