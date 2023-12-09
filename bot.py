import logging
import os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from msport import msport_create_ticket
from sportybet import parse_ticket_to_msport

PORT = int(os.environ.get('PORT', '8443'))
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
WORKER_URL = os.environ.get('WORKER_URL', "")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

last_commands = {}


def start(update, context):
    """Message user on /start"""
    user_ = update.message.from_user
    context.bot.send_message(
        chat_id=user_['id'],
        text="welcome"
    )


def check_games(update, context):
    chat_id = update.effective_chat.id
    print(chat_id)
    last_command = last_commands.get(chat_id)

    if last_command == "convert_sporty_code":
        print("started")
        update.message.reply_text(f"Started conversion...")
        sportybet_code = update.message.text
        msport_parsed_selections = parse_ticket_to_msport(sportybet_code)
        msport_ticket = msport_create_ticket(msport_parsed_selections)

        update.message.reply_text(f"Your msport code is: {msport_ticket}")


def convert_game(update, context):
    chat_id = update.effective_chat.id
    last_commands[chat_id] = "convert_sporty_code"
    update.message.reply_text("Please enter a sportybet code: ")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


updater = Updater(TOKEN, use_context=True)


# job = updater.job_queue

# def game_update_callback(context: telegram.ext.CallbackContext):
#     check_if_game_has_changed()


# job.run_repeating(game_update_callback, 30)


def main():
    dp = updater.dispatcher  # get dispatcher

    dp.add_handler(CommandHandler('start', start))
    # dp.add_handler(CommandHandler('echo', check_games))
    dp.add_handler(CommandHandler('convert_sporty_code', convert_game))
    # dp.add_handler(CommandHandler('check_bet', get_user_game))
    # dp.add_handler(CommandHandler('create_issue', create_issue))

    dp.add_handler(MessageHandler(Filters.text, check_games))
    dp.add_error_handler(error)
    # updater.start_polling()

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN,
                          webhook_url=WORKER_URL + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
