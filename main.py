import emoji
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

DAY_DICT = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}

COUNT = 0
CHANNEL = []
MESSAGES = []

CHANNEL_HANDLE = "@fodisnumberone"
CHANNEL_URL = "https://t.me/fodisnumberone"
BOT_TOKEN = "1414408039:AAFF_XI0DM1gINiPWcoBkxQnhQGteL-vomM"

# Stages
START, MENU, DELETE, ORIGIN, DAYS, TIME, PAX, REMARKS, END = range(9)


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
def start(update: Update, context: CallbackContext) -> None:

    keyboard = [
        [   InlineKeyboardButton("Main Menu", callback_data="menu")],

        ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    user = update.message.from_user

    context.user_data['username'] = user.username  # Changed from first and last name to username
    logger.info(f"User {user.first_name} started the conversation.")

    logger.info("User %s started the conversation.", user.first_name)

    # Send message with text and appended InlineKeyboard
    update.message.reply_text(text="*Looking for a meal buddy?*", parse_mode='Markdown', reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return START

def menu(update: Update, context: CallbackContext) -> int:
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("✍ Create Meal Session", callback_data="create")],
        [InlineKeyboardButton("🤝Join Meal Session", callback_data="join")],
        [InlineKeyboardButton("Delete", callback_data="delete")],
        [InlineKeyboardButton("🙋‍♂️🙋Help",callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)



    query.edit_message_text(text="*What do you want to do 🤔 ?*",
                            parse_mode='Markdown',
                            reply_markup=reply_markup)

    return MENU



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
    context.user_data['pax'] = query.data
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

def remarks(update: Update, context: CallbackContext) -> None:

    text = update.effective_message.text

    context.user_data['Remarks:'] = text
    logger.debug(f"\t{context.user_data['username']} remarked {text}")

    keyboard = [
        [
            InlineKeyboardButton("Confirm", callback_data="confirm")],
        [   InlineKeyboardButton("📃Main Menu", callback_data="main")],
        [   InlineKeyboardButton("🔙Back", callback_data="back")],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.effective_message.reply_text(f'*Just to confirm your session details:{facts_to_str(context.user_data)}*',parse_mode='Markdown', reply_markup=reply_markup)

    return END


def create(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Mon", callback_data="Monday"),
         InlineKeyboardButton("Tue", callback_data="Tuesday"),
         InlineKeyboardButton("Wed", callback_data="Wednesday"),
         InlineKeyboardButton("Thurs", callback_data="Thursday"),
         InlineKeyboardButton("Fri", callback_data="Friday"),
         InlineKeyboardButton("Sat", callback_data="Saturday"),
         InlineKeyboardButton("Sun", callback_data="Sunday")],
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

def delete(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Delete active meal sessions", callback_data="dams")],
        [InlineKeyboardButton("🔙Back", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="*Are you sure you want to delete your meal session?*",parse_mode= 'Markdown', reply_markup=reply_markup
    )

    return DELETE

def clear(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    event = Event(COUNT,
                  update.effective_message.from_user["username"],
                  context.user_data["days"],
                  context.user_data["time"],
                  context.user_data["pax"],
                  context.user_data["Remarks:"])
    del event

    keyboard = [
        [InlineKeyboardButton("📃Main Menu", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="*Session deleted*",parse_mode= 'Markdown', reply_markup=reply_markup
    )

    return ORIGIN

def help(update: Update, context: CallbackContext) -> None:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("📃Main Menu", callback_data="main")],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="*To find an existing session; click on join meal session at the main menu. To create a new session; click on create meal session at the main menu and input the neccessary details accordingly*",parse_mode= 'Markdown', reply_markup=reply_markup
    )

    return DAYS

def end(update: Update, context: CallbackContext) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over"""
    global COUNT
    query = update.callback_query
    text = update.effective_message.text
    context.user_data['choice'] = text
    logger.debug(f"\t{context.user_data['username']} has just {text}")

    query.edit_message_text('*Thank you for hosting a session!*',
                                        parse_mode='Markdown',
                                        )

    # Add event to CHANNEL
    event = Event(COUNT,
                  context.user_data['username'],
                  context.user_data["days"],
                  context.user_data["time"],
                  context.user_data["pax"],
                  context.user_data["Remarks:"])

    COUNT += 1
    add_to_channel(event, context)

    return ConversationHandler.END


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("1414408039:AAFF_XI0DM1gINiPWcoBkxQnhQGteL-vomM", use_context=True)
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
                CallbackQueryHandler(menu, pattern='^menu$'),
            ],
            MENU: [
                CallbackQueryHandler(create, pattern='^create$'),
                #MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), received_time),
                CallbackQueryHandler(join, pattern='^join$'),
                CallbackQueryHandler(delete, pattern='^delete$'),
                CallbackQueryHandler(help, pattern='^help$'),
            ],
            DELETE: [
                CallbackQueryHandler(clear, pattern='^dams$'),
                CallbackQueryHandler(menu, pattern='^back$'),
                CallbackQueryHandler(menu, pattern='^main$')
            ],
            ORIGIN: [
                CallbackQueryHandler(menu, pattern='^main$')
            ],
            DAYS: [
                CallbackQueryHandler(days, pattern='^Monday$'),
                CallbackQueryHandler(days, pattern='^Tuesday$'),
                CallbackQueryHandler(days, pattern='^Wednesday$'),
                CallbackQueryHandler(days, pattern='^Thursday$'),
                CallbackQueryHandler(days, pattern='^Friday$'),
                CallbackQueryHandler(days, pattern='^Saturday$'),
                CallbackQueryHandler(days, pattern='^Sunday$'),
                CallbackQueryHandler(menu, pattern='^main$')
            ],
            TIME: [
                MessageHandler(Filters.text & ~Filters.command, time),
                CallbackQueryHandler(create, pattern='^back$'),
                CallbackQueryHandler(menu, pattern='^main$')
            ],
            PAX: [
                CallbackQueryHandler(pax, pattern='^2$'),
                CallbackQueryHandler(pax, pattern='^3$'),
                CallbackQueryHandler(pax, pattern='^4$'),
                CallbackQueryHandler(pax, pattern='^5$'),
                CallbackQueryHandler(days, pattern='^back$'),
                CallbackQueryHandler(menu, pattern='^main$'),
            ],
            REMARKS: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), remarks),
                CallbackQueryHandler(time, pattern='^back$'),
                CallbackQueryHandler(start, pattern='^main$'),
            ],
            END: [
                CallbackQueryHandler(end, pattern='^confirm$'),
                CallbackQueryHandler(pax, pattern='^back$'),
                CallbackQueryHandler(start, pattern='^main$'),
            ]
        },
        fallbacks=[CommandHandler('start', start)],
    )

    # Add ConversationHandler to dispatcher that will be used for handling updates
    dispatcher.add_handler(conv_handler)

    # Initialise daily update
    updater.job_queue.run_daily(daily_update, datetime.time(2, 3, 00))  # To check again
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
