import asyncio
import os
import sqlite3
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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

DB_CHANNEL = -1004402060167

# Setup Permanent SQLite Database on Disk
db_conn = sqlite3.connect("movies.db", check_same_thread=False)
db_cursor = db_conn.cursor()
db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id INTEGER UNIQUE,
        title TEXT
    )
""")
db_conn.commit()


@app.on_message(filters.command("start"))
async def start_handler(client, message):
  await message.reply(
      "Hey there! 👋 I'm **Better Call Saf**, your permanent movie search"
      " assistant. Type any movie name to get started!"
  )


# Automatically save channel posts into the permanent SQLite database
@app.on_message(filters.chat(DB_CHANNEL))
async def track_channel_messages(client, message):
  text_content = (
      message.caption if message.caption else (message.text if message.text else "")
  )
  if text_content:
    try:
      db_cursor.execute(
          "INSERT OR IGNORE INTO movies (message_id, title) VALUES (?, ?)",
          (message.id, text_content),
      )
      db_conn.commit()
    except Exception as e:
      print(f"DB Insert Error: {e}")


@app.on_message(filters.text & ~filters.command(["start"]))
async def movie_search(client, message):
  query = message.text.lower().strip()
  searching_msg = await message.reply("🔍 Searching your database...")

  try:
    query_words = query.split()

    # Fetch all stored movies from permanent database
    db_cursor.execute("SELECT message_id, title FROM movies")
    rows = db_cursor.fetchall()

    matching_entries = []
    for msg_id, title in rows:
      title_lower = title.lower()
      if query_words and all(word in title_lower for word in query_words):
        if title not in [m[1] for m in matching_entries]:
          matching_entries.append((msg_id, title))

    if len(matching_entries) > 0:
      buttons = []
      for msg_id, title in matching_entries[:10]:
        buttons.append(
            [
                InlineKeyboardButton(
                    f"🎬 {title[:35]}...", callback_data=f"send_{msg_id}"
                )
            ]
        )

      await searching_msg.edit_text(
          "I found these matching movies! Tap below to get your files:",
          reply_markup=InlineKeyboardMarkup(buttons),
      )
    else:
      # Clean message for regular users (no confusing instructions)
      await searching_msg.edit_text(
          "Sorry, that movie is not available in our library yet! 😢 Please try"
          " searching for another title."
      )

  except Exception as e:
    await searching_msg.edit_text(f"Error: {str(e)}")


@app.on_callback_query(filters.regex("^send_"))
async def send_selected_movie(client, callback_query):
  main_msg_id = int(callback_query.data.split("_")[1])
  chat_id = callback_query.message.chat.id

  await callback_query.answer("Sending your movie files...")
  await callback_query.message.edit_text(
      "✅ Sending your files, please wait..."
  )

  try:
    main_msg = await client.get_messages(DB_CHANNEL, main_msg_id)
    if main_msg:
      await main_msg.copy(chat_id=chat_id)

      sent_count = 0
      for next_id in range(main_msg_id + 1, main_msg_id + 30):
        if sent_count >= 25:
          break
        try:
          next_msg = await client.get_messages(DB_CHANNEL, next_id)
          if next_msg and (next_msg.media or next_msg.text):
            await next_msg.copy(chat_id=chat_id)
            sent_count += 1
            await asyncio.sleep(0.3)
        except:
          break

    await callback_query.message.delete()
  except Exception as e:
    await callback_query.message.edit_text(
        f"Error sending file package: {str(e)}"
    )


if __name__ == "__main__":
  web_thread = threading.Thread(target=run_web)
  web_thread.daemon = True
  web_thread.start()

  while True:
    try:
      app.run()
    except FloodWait as e:
      import time

      time.sleep(e.value)
    except Exception as ex:
      import time

      time.sleep(10)
