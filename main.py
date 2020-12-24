import emoji
import logging
from typing import Dict, List, Union
import datetime
import pytz
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

# Stages of conversation
MENU, OPTIONS, DELETE, DAYS, TIME, PAX, REMARKS, CONFIRM, END, RESTART = range(10)


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


# Refreshes channel
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


# Adds a new entry to the channel
def add_to_channel(event: Event, context: CallbackContext) -> None:
    idx = (DAY_DICT[event.day] - datetime.datetime.today().weekday()) % 7
    CHANNEL[idx].add_event(event)
    msg = MESSAGES[idx]
    logger.debug(f"Adding @{event.handle}'s event to index {idx}...")
    context.bot.edit_message_text(chat_id=msg.chat_id,
                                  message_id=msg.message_id,
                                  text=str(CHANNEL[idx]),
                                  parse_mode=ParseMode.HTML)


# Returns index of channel entry in CHANNEL with entry of input id
def get_channel_index(id: int) -> int:
    for i in range(len(CHANNEL)):
        if CHANNEL[i].check_event_id(id):
            return i
    return -1


# Deletes event with input id from channel
def del_from_channel(id: int, context: CallbackContext) -> bool:
    channel_idx = get_channel_index(id)
    ret = CHANNEL[channel_idx].del_event(id)
    msg = MESSAGES[channel_idx]
    print(ret)
    logger.debug(f"Deleting index {id} event...")
    context.bot.edit_message_text(chat_id=msg.chat_id,
                                  message_id=msg.message_id,
                                  text=str(CHANNEL[channel_idx]),
                                  parse_mode=ParseMode.HTML)

    return ret

# Get events associated with input user handle
def get_user_events(user: str) -> List[Event]:
    user_events = []
    for entry in CHANNEL:
        user_events.extend(entry.get_user_events(user))
    return user_events


# Updates channel everyday
def daily_update(callback: CallbackContext) -> None:
    logger.debug("Running daily update...")
    channel_copy = CHANNEL.copy()
    day = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%A')
    for i in range(len(CHANNEL)-1):
       CHANNEL[i] = channel_copy[i+1]
    CHANNEL[6] = ChannelEntry(day, [])
    update_channel(callback)
    print_channel()


# Helper function to print channel contents to logger
def print_channel() -> None:
    txt = ""
    for day in CHANNEL:
        txt += (str(day) + "\n")
    logger.debug(txt)


#######
# Bot #
#######

# First function when users types in /start & logs users' telegram handle
def start(update: Update, context: CallbackContext) -> None:

    keyboard = [
        [InlineKeyboardButton("Yes! Lets Go!", callback_data="menu")],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    user = update.message.from_user

    context.user_data['Telegram Handle:'] = user.username  # Changed from first and last name to username
    logger.info(f"User {user.first_name} started the conversation.")

    logger.info("User %s started the conversation.", user.first_name)

    update.message.reply_text(text="*Looking for meal buddies?🙆‍♂️🙆‍♀️*",
                              parse_mode='Markdown',
                              reply_markup=reply_markup
                              )

    return MENU

def menu(update: Update, context: CallbackContext) -> int:
    """Send message on `/start`."""
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("✍ Create Meal Session", callback_data="create")],
        [InlineKeyboardButton("🤝Join Meal Session", callback_data="join")],
        [InlineKeyboardButton("❌Delete Session", callback_data="delete")],
        [InlineKeyboardButton("🙋‍♂️🙋Help", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text="*What do you want to do 🤔 ?*",
                            parse_mode="Markdown",
                            reply_markup=reply_markup
                            )

    return OPTIONS

# Allows logged user_data to be printed as string
def facts_to_str(user_data: Dict[str, str]) -> str:
    facts = list()
    for key, value in user_data.items():
        facts.append(f'{key} - {value}')

    return "\n".join(facts).join(['\n', '\n'])

###########################
# CREATE SESSION SEQUENCE #
###########################

# User to pick the day for the session
def days(update: Update, context: CallbackContext) -> int:
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
    query.edit_message_text(text="*Please choose a day in the current academic week 📅:*",
                            parse_mode="Markdown",
                            reply_markup=reply_markup
                            )
    return TIME

# User to input the time of the meal session after selecting the day
def time(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    context.user_data['Day:'] = query.data
    logger.debug(f"\t{context.user_data['Telegram Handle:']} chose {query.data}")
    keyboard = [
        [InlineKeyboardButton("📃Main Menu", callback_data="main")],
        [InlineKeyboardButton("🔙Back", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="*Please indicate the time 🕔 of the meal, following this format: 1500*",
                            parse_mode="Markdown",
                            reply_markup=reply_markup
                            )
    return PAX

# User to select maximum numer of pax after inputing time
def pax(update: Update, context: CallbackContext) -> int:
    text = update.effective_message.text
    context.user_data['Time:'] = text
    logger.debug(f"\t{context.user_data['Telegram Handle:']} chose {text}")
    keyboard = [
        [InlineKeyboardButton("2", callback_data="2"),
         InlineKeyboardButton("3", callback_data="3"),
         InlineKeyboardButton("4", callback_data="4"),
         InlineKeyboardButton("5", callback_data="5"),
         InlineKeyboardButton("6", callback_data="6"),
         InlineKeyboardButton("7", callback_data="7")],
        [InlineKeyboardButton("🔙Back", callback_data="back")],
        [InlineKeyboardButton("📃Main Menu", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text(text="*Choose the max number 🔢 of people (excluding yourself) for the meal:*",
                                        parse_mode="Markdown",
                                        reply_markup=reply_markup
                                        )
    return REMARKS

# User to input other remarks after selecting max number of pax
def remarks(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    context.user_data['Pax:'] = query.data
    keyboard = [
        [InlineKeyboardButton("🔙Back", callback_data="back")],
        [InlineKeyboardButton("📃Main Menu", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="*Please indicate the location 🧭 of the meal and other preferences*",
                            parse_mode="Markdown",
                            reply_markup=reply_markup
                            )
    return CONFIRM

# User to confirm session details before the bot sends to channel
def confirm(update: Update, context: CallbackContext) -> None:
    text = update.effective_message.text

    context.user_data['Remarks:'] = text
    logger.debug(f"\t{context.user_data['Telegram Handle:']} remarked {text}")

    keyboard = [
        [InlineKeyboardButton("✔Confirm", callback_data="confirm")],
        [InlineKeyboardButton("📃Main Menu", callback_data="main")],
        [InlineKeyboardButton("🔙Back", callback_data="back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.effective_message.reply_text(f'*Please confirm your session details:{facts_to_str(context.user_data)}*',
                                        parse_mode="Markdown",
                                        reply_markup=reply_markup
                                        )

    return END

# Bot sends session details to channel after confirmation
def end(update: Update, context: CallbackContext) -> int:
    global COUNT
    query = update.callback_query
    text = update.effective_message.text
    context.user_data['choice'] = text
    logger.debug(f"\t{context.user_data['Telegram Handle:']} has just confirmed the following details:{text}")
    # Add event to CHANNEL
    event = Event(COUNT,
                  context.user_data['Telegram Handle:'],
                  context.user_data['Day:'],
                  context.user_data['Time:'],
                  context.user_data['Pax:'],
                  context.user_data['Remarks:'])

    COUNT += 1
    add_to_channel(event, context)


    keyboard = [
            [InlineKeyboardButton("📃Main Menu", callback_data="main")],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text('*Session created successfully! Thank you for hosting a session!😊*',
                            parse_mode='Markdown',
                            reply_markup=reply_markup
                            )


    return RESTART

############################
# JOINING SESSION SEQUENCE #
############################

def join(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    logger.debug(f"\t{context.user_data['Telegram Handle:']} wants to join a session")
    keyboard = [
        [InlineKeyboardButton("🧐Browse active sessions", url=CHANNEL_URL)],
        [InlineKeyboardButton("📃Main Menu", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="*Search🔍 for available sessions!*",
                            parse_mode="Markdown",
                            reply_markup=reply_markup
                            )
    return MENU

#############################
# DELETING SESSION SEQUENCE #
#############################

def delete(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    #Backend function that lists user's events to be inserted here


    keyboard = [
        [InlineKeyboardButton("1st Session", callback_data="I0")],
        [InlineKeyboardButton("2nd Session", callback_data="I1")],
        [InlineKeyboardButton("3rd Session", callback_data="I2")],
        [InlineKeyboardButton("4th Session", callback_data="I3")],
        [InlineKeyboardButton("🔙Back", callback_data="back")],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
    text=f"*Which of the following sessions do you want to delete? \n {event_str}*",
    parse_mode='Markdown',
    reply_markup=reply_markup
    )


    return DELETE

# Deletes first session created by user
def clear0(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    #Backend delete function to be inserted here

    keyboard = [
        [InlineKeyboardButton("📃Main Menu", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="*Session deleted successfully!*",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

    return RESTART
# Deletes second session created by user
def clear1(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    #Backend delete function to be inserted here

    keyboard = [
        [InlineKeyboardButton("📃Main Menu", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="*Session deleted successfully!*",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

    return RESTART

# Deletes third session created by user
def clear2(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    #Backend delete function to be inserted here

    keyboard = [
        [InlineKeyboardButton("📃Main Menu", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="*Session deleted successfully!*",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

    return RESTART

# Deletes fourth session created by user
def clear3(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    #Backend delete function to be inserted here

    keyboard = [
        [InlineKeyboardButton("📃Main Menu", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="*Session deleted successfully*",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

    return RESTART

# Help message to guide user in using the bot
def help(update: Update, context: CallbackContext) -> None:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("📃Main Menu", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="*To find an existing session:*\n\t\t"
             "Click on join meal session at the main menu\n"
             "*To create a new session:*\n\t\t"
             "Click on create meal session at the main menu and input the necessary details accordingly",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

    return MENU


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN, use_context=True)
    init_channel(updater)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [
                CallbackQueryHandler(menu, pattern='^menu$'),
            ],
            OPTIONS: [
                CallbackQueryHandler(days, pattern='^create$'),
                CallbackQueryHandler(join, pattern='^join$'),
                CallbackQueryHandler(delete, pattern='^delete$'),
                CallbackQueryHandler(help, pattern='^help$'),
            ],
            DELETE: [
                CallbackQueryHandler(clear0, pattern='^I0$'),
                CallbackQueryHandler(clear1, pattern='^I1$'),
                CallbackQueryHandler(clear2, pattern='^I2$'),
                CallbackQueryHandler(clear3, pattern='^I3$'),
                CallbackQueryHandler(menu, pattern='^back$'),
            ],
            TIME: [
                CallbackQueryHandler(time, pattern='^Monday$'),
                CallbackQueryHandler(time, pattern='^Tuesday$'),
                CallbackQueryHandler(time, pattern='^Wednesday$'),
                CallbackQueryHandler(time, pattern='^Thursday$'),
                CallbackQueryHandler(time, pattern='^Friday$'),
                CallbackQueryHandler(time, pattern='^Saturday$'),
                CallbackQueryHandler(time, pattern='^Sunday$'),
                CallbackQueryHandler(menu, pattern='^main$')
            ],
            PAX: [
                MessageHandler(Filters.text & ~Filters.command, pax),
                CallbackQueryHandler(days, pattern='^back$'),
                CallbackQueryHandler(menu, pattern='^main$')
            ],
            REMARKS: [
                CallbackQueryHandler(remarks, pattern='^2$'),
                CallbackQueryHandler(remarks, pattern='^3$'),
                CallbackQueryHandler(remarks, pattern='^4$'),
                CallbackQueryHandler(remarks, pattern='^5$'),
                CallbackQueryHandler(remarks, pattern='^6$'),
                CallbackQueryHandler(remarks, pattern='^7$'),
                CallbackQueryHandler(time, pattern='^back$'),
                CallbackQueryHandler(menu, pattern='^main$'),
            ],
            CONFIRM: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), confirm),
                CallbackQueryHandler(pax, pattern='^back$'),
                CallbackQueryHandler(menu, pattern='^main$'),
            ],
            END: [
                CallbackQueryHandler(end, pattern='^confirm$'),
                CallbackQueryHandler(remarks, pattern='^back$'),
                CallbackQueryHandler(menu, pattern='^main$'),
            ],
            RESTART: [
                CallbackQueryHandler(menu, pattern='^main$')
            ],
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
