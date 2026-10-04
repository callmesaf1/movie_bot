import os
import telebot
import requests

# Your bot token from BotFather
TOKEN = "830262327:AAENbiMm_BYDKDqXbvZYm5YK91PYgDDZtgE"
bot = telebot.TeleBot(TOKEN)

# Free OMDb API key for fetching movie info
OMDB_API_KEY = "a_free_key_placeholder" # You can grab a free key from omdbapi.com

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hey Saf! Send me the name of a movie, and I will find the link for you.")

@bot.message_handler(func=lambda message: True)
def search_movie(message):
    movie_title = message.text
    chat_id = message.chat.id
    
    sent_msg = bot.send_message(chat_id, f"🔍 Searching for '{movie_title}'...")

    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"
    response = requests.get(url).json()

    if response.get("Response") == "True":
        title = response.get("Title")
        year = response.get("Year")
        rating = response.get("imdbRating")
        genre = response.get("Genre")
        poster = response.get("Poster")
        
        movie_link = f"https://example.com/download/{title.lower().replace(' ', '-')}"

        caption = (
            f"🎬 **{title}** ({year})\n"
            f"⭐ **Rating:** {rating}/10\n"
            f"🎭 **Genre:** {genre}\n\n"
            f"🔗 **Download Link:** [Click Here to Watch/Download]({movie_link})"
        )

        bot.delete_message(chat_id, sent_msg.message_id)
        bot.send_photo(chat_id, poster, caption=caption, parse_mode="Markdown")
    else:
        bot.edit_message_text("❌ Movie not found! Please check the spelling and try again.", chat_id, sent_msg.message_id)

# Start polling for cloud deployment
bot.infinity_polling()