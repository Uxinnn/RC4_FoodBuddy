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
START, DAYS, TIME, PAX, REMARKS = range(5)

def start(update: Update, context: CallbackContext) -> None:
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    keyboard = [
        [
            InlineKeyboardButton("✍ Create Meal Session", callback_data="create")],
        [    InlineKeyboardButton("🤝Join Meal Session", callback_data="join")],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        user = update.message.from_user
    except AttributeError:
        update.callback_query.edit_message_text(text="*What do you want to do 🤔 ?*", parse_mode='Markdown', reply_markup=reply_markup)
        return START

    context.user_data['username'] = user.first_name + ' ' + user.last_name
    logger.info("User %s started the conversation.", user.first_name)
    # Send message with text and appended InlineKeyboard
    update.message.reply_text(text="*What do you want to do 🤔 ?*", parse_mode='Markdown', reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return START

def facts_to_str(user_data: Dict[str, str]) -> str:
    facts = list()

    for key, value in user_data.items():
        facts.append(f'{key} - {value}')

    return "\n".join(facts).join(['\n', '\n'])

def days(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    context.user_data['days'] = query.data
    keyboard = [
        [
            InlineKeyboardButton("📃Main Menu", callback_data="main")],
        [   InlineKeyboardButton("🔙Back", callback_data="back")],


    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="*Please indicate the timeframe 🕔 of the meal, following this example: 1500-1600*",parse_mode= 'Markdown',reply_markup=reply_markup)

    return TIME

def time(update: Update, context: CallbackContext) -> None:
    text = update.effective_message.text
    context.user_data['time'] = text
    keyboard = [
        [   InlineKeyboardButton("2", callback_data="2"),
            InlineKeyboardButton("3", callback_data="3"),
            InlineKeyboardButton("4", callback_data="4"),
            InlineKeyboardButton("5", callback_data="5")],
        [   InlineKeyboardButton("🔙Back", callback_data="back")],
        [   InlineKeyboardButton("📃Main Menu", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text(
        text="*Choose the max number 🔢 of pax*",parse_mode='Markdown', reply_markup=reply_markup
    )

    return PAX






def pax(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("🔙Back", callback_data="back")],
        [   InlineKeyboardButton("📃Main Menu", callback_data="main")],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="*Additional remarks such as location 🧭 and other preferences?*",parse_mode= 'Markdown',reply_markup=reply_markup)

    return REMARKS

def create(update: Update, context: CallbackContext) -> None:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [   InlineKeyboardButton("Mon", callback_data="mon"),
            InlineKeyboardButton("Tue", callback_data="tues"),
            InlineKeyboardButton("Wed", callback_data="wed"),
            InlineKeyboardButton("Thurs", callback_data="thurs"),
            InlineKeyboardButton("Fri", callback_data="fri"),
            InlineKeyboardButton("Sat", callback_data="sat"),
            InlineKeyboardButton("Sun", callback_data="sun")],
        [   InlineKeyboardButton("📃Main Menu", callback_data="main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="*Choose a day in the current academic week 📅:*",parse_mode= 'Markdown', reply_markup=reply_markup
    )
    return DAYS

def join(update: Update, context: CallbackContext) -> None:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("🧐Browse active sessions", url='https://t.me/test_channel12333')],
        [   InlineKeyboardButton("📃Main Menu", callback_data="main")],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="*Search🔍 for available sessions!*",parse_mode= 'Markdown', reply_markup=reply_markup
    )
    return DAYS

def end(update: Update, context: CallbackContext) -> None:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over"""
    text = update.effective_message.text
    context.user_data['choice'] = text
    keyboard = [
        [
            InlineKeyboardButton("🔙Back", callback_data="back")],
        [   InlineKeyboardButton("📃Main Menu", callback_data="main")],
        
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text('*Thank you for hosting a session!*',parse_mode='Markdown',reply_markup=reply_markup)
    return ConversationHandler.END


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("1414408039:AAFF_XI0DM1gINiPWcoBkxQnhQGteL-vomM", use_context=True)

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
            START: [
                CallbackQueryHandler(create, pattern='^create$'),
                #MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), received_time),
                CallbackQueryHandler(join, pattern='^join$')
            ],
            DAYS: [
                CallbackQueryHandler(days, pattern='^mon$'),
                CallbackQueryHandler(days, pattern='^tues$'),
                CallbackQueryHandler(days, pattern='^wed$'),
                CallbackQueryHandler(days, pattern='^thurs$'),
                CallbackQueryHandler(days, pattern='^fri$'),
                CallbackQueryHandler(days, pattern='^sat$'),
                CallbackQueryHandler(days, pattern='^sun$'),
                CallbackQueryHandler(start, pattern='^main$')
            ],
            TIME: [
                MessageHandler(Filters.text & ~Filters.command, time),
                CallbackQueryHandler(create, pattern='^back$'),
                CallbackQueryHandler(start, pattern='^main$')
            ],
            PAX: [
                CallbackQueryHandler(pax, pattern='^2$'),
                CallbackQueryHandler(pax, pattern='^3$'),
                CallbackQueryHandler(pax, pattern='^4$'),
                CallbackQueryHandler(pax, pattern='^5$'),
                CallbackQueryHandler(days, pattern='^back$'),
                CallbackQueryHandler(start, pattern='^main$'),
            ],
            REMARKS: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), end)
            ]
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
