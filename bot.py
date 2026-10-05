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

# Dynamic background cache so you never lose files
channel_messages = []


@app.on_message(filters.command("start"))
async def start_handler(client, message):
  await message.reply(
      "Hey there! 👋 I'm **Better Call Saf**, your go-to movie search"
      " assistant. Type any movie name to get started!"
  )


@app.on_message(filters.chat(DB_CHANNEL))
async def track_channel_messages(client, message):
  channel_messages.append(message)
  # Expands buffer to remember up to 500 files/messages so nothing gets cut off
  if len(channel_messages) > 500:
    channel_messages.pop(0)


@app.on_message(filters.text & ~filters.command(["start"]))
async def movie_search(client, message):
  query = message.text.lower().strip()
  searching_msg = await message.reply("🔍 Searching for your movie...")

  found_index = -1
  for i, db_msg in enumerate(channel_messages):
    text_content = (
        db_msg.caption
        if db_msg.caption
        else (db_msg.text if db_msg.text else "")
    )
    if query in text_content.lower():
      found_index = i
      break

  if found_index != -1:
    # Send the main title card/poster
    main_msg = channel_messages[found_index]
    await main_msg.copy(chat_id=message.chat.id)

    # Automatically sweep and send ALL attached files underneath (up to 30+ files safely)
    sent_count = 0
    for j in range(found_index + 1, len(channel_messages)):
      if sent_count >= 30:  # Maximum cap to prevent spam limits
        break
      next_msg = channel_messages[j]
      next_text = (
          next_msg.caption
          if next_msg.caption
          else (next_msg.text if next_msg.text else "")
      )

      # Stop collecting if we hit a completely new text description card header
      if (
          next_text
          and ":" in next_text
          and ("english" in next_text.lower() or "rip" in next_text.lower())
          and len(next_text) < 150
      ):
        break

      await next_msg.copy(chat_id=message.chat.id)
      sent_count += 1
      # Brief pause between files to ensure Telegram delivers large bundles smoothly
      await asyncio.sleep(0.3)

    await searching_msg.delete()
  else:
    await searching_msg.edit_text(
        "Sorry, I couldn't find that movie in the database! 😢"
    )


if __name__ == "__main__":
  web_thread = threading.Thread(target=run_web)
  web_thread.daemon = True
  web_thread.start()

  app.run()
