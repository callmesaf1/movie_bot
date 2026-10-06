import asyncio
import os
import sqlite3
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

# Setup SQLite Database for Titles & Links
db_conn = sqlite3.connect("streaming_links.db", check_same_thread=False)
db_cursor = db_conn.cursor()
db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        url TEXT
    )
""")
db_conn.commit()


@app.on_message(filters.command("start"))
async def start_handler(client, message):
  await message.reply(
      "Hey there! 👋 I'm your Online Streaming Assistant.\nType any movie"
      " name to find streaming links!"
  )


# Admin command to add a movie link: /add Movie Title | https://link.com
@app.on_message(filters.command("add"))
async def add_link_handler(client, message):
  try:
    text_data = message.text.split(" ", 1)[1]
    title, url = text_data.split("|")
    title = title.strip()
    url = url.strip()

    db_cursor.execute(
        "INSERT INTO links (title, url) VALUES (?, ?)", (title, url)
    )
    db_conn.commit()
    await message.reply(
        f"✅ **Successfully Added!**\n🎬 **Title:** {title}\n🔗 **URL:** {url}"
    )
  except Exception:
    await message.reply(
        "❌ **Usage Error!**\nPlease use this format:\n`/add Spiderman Brand"
        " New Day | https://bingebox.ac/movie/...`"
    )


@app.on_message(filters.text & ~filters.command(["start", "add"]))
async def movie_search(client, message):
  query = message.text.lower().strip()
  searching_msg = await message.reply("🔍 Searching streaming library...")

  try:
    query_words = query.split()

    db_cursor.execute("SELECT id, title, url FROM links")
    rows = db_cursor.fetchall()

    matching_entries = []
    for row_id, title, url in rows:
      title_lower = title.lower()
      if query_words and all(word in title_lower for word in query_words):
        matching_entries.append((row_id, title, url))

    if len(matching_entries) > 0:
      buttons = []
      for row_id, title, url in matching_entries[:10]:
        buttons.append(
            [
                InlineKeyboardButton(
                    f"🎬 {title[:35]}", callback_data=f"watch_{row_id}"
                )
            ]
        )

      await searching_msg.edit_text(
          "I found these matching movie versions! Tap below to watch"
          " online:",
          reply_markup=InlineKeyboardMarkup(buttons),
      )
    else:
      await searching_msg.edit_text(
          "Sorry, that movie streaming link is not available yet! 😢"
      )

  except Exception as e:
    await searching_msg.edit_text(f"Error: {str(e)}")


@app.on_callback_query(filters.regex("^watch_"))
async def send_streaming_link(client, callback_query):
  row_id = int(callback_query.data.split("_")[1])

  db_cursor.execute("SELECT title, url FROM links WHERE id = ?", (row_id,))
  result = db_cursor.fetchone()

  if result:
    title, url = result
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🌐 Watch Online Now", url=url)]]
    )
    await callback_query.message.edit_text(
        f"🎬 **{title}**\n\nClick the button below to stream online:",
        reply_markup=keyboard,
    )
  else:
    await callback_query.answer("Link not found!", show_alert=True)


if __name__ == "__main__":
  app.run()
