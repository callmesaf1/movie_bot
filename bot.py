import os
import telebot
import requests

TOKEN = "830262327:AAENbiMm_BYDKDqXbvZYm5YK91PYgDDZtgE"
bot = telebot.TeleBot(TOKEN)

TMDB_API_KEY = "3a4e7e9aa297e7e0320849cbae4f6d67"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hey Saf! Send me any movie name, and I will fetch its details and watch links for you!")

@bot.message_handler(func=lambda message: True)
def search_movie(message):
    movie_title = message.text
    chat_id = message.chat.id
    
    sent_msg = bot.send_message(chat_id, f"🔍 Searching movie database for '{movie_title}'...")

    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_title}"
    response = requests.get(search_url).json()

    if response.get("results") and len(response["results"]) > 0:
        movie = response["results"][0]
        title = movie.get("title")
        year = movie.get("release_date", "N/A")[:4]
        rating = movie.get("vote_average")
        overview = movie.get("overview")
        poster_path = movie.get("poster_path")
        
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
        watch_link = f"https://www.google.com/search?q=watch+{title.replace(' ', '+')}+online"

        caption = (
            f"🎬 **{title}** ({year})\n"
            f"⭐ **Rating:** {rating}/10\n\n"
            f"📖 **Overview:** {overview}\n\n"
            f"🔗 **Where to Watch / Find:** [Click Here to Search & Stream]({watch_link})"
        )

        bot.delete_message(chat_id, sent_msg.message_id)
        if poster_url:
            bot.send_photo(chat_id, poster_url, caption=caption, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, caption, parse_mode="Markdown")
    else:
        bot.edit_message_text("❌ Movie not found in the database! Check the spelling and try again.", chat_id, sent_msg.message_id)

bot.infinity_polling()
