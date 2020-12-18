import logging
from typing import Dict, Union
import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, CallbackContext,
                          MessageHandler, Filters)
from telegram.error import BadRequest
from base_classes import Event, ChannelEntry


# Enable logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DAY_DICT = {"mon": 0, "tues": 1, "wed": 2, "thurs": 3, "fri": 4, "sat": 5, "sun": 6}

COUNT = 0
CHANNEL = []
MESSAGES = []

CHANNEL_HANDLE = "@test_channel1233"
CHANNEL_URL = "https://t.me/test_channel1233"
BOT_TOKEN = "insert token here"

# Stages
START, DAYS, TIME, PAX, REMARKS = range(5)
TIME_ZONE = pytz.timezone("Asia/Singapore")
DAILY_UPDATE_TIME = datetime.time(hour=0, minute=0, second=0, tzinfo = TIME_ZONE) 


####################################
# Functions to interact with store #
####################################
def init_channel(updater: Updater) -> None:
    logger.debug("Initializing channel...")

    date = datetime.datetime.today()
    while len(CHANNEL) != 7:
        day = date.strftime('%A')
        logging.debug(f"\tCreating entry for {day}...")
        msg = updater.bot.send_message(text=f"<b>{day}</b>\n", chat_id=CHANNEL_HANDLE, parse_mode=ParseMode.HTML)
        CHANNEL.append(ChannelEntry(day, []))
        MESSAGES.append(msg)
        date += datetime.timedelta(days=1)


def update_channel(context: Union[CallbackContext, Updater]) -> None:
    logger.debug("Updating Channel...")
    for entry in CHANNEL:
        msg = MESSAGES[CHANNEL.index(entry)]
        logger.debug(f"\t{entry.day} updating...")
        # Will raise error if message is not different, FIND WAY TO RECTIFY!
        try:
            context.bot.edit_message_text(chat_id=msg.chat_id,
                                          message_id=msg.message_id,
                                          text=str(entry),
                                          parse_mode=ParseMode.HTML)
        except BadRequest:
            continue


def add_to_channel(event: Event, context: CallbackContext) -> None:
    idx = (DAY_DICT[event.day] - datetime.datetime.today().weekday()) % 7
    CHANNEL[idx].add_event(event)
    msg = MESSAGES[idx]
    logger.debug(f"Adding @{event.handle}'s event to index {idx}...")
    context.bot.edit_message_text(chat_id=msg.chat_id,
                                  message_id=msg.message_id,
                                  text=str(CHANNEL[idx]),
                                  parse_mode=ParseMode.HTML)


def daily_update(callback: CallbackContext) -> None:
    logger.debug("Running daily update...")
    channel_copy = CHANNEL.copy()
    day = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%A')
    for i in range(len(CHANNEL)-1):
       CHANNEL[i] = channel_copy[i+1]
    CHANNEL[6] = ChannelEntry(day, [])
    update_channel(callback)
    print_channel()


def print_channel() -> None:
    txt = ""
    for day in CHANNEL:
        txt += (str(day) + "\n")
    logger.debug(txt)


#######
# Bot #
#######
def start(update: Update, context: CallbackContext) -> int:
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    keyboard = [
        [InlineKeyboardButton("✍ Create Meal Session", callback_data="create")],
        [InlineKeyboardButton("🤝Join Meal Session", callback_data="join")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        user = update.message.from_user
    except AttributeError:
        update.callback_query.edit_message_text(text="*What do you want to do 🤔 ?*",
                                                parse_mode='Markdown',
                                                reply_markup=reply_markup)
        return START

    context.user_data['username'] = user.username  # Changed from first and last name to username
    logger.info(f"User {user.first_name} started the conversation.")
    # Send message with text and appended InlineKeyboard
    update.message.reply_text(text="*What do you want to do 🤔 ?*",
                              parse_mode='Markdown',
                              reply_markup=reply_markup)
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
    logger.debug(f"\t{context.user_data['username']} chose {query.data}")
    keyboard = [
        [InlineKeyboardButton("📃Main Menu", callback_data="main")],
        [InlineKeyboardButton("🔙Back", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="*Please indicate the timeframe 🕔 of the meal, following this example: 1500-1600*",
                            parse_mode='Markdown',
                            reply_markup=reply_markup
                            )
    return TIME


def time(update: Update, context: CallbackContext) -> int:
    text = update.effective_message.text
    context.user_data['time'] = text
    logger.debug(f"\t{context.user_data['username']} chose {text}")
    keyboard = [
        [InlineKeyboardButton("2", callback_data="2"),
         InlineKeyboardButton("3", callback_data="3"),
         InlineKeyboardButton("4", callback_data="4"),
         InlineKeyboardButton("5", callback_data="5")],
        [InlineKeyboardButton("🔙Back", callback_data="back")],
        [InlineKeyboardButton("📃Main Menu", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text(text="*Choose the max number 🔢 of pax*",
                                        parse_mode='Markdown',
                                        reply_markup=reply_markup
                                        )
    return PAX


def pax(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("🔙Back", callback_data="back")],
        [InlineKeyboardButton("📃Main Menu", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="*Additional remarks such as location 🧭 and other preferences?*",
                            parse_mode='Markdown',
                            reply_markup=reply_markup
                            )
    return REMARKS


def create(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Mon", callback_data="mon"),
         InlineKeyboardButton("Tue", callback_data="tues"),
         InlineKeyboardButton("Wed", callback_data="wed"),
         InlineKeyboardButton("Thurs", callback_data="thurs"),
         InlineKeyboardButton("Fri", callback_data="fri"),
         InlineKeyboardButton("Sat", callback_data="sat"),
         InlineKeyboardButton("Sun", callback_data="sun")],
        [InlineKeyboardButton("📃Main Menu", callback_data="main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="*Choose a day in the current academic week 📅:*",
                            parse_mode='Markdown',
                            reply_markup=reply_markup
                            )
    return DAYS


def join(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    logger.debug(f"\t{context.user_data['username']} wants to join a session")
    keyboard = [
        [InlineKeyboardButton("🧐Browse active sessions", url=CHANNEL_URL)],
        [InlineKeyboardButton("📃Main Menu", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="*Search🔍 for available sessions!*",
                            parse_mode="Markdown",
                            reply_markup=reply_markup
                            )
    return DAYS


def end(update: Update, context: CallbackContext) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over"""
    global COUNT
    text = update.effective_message.text
    context.user_data['choice'] = text
    logger.debug(f"\t{context.user_data['username']} remarked {text}")
    keyboard = [
        [InlineKeyboardButton("🔙Back", callback_data="back")],
        [InlineKeyboardButton("📃Main Menu", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text('*Thank you for hosting a session!*',
                                        parse_mode='Markdown',
                                        reply_markup=reply_markup
                                        )

    # Add event to CHANNEL
    event = Event(COUNT,
                  update.message.from_user["username"],
                  context.user_data["days"],
                  context.user_data["time"],
                  "food place")
    COUNT += 1
    add_to_channel(event, context)

    return ConversationHandler.END


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN, use_context=True)
    init_channel(updater)

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
                # MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), received_time),
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

    # Add ConversationHandler to dispatcher that will be used for handling updates
    dispatcher.add_handler(conv_handler)

    # Initialise daily update
    updater.job_queue.run_daily(daily_update, DAILY_UPDATE_TIME)  # To check again
    updater.job_queue.start()
    logger.debug(f"Daily updates schedule: {updater.job_queue.jobs()[0].next_t}")
    # updater.job_queue.jobs()[0].run(dispatcher)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
