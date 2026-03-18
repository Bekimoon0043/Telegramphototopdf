import os
import asyncio
from PIL import Image
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 🔑 Environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Flask app (Render needs this)
app = Flask(__name__)

# Telegram bot setup
application = ApplicationBuilder().token(BOT_TOKEN).build()
bot = Bot(token=BOT_TOKEN)

# Folder for files
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 📸 Handle image
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        image_path = f"{DOWNLOAD_FOLDER}/{photo.file_id}.jpg"
        pdf_path = f"{DOWNLOAD_FOLDER}/{photo.file_id}.pdf"

        # Download image
        await file.download_to_drive(image_path)

        # Convert to PDF
        image = Image.open(image_path).convert("RGB")
        image.save(pdf_path)

        # Send back PDF
        await update.message.reply_document(document=open(pdf_path, "rb"))

        # Cleanup
        os.remove(image_path)
        os.remove(pdf_path)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# 👋 Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Send image → get PDF instantly")

# Add handlers
application.add_handler(MessageHandler(filters.PHOTO, handle_image))
application.add_handler(MessageHandler(filters.COMMAND, start))

# 🔥 Webhook route (SYNC FIX)
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)

    # Run async safely
    asyncio.run(application.process_update(update))

    return "ok"

# Home route
@app.route("/")
def home():
    return "Bot is running!"
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Send image → get PDF")

application.add_handler(MessageHandler(filters.PHOTO, handle_image))
application.add_handler(MessageHandler(filters.COMMAND, start))

# Webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return "ok"

# Home route
@app.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
    )
