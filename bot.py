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
    "streaming_bot",
    api_id=int(os.environ.get("API_ID", 0)),
    api_hash=os.environ.get("API_HASH", ""),
    bot_token=os.environ.get("BOT_TOKEN", ""),
)


@app.on_message(filters.command("start"))
async def start_handler(client, message):
  await message.reply(
      "Hey there! 👋 I'm your Universal Streaming Assistant.\nType *any*"
      " movie name in the world, and I will generate the direct watch links"
      " for you!"
  )


@app.on_message(filters.text & ~filters.command(["start"]))
async def movie_search(client, message):
  try:
    query = message.text.strip()
    if not query:
      return

    # Clean up user query for web search formatting
    formatted_query = query.lower().replace(" ", "-")
    search_query_url = query.lower().replace(" ", "+")

    # Direct dynamic links for any movie typed across your 3 favorite platforms
    bingebox_url = f"https://bingebox.ac/search?q={search_query_url}"
    popcorn_url = f"https://popcornmovies.ac/search?q={search_query_url}"
    vivarium_url = f"https://vivarium.su/search?q={search_query_url}"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🎬 Watch on Bingebox", url=bingebox_url)],
        [InlineKeyboardButton(f"🍿 Watch on Popcorn Movies", url=popcorn_url)],
        [InlineKeyboardButton(f"🌐 Watch on Vivarium", url=vivarium_url)],
    ])

    await message.reply(
        f"🔍 **Search Results for:** `{query.title()}`\n\nClick your preferred"
        " platform below to jump straight to the movie page:",
        reply_markup=keyboard,
    )
  except Exception as e:
    print(f"Search Error: {e}")


if __name__ == "__main__":
  app.run()
