import asyncio
import os
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

# Use your private channel numeric ID
DB_CHANNEL = -1004402060167
channel_messages = []


@app.on_message(filters.command("start"))
async def start_handler(client, message):
  await message.reply(
      "Hey there! 👋 I'm **Better Call Saf**, your go-to movie search"
      " assistant. Type any movie name to get started!"
  )


# Automatically cache incoming or existing channel messages live
@app.on_message(filters.chat(DB_CHANNEL))
async def track_channel_messages(client, message):
  if message not in channel_messages:
    channel_messages.append(message)
  if len(channel_messages) > 1000:
    channel_messages.pop(0)


@app.on_message(filters.text & ~filters.command(["start"]))
async def movie_search(client, message):
  query = message.text.lower().strip()
  searching_msg = await message.reply("🔍 Searching your database...")

  try:
    query_words = query.split()
    matching_entries = []

    for i, db_msg in enumerate(channel_messages):
      text_content = (
          db_msg.caption
          if db_msg.caption
          else (db_msg.text if db_msg.text else "")
      )
      text_lower = text_content.lower()

      if query_words and all(word in text_lower for word in query_words):
        if text_content not in [m[1] for m in matching_entries]:
          matching_entries.append((i, text_content))

    if len(matching_entries) > 1:
      buttons = []
      for idx, title in matching_entries[:10]:
        buttons.append([InlineKeyboardButton(title, callback_data=f"send_{idx}")])

      await searching_msg.edit_text(
          "I found multiple matches! Please choose the one you want:",
          reply_markup=InlineKeyboardMarkup(buttons),
      )

    elif len(matching_entries) == 1:
      found_index = matching_entries[0][0]
      await send_movie_package(client, message.chat.id, found_index)
      await searching_msg.delete()
    else:
      await searching_msg.edit_text(
          "Sorry, I couldn't find that movie in your database! 😢\n\n*Tip:* Just"
          " forward the movie post once in your private channel to index it."
      )

  except Exception as e:
    await searching_msg.edit_text(f"Error: {str(e)}")


@app.on_callback_query(filters.regex("^send_"))
async def send_selected_movie(client, callback_query):
  found_index = int(callback_query.data.split("_")[1])
  chat_id = callback_query.message.chat.id

  await callback_query.answer("Sending your movie files...")
  await callback_query.message.edit_text(
      "✅ Sending your files, please wait..."
  )

  await send_movie_package(client, chat_id, found_index)
  await callback_query.message.delete()


async def send_movie_package(client, chat_id, found_index):
  if found_index >= len(channel_messages):
    return

  main_msg = channel_messages[found_index]
  await main_msg.copy(chat_id=chat_id)

  sent_count = 0
  for j in range(found_index + 1, len(channel_messages)):
    if sent_count >= 25:
      break
    next_msg = channel_messages[j]
    await next_msg.copy(chat_id=chat_id)
    sent_count += 1
    await asyncio.sleep(0.3)


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
