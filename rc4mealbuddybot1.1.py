import logging
import emoji
from typing import Dict

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
    MessageHandler,
    Filters
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Stages
FIRST, SECOND = range(2)
# Callback data
ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, ELEVEN, TWELVE, THIRTEEN, FOURTEEN, FIFTEEN, SIXTEEN, SEVENTEEN, EIGHTEEN, NINETEEN, TWENTY = range(20)



def start(update: Update, context: CallbackContext) -> None:
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    user = update.effective_message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    # Send message with text and appended InlineKeyboard
    keyboard = [
        [
            InlineKeyboardButton("✍ Create Meal Session", callback_data=str(ONE)),
            InlineKeyboardButton("🤝Join Meal Session", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text(text="*What do you want to do 🤔 ?*", parse_mode='Markdown', reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return FIRST

def facts_to_str(user_data: Dict[str, str]) -> str:
    facts = list()

    for key, value in user_data.items():
        facts.append(f'{key} - {value}')

    return "\n".join(facts).join(['\n', '\n'])

def time(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("📃Main Menu", callback_data=str(TEN)),
            InlineKeyboardButton("🔙Back", callback_data=str(ELEVEN)),

        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="*Please indicate the timeframe 🕔 of the meal, following this example: 1500-1600*",parse_mode= 'Markdown',reply_markup=reply_markup)

    return FIRST

def received_time(update: Update, context: CallbackContext) -> None:

    text = update.effective_message.text
    context.user_data['choice'] = text
    keyboard = [
        [   InlineKeyboardButton("2", callback_data=str(FOURTEEN)),
            InlineKeyboardButton("3", callback_data=str(FIFTEEN)),
            InlineKeyboardButton("4", callback_data=str(SIXTEEN)),
            InlineKeyboardButton("5", callback_data=str(SEVENTEEN))],
        [   InlineKeyboardButton("🔙Back", callback_data=str(EIGHTEEN)),
            InlineKeyboardButton("📃Main Menu", callback_data=str(TEN))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text(
        text="*Choose the max number 🔢 of pax*",parse_mode='Markdown', reply_markup=reply_markup
    )

    return SECOND






def pax(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("🔙Back", callback_data=str(NINETEEN)),
            InlineKeyboardButton("📃Main Menu", callback_data=str(TEN)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="*Additional remarks such as location 🧭 and other preferences?*",parse_mode= 'Markdown',reply_markup=reply_markup)

    return SECOND

def days(update: Update, context: CallbackContext) -> None:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [   InlineKeyboardButton("Mon", callback_data=str(THREE)),
            InlineKeyboardButton("Tue", callback_data=str(FOUR)),
            InlineKeyboardButton("Wed", callback_data=str(FIVE)),
            InlineKeyboardButton("Thurs", callback_data=str(SIX)),
            InlineKeyboardButton("Fri", callback_data=str(SEVEN)),
            InlineKeyboardButton("Sat", callback_data=str(EIGHT)),
            InlineKeyboardButton("Sun", callback_data=str(NINE))],
        [   InlineKeyboardButton("📃Main Menu", callback_data=str(TEN))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="*Choose a day in the current academic week 📅:*",parse_mode= 'Markdown', reply_markup=reply_markup
    )
    return FIRST

def join(update: Update, context: CallbackContext) -> None:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("🧐Browse active sessions", url='https://t.me/test_channel12333'),
            InlineKeyboardButton("📃Main Menu", callback_data=str(TEN)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="*Search🔍 for available sessions!*",parse_mode= 'Markdown', reply_markup=reply_markup
    )
    return FIRST

def end(update: Update, context: CallbackContext) -> None:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over"""
    text = update.effective_message.text
    context.user_data['choice'] = text
    keyboard = [
        [
            InlineKeyboardButton("🔙Back", callback_data=str(TWENTY)),
            InlineKeyboardButton("📃Main Menu", callback_data=str(TEN)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text('*Thank you for hosting a session!*',parse_mode='Markdown',reply_markup=reply_markup)
    return ConversationHandler.END


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("TOKEN", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [
                CallbackQueryHandler(days, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(time, pattern='^' + str(THREE) + '$'),
                CallbackQueryHandler(time, pattern='^' + str(FOUR) + '$'),
                CallbackQueryHandler(time, pattern='^' + str(FIVE) + '$'),
                CallbackQueryHandler(time, pattern='^' + str(SIX) + '$'),
                CallbackQueryHandler(time, pattern='^' + str(SEVEN) + '$'),
                CallbackQueryHandler(time, pattern='^' + str(EIGHT) + '$'),
                CallbackQueryHandler(time, pattern='^' + str(NINE) + '$'),
                CallbackQueryHandler(start, pattern='^' + str(TEN) + '$'),
                CallbackQueryHandler(days, pattern='^' + str(ELEVEN) + '$'),
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), received_time),
                CallbackQueryHandler(join, pattern='^' + str(TWO) + '$'),
            ],
            SECOND: [
                CallbackQueryHandler(pax, pattern='^' + str(FOURTEEN) + '$'),
                CallbackQueryHandler(pax, pattern='^' + str(FIFTEEN) + '$'),
                CallbackQueryHandler(pax, pattern='^' + str(SIXTEEN) + '$'),
                CallbackQueryHandler(pax, pattern='^' + str(SEVENTEEN) + '$'),
                CallbackQueryHandler(time, pattern='^' + str(EIGHTEEN) + '$'),
                CallbackQueryHandler(received_time, pattern='^' + str(NINETEEN) + '$'),
                CallbackQueryHandler(pax, pattern='^' + str(TWENTY) + '$'),
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), end)
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )


    # Add ConversationHandler to dispatcher that will be used for handling
    # updates


    dispatcher.add_handler(conv_handler)


    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
