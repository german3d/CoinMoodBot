import os 
import sys
import datetime
import logging
import pandas as pd
import numpy as np
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from data_transfer.database import PSQLClient
from bot_utils import build_menu, send_chatbase_msg
from config import PATHS, TEXTS, TOKEN, REQUEST_PARAMS, MAIN_LIST, CRYPTO_LIST, HEROKU_INFO, PSQL_HEROKU_CONN_STRING


logging.basicConfig(format="%(asctime)s - %(name)s - {%(pathname)s:%(lineno)d} - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Initialize PSQL client to work with database
psql_client = PSQLClient(conn_string=PSQL_HEROKU_CONN_STRING)


def error(bot, update, error):
    logger.warning("Update {} caused error {}".format(update, error))
    
    
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text=TEXTS["start"],
                     reply_markup=main_keyboard)
    send_chatbase_msg(intent="start_menu", user_id=update.message.from_user.id)


def fb(bot, update, args):
    bot.send_message(chat_id=update.message.chat_id,
                     text=TEXTS["feedback_ok"],
                     reply_markup=back_keyboard)
    user_info = update.message.from_user
    comment = " ".join(args)
    psql_client.insert_user_feedback(comment=comment, user_info=user_info)
    send_chatbase_msg(intent="feedback_was_sent", user_id=update.message.from_user.id)
    
    
def action(bot, update):
    callback = update.callback_query
    callback_data = callback.data
    message_kwargs = {"message_id": callback.message.message_id,
                      "chat_id": callback.message.chat.id
                     }
    
    if callback_data=="📋 Crypto List":
        bot.edit_message_text(text=TEXTS["list"],
                              reply_markup=crypto_keyboard,
                              **message_kwargs)
        send_chatbase_msg(intent="crypto_list", user_id=callback.from_user.id)
        
    elif callback_data=="💸 Make a Donation":
        bot.edit_message_text(text=TEXTS["donate"],
                              reply_markup=back_keyboard,
                              **message_kwargs)
        send_chatbase_msg(intent="make_donation", user_id=callback.from_user.id)
        
    elif callback_data=="🏗 Future Improvements":
        bot.edit_message_text(text=TEXTS["plans"],
                              reply_markup=back_keyboard,
                              **message_kwargs)
        send_chatbase_msg(intent="future_improvements", user_id=callback.from_user.id)
        
    elif callback_data=="❓ What I Can Do":
        bot.edit_message_text(text=TEXTS["about"],
                              reply_markup=back_keyboard,
                              **message_kwargs)
        send_chatbase_msg(intent="what_i_can_do", user_id=callback.from_user.id)
        
    elif callback_data=="✏ Leave Feedback":
        bot.edit_message_text(text=TEXTS["feedback"],
                              reply_markup=back_keyboard,
                              **message_kwargs)
        send_chatbase_msg(intent="leave_feedback", user_id=callback.from_user.id)
        
    elif callback_data=="<< Back to Main":
        bot.edit_message_text(text=TEXTS["start"],
                              reply_markup=main_keyboard,
                              **message_kwargs)
        send_chatbase_msg(intent="back_to_main", user_id=callback.from_user.id)
        
    elif callback_data in CRYPTO_LIST:
        url = psql_client.get_last_asset_link(asset=callback_data)
        if url=="":
            logger.warning("File was not found: {}".format(callback_data))
            bot.edit_message_text(text=TEXTS["no_info"],
                                  reply_markup=back_keyboard,
                                  **message_kwargs)
            send_chatbase_msg(intent="file_was_not_found", user_id=callback.from_user.id)
        else: # send chart            
            bot.send_chat_action(action=telegram.ChatAction.TYPING, **message_kwargs)
            bot.send_photo(photo=url, **message_kwargs)
            send_chatbase_msg(intent="file_was_sent", user_id=callback.from_user.id)


# Create buttons
main_buttons =  [InlineKeyboardButton(text=bt, callback_data=bt) for bt in MAIN_LIST]
crypto_buttons = [InlineKeyboardButton(text=bt, callback_data=bt) for bt in sorted(CRYPTO_LIST)]
back_button = InlineKeyboardButton(text="<< Back to Main", callback_data="<< Back to Main")

# Create keyboards
main_keyboard = InlineKeyboardMarkup(build_menu(main_buttons, n_cols=1))
back_keyboard = InlineKeyboardMarkup(build_menu([back_button], n_cols=1))    
crypto_keyboard = InlineKeyboardMarkup(build_menu(crypto_buttons, n_cols=2, footer_buttons=[back_button]))


def main():

	# Connection parameters
    request_proxy = telegram.utils.request.Request(**REQUEST_PARAMS)
    
    # Testing bot instance
    bot = telegram.Bot(token=TOKEN, request=request_proxy)
    print(bot.get_me())
    
    # Initialize updater and dispatcher
    updater = Updater(token=TOKEN, request_kwargs=REQUEST_PARAMS)
    dispatcher = updater.dispatcher
    
    # Add handlers
    dispatcher.add_handler(CommandHandler(command="start", callback=start))
    dispatcher.add_handler(CommandHandler(command="fb", callback=fb, pass_args=True))
    dispatcher.add_handler(CallbackQueryHandler(callback=action))
    dispatcher.add_error_handler(error)

    # Start the bot
    #updater.start_polling(timeout=30)
    PORT = int(os.environ.get("PORT", "8443"))
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.set_webhook(HEROKU_INFO["app_url"] + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
