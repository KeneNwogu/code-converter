import logging
import random
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ContextTypes
from betnaija import get_games, bet9ja_create_ticket


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = '1829567016:AAHlWAPxOHyqTMrxg_k3Rm1o7tIFHwL09G8'

updater = Updater(BOT_TOKEN, use_context=True)

def start(update: Update, context):
    """Start command"""
    update.message.reply_text(
        "🔵 *Bet9ja Code Randomizer Bot*\n\n"
        "📋 *How to use:*\n"
        "Send: `CODE` or `CODE NUMBER`\n\n"
        "*Examples:*\n"
        "• `3MQSVBL` - Random selection\n"
        "• `3MQSVBL 5` - Select 5 games\n"
        "• `ABC123 3` - Select 3 games\n\n"
        "*Commands:*\n"
        "/start - This message\n"
        "/help - Help info",
        parse_mode='Markdown'
    )

def help_command(update: Update, context):
    """Help command"""
    update.message.reply_text(
        "📖 *Help - Bet9ja Randomizer*\n\n"
        "*Format:*\n"
        "`CODE` - Random selection\n"
        "`CODE 5` - Select exactly 5 games\n\n"
        "*Examples:*\n"
        "• `3MQSVBL` - Random\n"
        "• `3MQSVBL 5` - Select 5\n"
        "• `ABC123 3` - Select 3\n\n"
        "⚠️ Make sure code is valid!",
        parse_mode='Markdown'
    )

def process_code(update: Update, context):
    """Process booking code"""
    logger.info(f"Start processing code")
    parts = update.message.text.strip().split()
    if not parts:
        update.message.reply_text("❌ Send a booking code!")
        return
    
    code = parts[0].upper()
    num = None
    
    if len(parts) > 1:
        try:
            num = int(parts[1])
        except:
            update.message.reply_text("❌ Invalid number!")
            return
    
    logger.info(f"Processing code: {code}, num: {num}")
    msg = update.message.reply_text("⏳ Processing your Bet9ja code...")
    
    try:
        # Get games
        games = get_games(code)
        total = len(games)
        
        if total == 0:
            msg.edit_text("❌ No games found!")
            return
        
        # Determine number to select
        if num is None:
            num = random.randint(2, max(2, total))
        
        if num > total:
            msg.edit_text(f"❌ Cannot select {num} games.\nCode has only {total} games!")
            return
        
        if num < 1:
            msg.edit_text("❌ Select at least 1 game!")
            return
        
        # Randomly select games
        selected = random.sample(games, num)
        
        # Create new booking code
        new_code = bet9ja_create_ticket(selected)
        
        # Calculate odds
        # total_odds = calculate_total_odds(selected)
        
        # Format response
        resp = "🔵 *BET9JA*\n\n"
        resp += f"✅ Original: `{code}`\n"
        resp += f"🎲 Selected {num} out of {total} games\n\n"
        
        resp += "*Selected Games:*\n"
        for i, g in enumerate(selected, 1):
            resp += f"{i}. {g['E_NAME']}\n"
            resp += f"   └ {g['M_NAME']}: {g['SGN']} @ {g['odds_display']}\n"
        
        # resp += f"\n📊 Total Odds: *{total_odds}*\n\n"
        resp += f"🎫 *New Booking Code:*\n`{new_code}`\n\n"
        resp += "✨ Use this code on Bet9ja!"
        
        msg.edit_text(resp, parse_mode='Markdown')
        logger.info(f"Success! New code: {new_code}")
        
    except ValueError as e:
        logger.error(f"ValueError: {e}")
        msg.edit_text(f"❌ Error: {str(e)}")
    except Exception as e:
        logger.error(f"Exception: {e}", exc_info=True)
        msg.edit_text(f"❌ An error occurred: {str(e)}\n\nPlease try again.")


def error_handler(update: Update, context):
    """Global error handler"""
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)


def main():
    """Start the bot"""
    # app = Application.builder().token(BOT_TOKEN).build()
    app = updater.dispatcher
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(Filters.text, process_code))
    app.add_error_handler(error_handler)
    
    logger.info("🔵 BET9JA BOT STARTED - Ready to process codes!")
    
    updater.start_polling()

if __name__ == '__main__':
    main()