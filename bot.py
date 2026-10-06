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

# Accurate movie entries with correct platform paths
MOVIE_PARTS = {
    "spiderman": [
        {
            "title": "Spider-Man: Brand New Day (2026)",
            "bingebox": "https://bingebox.ac/",
            "popcorn": "https://popcornmovies.ac/",
            "vivarium": "https://vivarium.su/",
        },
        {
            "title": "Spider-Man: No Way Home (2021)",
            "bingebox": "https://bingebox.ac/movie/634649",
            "popcorn": "https://popcornmovies.ac/movie/634649",
            "vivarium": "https://vivarium.su/",
        },
    ],
    "batman": [
        {
            "title": "The Batman (2022)",
            "bingebox": "https://bingebox.ac/movie/414906",
            "popcorn": "https://popcornmovies.ac/movie/414906",
            "vivarium": "https://vivarium.su/",
        },
        {
            "title": "The Dark Knight (2008)",
            "bingebox": "https://bingebox.ac/movie/155",
            "popcorn": "https://popcornmovies.ac/movie/155",
            "vivarium": "https://vivarium.su/",
        },
    ],
}


@app.on_message(filters.command("start"))
async def start_handler(client, message):
  await message.reply(
      "Hey there! 👋 I'm your Smart Streaming Assistant.\nType a movie name"
      " like `spiderman` or `batman` to select a part!"
  )


@app.on_message(filters.text & ~filters.command(["start"]))
async def movie_search(client, message):
  query = message.text.lower().strip()

  matched_key = None
  for key in MOVIE_PARTS:
    if key in query:
      matched_key = key
      break

  if matched_key:
    parts = MOVIE_PARTS[matched_key]
    buttons = []
    for idx, movie in enumerate(parts):
      buttons.append([
          InlineKeyboardButton(
              f"🎬 {movie['title']}", callback_data=f"part_{matched_key}_{idx}"
          )
      ])

    await message.reply(
        f"🔍 I found multiple parts for **{query.title()}**.\nPlease select the"
        " specific part you want to watch:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
  else:
    await message.reply(
        f"❌ Sorry, no parts found for `{query.title()}` yet. Try searching"
        " `spiderman` or `batman`!"
    )


@app.on_callback_query(filters.regex("^part_"))
async def select_movie_part(client, callback_query):
  data_parts = callback_query.data.split("_")
  key = data_parts[1]
  idx = int(data_parts[2])

  movie = MOVIE_PARTS[key][idx]

  keyboard = InlineKeyboardMarkup([
      [
          InlineKeyboardButton(
              "🎬 Watch on Bingebox", url=movie["bingebox"]
          )
      ],
      [
          InlineKeyboardButton(
              "🍿 Watch on Popcorn Movies", url=movie["popcorn"]
          )
      ],
      [
          InlineKeyboardButton(
              "🌐 Watch on Vivarium", url=movie["vivarium"]
          )
      ],
  ])

  await callback_query.message.edit_text(
      f"✨ **Selected:** {movie['title']}\n\nClick below to open the streaming"
      " page:",
      reply_markup=keyboard,
  )


if __name__ == "__main__":
  app.run()
