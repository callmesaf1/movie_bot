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

# Store message IDs and their sequence in the database channel
channel_messages = []


@app.on_message(filters.command("start"))
async def start_handler(client, message):
  await message.reply(
      "Hey there! 👋 I'm **Better Call Saf**, your go-to movie search"
      " assistant. Type any movie name to get started!"
  )


# Automatically keep track of messages posted in the database channel
@app.on_message(filters.chat(DB_CHANNEL))
async def track_channel_messages(client, message):
  channel_messages.append(message)
  # Keep only the last 200 messages in memory to stay lightweight
  if len(channel_messages) > 200:
    channel_messages.pop(0)


@app.on_message(filters.text & ~filters.command(["start"]))
async def movie_search(client, message):
  query = message.text.lower().strip()
  searching_msg = await message.reply("🔍 Searching for your movie...")

  found_index = -1
  # Search for the message containing the movie title
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
    # Send the main title/poster message found
    main_msg = channel_messages[found_index]
    await main_msg.copy(chat_id=message.chat.id)

    # Automatically grab and send the next 3 messages (your video files) that follow it!
    sent_count = 0
    for j in range(found_index + 1, len(channel_messages)):
      if sent_count >= 3:
        break
      next_msg = channel_messages[j]
      # Stop if we hit another movie title card
      next_text = (
          next_msg.caption
          if next_msg.caption
          else (next_msg.text if next_msg.text else "")
      )
      if "Spiderman" in next_text or "amazon prime" in next_text.lower():
        # If it's another title header, let's look closer, but for now let's copy consecutive items
        pass

      await next_msg.copy(chat_id=message.chat.id)
      sent_count += 1

    await searching_msg.delete()
  else:
    await searching_msg.edit_text(
        "Sorry, I couldn't find that movie in the database! 😢\n\n*Tip:* Try"
        " posting or forwarding the movie card again in `@BetterCallSafDB` so"
        " the bot registers it."
    )


if __name__ == "__main__":
  web_thread = threading.Thread(target=run_web)
  web_thread.daemon = True
  web_thread.start()

  app.run()
