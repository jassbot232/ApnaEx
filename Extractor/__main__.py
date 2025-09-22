import os
import asyncio
import importlib
import signal
import threading
from flask import Flask
from pyrogram import idle
from Extractor.modules import ALL_MODULES

# -------------------------
# Flask app for Koyeb health check
# -------------------------
app = Flask(__name__)
PORT = int(os.environ.get("PORT", 8080))

@app.route("/")
def home():
    return "✅ Bot is running on Koyeb!"

def run_web():
    app.run(host="0.0.0.0", port=PORT)

# -------------------------
# Event Loop
# -------------------------
loop = asyncio.get_event_loop()
should_exit = asyncio.Event()

def shutdown():
    print("Shutting down gracefully...")
    loop.create_task(should_exit.set())

signal.signal(signal.SIGTERM, lambda s, f: shutdown())
signal.signal(signal.SIGINT, lambda s, f: shutdown())

# -------------------------
# Bot Boot
# -------------------------
async def sumit_boot():
    for all_module in ALL_MODULES:
        importlib.import_module("Extractor.modules." + all_module)

    print("» ʙᴏᴛ ᴅᴇᴘʟᴏʏ sᴜᴄᴄᴇssғᴜʟʟʏ ✨ 🎉")

    await idle()  # keeps Pyrogram bot alive
    print("» ɢᴏᴏᴅ ʙʏᴇ ! sᴛᴏᴘᴘɪɴɢ ʙᴏᴛ.")

# -------------------------
# Main Entry
# -------------------------
if __name__ == "__main__":
    # Flask ko background me start karo
    threading.Thread(target=run_web).start()

    try:
        loop.run_until_complete(sumit_boot())
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.close()
        print("Loop closed.")
