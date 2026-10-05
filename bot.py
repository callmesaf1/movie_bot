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


@app.on_message(filters.command("start"))
async def start_handler(client, message):
  await message.reply(
      "Hey there! 👋 I'm **Better Call Saf**, your go-to movie search"
      " assistant. Type any movie name to get started!"
  )


@app.on_message(filters.text & ~filters.command(["start"]))
async def movie_search(client, message):
  query = message.text.lower().strip()
  searching_msg = await message.reply("🔍 Searching for your movie...")

  try:
    found_any = False
    sent_count = 0
    target_found = False

    # Scan recent messages directly from your database channel on the fly
    async for db_msg in client.search_global_messages(query, limit=10):
      # Filter for messages originating from your database channel
      if str(db_msg.chat.id) in [str(DB_CHANNEL), "-1004402060167", "BetterCallSafDB"]:
        target_found = True
        break

    # Alternative direct scan through history if global search misses channel context
    if not target_found:
      matched_msg = None
      following_msgs = []
      
      async for db_msg in client.get_chat_history(DB_CHANNEL, limit=100):
        text_content = (
            db_msg.caption
            if db_msg.caption
            else (db_msg.text if db_msg.text else "")
        )
        if query in text_content.lower():
          matched_msg = db_msg
          break

      if matched_msg:
        found_any = True
        await matched_msg.copy(chat_id=message.chat.id)
        
        # Now pull all subsequent files following this match in the channel history
        async for db_msg in client.get_chat_history(DB_CHANNEL, limit=50):
          if db_msg.id < matched_msg.id and (matched_msg.id - db_msg.id) <= 20:
            following_msgs.append(db_msg)

        # Sort them in chronological order so they send top-to-bottom
        following_msgs.sort(key=lambda x: x.id)

        for next_msg in following_msgs:
          if sent_count >= 20: # Allows up to 20 files per movie safely!
            break
          await next_msg.copy(chat_id=message.chat.id)
          sent_count += 1
          await asyncio.sleep(0.3)

    if not found_any and not target_found:
      await searching_msg.edit_text(
          "Sorry, I couldn't find that movie in the database! 😢"
      )
    else:
      await searching_msg.delete()

  except Exception as e:
    await searching_msg.edit_text(f"Error: {str(e)}")


if __name__ == "__main__":
  web_thread = threading.Thread(target=run_web)
  web_thread.daemon = True
  web_thread.start()

  app.run()
