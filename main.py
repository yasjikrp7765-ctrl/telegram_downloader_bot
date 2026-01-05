import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os

# ========= CONFIG =========
BOT_TOKEN = "8540992050:AAGmXIhb1yKXQH35c8YxGtoTGqCsfztxIk8"

bot = telebot.TeleBot(BOT_TOKEN)
user_links = {}

# ========= START =========
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Welcome!\n\n"
        "📥 Video / 🎵 Audio / 📝 Caption / 🚀 Fast Download\n\n"
        "👉 Koi bhi PUBLIC video link bhejo"
    )

# ========= LINK =========
@bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
def get_link(message):
    user_links[message.chat.id] = message.text

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton("🎥 Video", callback_data="video"),
        InlineKeyboardButton("🎵 Audio", callback_data="audio")
    )
    kb.row(
        InlineKeyboardButton("📝 Caption", callback_data="caption"),
        InlineKeyboardButton("🚀 Fast Download", callback_data="fast")
    )

    bot.send_message(message.chat.id, "👇 Option select karo:", reply_markup=kb)

# ========= BUTTONS =========
@bot.callback_query_handler(func=lambda call: True)
def buttons(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)

    if not url:
        bot.answer_callback_query(call.id, "Link dobara bhejo")
        return

    if call.data == "video":
        download_video(chat_id, url)

    elif call.data == "audio":
        download_audio(chat_id, url)

    elif call.data == "caption":
        send_caption(chat_id, url)

    elif call.data == "fast":
        fast_link(chat_id, url)

# ========= FAST LINK =========
def fast_link(chat_id, url):
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            direct = info.get("url")

        bot.send_message(chat_id, f"🚀 Fast Download Link:\n{direct}")
    except:
        bot.send_message(chat_id, "❌ Fast link nahi mila")

# ========= VIDEO =========
def download_video(chat_id, url):
    try:
        ydl_opts = {
            "format": "best[filesize<50M]",
            "outtmpl": "video.mp4",
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open("video.mp4", "rb") as f:
            bot.send_video(chat_id, f)

        os.remove("video.mp4")

    except:
        bot.send_message(chat_id, "❌ Video download fail")

# ========= AUDIO =========
def download_audio(chat_id, url):
    try:
        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": "audio.%(ext)s",
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            file = ydl.prepare_filename(info)

        with open(file, "rb") as f:
            bot.send_audio(chat_id, f)

        os.remove(file)

    except:
        bot.send_message(chat_id, "❌ Audio error")

# ========= CAPTION =========
def send_caption(chat_id, url):
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        cap = info.get("description", "❌ Caption nahi mila")
        bot.send_message(chat_id, cap[:4000])

    except:
        bot.send_message(chat_id, "❌ Caption error")

# ========= RUN =========
bot.polling(none_stop=True)
