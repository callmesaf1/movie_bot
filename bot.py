import asyncio
import os
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# 1. Initialize Flask web server for Render keep-alive
app_web = Flask(__name__)


@app_web.route("/")
def home():
  return "Bot is alive and running!"


# 2. Initialize Pyrogram Client
app = Client(
    "movie_bot",
    api_id=int(os.environ.get("API_ID", 0)),
    api_hash=os.environ.get("API_HASH", ""),
    bot_token=os.environ.get("BOT_TOKEN", ""),
)

DB_CHANNEL = -1004402060167


@app.on_message(filters.command("start"))
async def start_handler(client, message):
  await message.reply(
      "Hey there! 👋 I'm **Better Call Saf**, your movie search assistant."
      " Type any movie name to get started!"
  )


@app.on_message(filters.text & ~filters.command(["start"]))
async def movie_search(client, message):
  query = message.text.lower().strip()
  searching_msg = await message.reply("🔍 Searching channel library...")

  try:
    # Resolve chat entity first to completely prevent Peer id invalid errors
    chat_entity = await client.get_chat(DB_CHANNEL)

    query_words = query.split()
    matching_entries = []
    channel_messages = []

    # Fetch recent messages directly from your private channel
    async for db_msg in client.get_chat_history(chat_entity.id, limit=100):
      channel_messages.insert(0, db_msg)

    for i, db_msg in enumerate(channel_messages):
      text_content = (
          db_msg.caption
          if db_msg.caption
          else (db_msg.text if db_msg.text else "")
      )
      text_lower = text_content.lower()

      if query_words and all(word in text_lower for word in query_words):
        if text_content and text_content not in [m[1] for m in matching_entries]:
          matching_entries.append((i, text_content, channel_messages))

    if len(matching_entries) > 0:
      buttons = []
      for idx, title, _ in matching_entries[:10]:
        buttons.append(
            [
                InlineKeyboardButton(
                    f"🎬 {title[:35]}...", callback_data=f"send_{idx}"
                )
            ]
        )

      await searching_msg.edit_text(
          "I found these matching movies! Tap below to get your files:",
          reply_markup=InlineKeyboardMarkup(buttons),
      )
    else:
      await searching_msg.edit_text(
          "Sorry, that movie is not available in our library yet! 😢"
      )

  except Exception as e:
    await searching_msg.edit_text(f"Error scanning channel: {str(e)}")


@app.on_callback_query(filters.regex("^send_"))
async def send_selected_movie(client, callback_query):
  found_index = int(callback_query.data.split("_")[1])
  chat_id = callback_query.message.chat.id

  await callback_query.answer("Sending your movie files...")
  await callback_query.message.edit_text(
      "✅ Sending your files, please wait..."
  )

  try:
    chat_entity = await client.get_chat(DB_CHANNEL)
    channel_messages = []
    async for db_msg in client.get_chat_history(chat_entity.id, limit=100):
      channel_messages.insert(0, db_msg)

    if found_index < len(channel_messages):
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

    await callback_query.message.delete()
  except Exception as e:
    await callback_query.message.edit_text(
        f"Error sending file package: {str(e)}"
    )


if __name__ == "__main__":
  # Run Flask on port 10000 in background thread
  port = int(os.environ.get("PORT", 10000))
  threading.Thread(
      target=lambda: app_web.run(host="0.0.0.0", port=port), daemon=True
  ).start()

  # Run Pyrogram Bot directly
  app.run()
