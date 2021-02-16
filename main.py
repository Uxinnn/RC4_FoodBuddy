import emoji
import logging
from typing import Dict, List, Union
import datetime
import pytz
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, CallbackContext,
                          MessageHandler, Filters)
from telegram.error import BadRequest
from base_classes import Event, ChannelEntry


# Enable logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

THEMES_SET = ("Games", "Movies", "TV Shows", "Books", "Hobbies",
              "Current Affairs", "Politics", "Music", "Sports",
              "Academics", "Food", "Travel", "Animals", "Tech")

COUNT = 0
CHANNEL = []
MESSAGES = []

CHANNEL_HANDLE = "<INSERT CHANNEL HANDLE HERE>"
CHANNEL_URL = "<INSERT CHANNEL URL HERE>"
BOT_TOKEN = "<INSERT BOT TOKEN HERE>"

# Stages of conversation
MENU, OPTIONS, DELETE, RET_DEL, DAYS, TIME, RET_TIME, PAX, REMARKS, CONFIRM, END, RESTART = range(12)

TIME_ZONE = pytz.timezone("Asia/Singapore")
DAILY_UPDATE_TIME = datetime.time(hour=8, minute=0, second=0, tzinfo=TIME_ZONE)


####################################
# Functions to interact with store #
####################################

# Initializes CHANNEL and MESSAGES
def init_channel(updater: Updater) -> None:
    logger.debug("Initializing channel...")

    date = datetime.datetime.today()
    while len(CHANNEL) != 7:
        channel_entry = ChannelEntry(date, [])
        logger.debug(f"\tCreating entry for {date.strftime('%A')}...")
        msg = updater.bot.send_message(text=str(channel_entry),
                                       chat_id=CHANNEL_HANDLE,
                                       parse_mode=ParseMode.HTML)
        CHANNEL.append(channel_entry)
        MESSAGES.append(msg)
        date += datetime.timedelta(days=1)


# Refreshes channel
def update_channel(context: Union[CallbackContext, Updater]) -> None:
    logger.debug("Updating Channel...")
    for entry in CHANNEL:
        msg = MESSAGES[CHANNEL.index(entry)]
        logger.debug(f"\t{entry.date} updating...")
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
    idx = (event.dt.weekday() - datetime.datetime.today().weekday()) % 7
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
    dt = datetime.datetime.now() + datetime.timedelta(days=6)
    for i in range(len(CHANNEL)-1):
        CHANNEL[i] = channel_copy[i+1]
    CHANNEL[6] = ChannelEntry(dt, [])
    update_channel(callback)
    print_channel()


# Helper function to print channel contents to logger
def print_channel() -> None:
    txt = ""
    for day in CHANNEL:
        txt += (str(day) + "\n")
    logger.debug(txt)


# Generates a string describing the theme of the week
def random_theme_generator():
    theme = random.choice(THEMES_SET)
    theme_string = f"Theme of the week: {theme}"
    return theme_string


#######
# Bot #
#######

# First function when users types in /start & logs users' telegram handle
def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Main Menu🍱", callback_data="main")],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    user = update.message.from_user
    context.user_data["Telegram Handle"] = user.username
    logger.info(f"User {user.first_name} started the conversation.")

    update.message.reply_text(
        text="*Welcome to RC4FoodBud!*\n\n"
             "Want to jio friends, IG mates for lunch or dinner🥘?\n"
             "Want to join others to grab a quick meal🥡?\n"
             "RC4FoodBud is here to help!💪\n"
             "Through this bot, you can create meal sessions to jio others 📣 or you can find others jioing you 🤪 via our channel!\n\n\n"
             "An OrcaTech Initiative 🐳 by @Uxinnn, @mukundrs, @bryanwhl and @Albunist",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return MENU


def menu(update: Update, context: CallbackContext) -> int:
    """Send message on `/start`."""
    if get_user_events(context.user_data["Telegram Handle"]):
        query = update.callback_query
        query.answer()
        keyboard = [
        [InlineKeyboardButton("Create🍳", callback_data="create")],
        [InlineKeyboardButton("View Sessions🥂", url=CHANNEL_URL)],
        [InlineKeyboardButton("Delete❌", callback_data="delete")],
        [InlineKeyboardButton("Help🙋‍♂️🙋", callback_data="help")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            text="*Main Menu*\n\n"
                 "Select _Create🍳_ to host a new meal session by adding more details\n\n"
                 "Select _View Sessions🥂_ to join active meal sessions!\n\n"
                 "Select _Delete❌_ to delete an existing session\n\n"
                 "Select _Help🙋‍♂️🙋_ if you need further assistance or wish to contact the developers.",
            parse_mode="Markdown",
            reply_markup=reply_markup
            )
        return OPTIONS

    # Remove delete button if no sessions have been created by the user
    elif not get_user_events(context.user_data["Telegram Handle"]):
        query = update.callback_query
        query.answer()
        keyboard = [
        [InlineKeyboardButton("Create🍳", callback_data="create")],
        [InlineKeyboardButton("View Sessions🥂", url=CHANNEL_URL)],
        [InlineKeyboardButton("Help🙋‍♂️🙋", callback_data="help")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            text="*Main Menu*\n\n"
                 "Select _Create🍳_ to host a new meal session by adding more details\n\n"
                 "Select _View Sessions🥂_ to join active meal sessions!\n"
                 "To join, you need to PM the host listed in the channel\n\n"
                 "Select _Help🙋‍♂️🙋_ if you need further assistance or wish to contact the developers.",
            parse_mode="Markdown",
            reply_markup=reply_markup
            )
        return OPTIONS


# Allows logged user_data to be printed as string
def facts_to_str(user_data: Dict[str, Union[str, datetime.datetime]]) -> str:
    facts = list()
    for key, value in user_data.items():
        if key == "dt":
            facts.append(f"Date - {value.strftime('%d/%m, %a')}")
            facts.append(f"Time - {value.strftime('%H%M')}")
            continue
        facts.append(f'{key} - {value}')

    return "\n".join(facts).join(['\n', '\n'])


###########################
# CREATE SESSION SEQUENCE #
###########################

# User to name session
def description(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Main Menu🍱", callback_data="main")]
        
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="*Session Description*\n\n"
             "Please put a brief description✍ of your session.\n"
             "Example:_OrcaTech Bonding👋_",
        parse_mode="Markdown",
        reply_markup=reply_markup
        )
    return DAYS


# User to pick the day for the session
def days(update: Update, context: CallbackContext) -> int:
    text = update.effective_message.text
    context.user_data['Description'] = text
    logger.debug(f"\t{context.user_data['Telegram Handle']} remarked {text}")
    dates = [datetime.date.today() + datetime.timedelta(days=i) for i in range(7)]
    keyboard = [
        [InlineKeyboardButton(dates[i].strftime("%d/%m"), callback_data=str(i)) for i in range(len(dates))],
        [InlineKeyboardButton("Back🔙", callback_data="back")],
        [InlineKeyboardButton("Main Menu🍱", callback_data="main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text(
        text="*Session Date*\n\n"
             "Please choose a day in the current academic week 📅.",
        parse_mode="Markdown",
        reply_markup=reply_markup
        )
    return TIME


# User to input the time of the meal session after selecting the day
def time(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    if query.data != "back":  # At any point the user presses back, this is called
        context.user_data['dt'] = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=int(query.data))
        logger.debug(f"\t{context.user_data['Telegram Handle']} chose {query.data}")
    keyboard = [ 
        [InlineKeyboardButton("Back🔙", callback_data="back")],
        [InlineKeyboardButton("Main Menu🍱", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="*Session Time*\n\n"
             "Please indicate the time 🕔 of the meal in the 24hr format.\n"
             "_Example:1500_",
        parse_mode="Markdown",
        reply_markup=reply_markup
        )
    return PAX


# User to select maximum numer of pax after inputing time
def pax(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    text = update.effective_message.text
    is_bot = update.effective_message.from_user["is_bot"]

    # Display error if most recent message is created by a user and has an invalid format
    if (len(text) != 4 or not text.isnumeric() or int(text[2:]) > 60 or int(text) < 0 or int(text) > 2359) and not is_bot:
        update.effective_message.reply_text(
            text="Sorry, a valid time was not registered. Please send us the time in 24hr format.\n_Example:2359_",
            parse_mode='Markdown'
        )
        return RET_TIME

    # Update time in datetime object if most recent message is created by a user
    if not is_bot:
        context.user_data["dt"] = context.user_data["dt"].replace(hour=int(text[:2]), minute=int(text[2:]))
        # Checks if datetime entered is in the past
        if context.user_data["dt"] < datetime.datetime.now():
            current_time = datetime.datetime.now()

            update.effective_message.reply_text(
                text="Sorry, the date and time entered has past. Please send us a valid time in 24hr format. "
                     f"Current time is {current_time.strftime('%H%M')}."
                     f"\n_Example:{(current_time + datetime.timedelta(minutes=5)).strftime('%H%M')}_",
                parse_mode='Markdown'
            )
            return RET_TIME
        logger.debug(f"\t{context.user_data['Telegram Handle']} chose {text}")

    keyboard = [
        [InlineKeyboardButton("2", callback_data="2"),
         InlineKeyboardButton("3", callback_data="3"),
         InlineKeyboardButton("4", callback_data="4"),
         InlineKeyboardButton("5", callback_data="5"),
         InlineKeyboardButton("6", callback_data="6"),
         InlineKeyboardButton("7", callback_data="7")],
        [InlineKeyboardButton("Back🔙", callback_data="back")],
        [InlineKeyboardButton("Main Menu🍱", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text(
        text="*Session Pax*\n\n"
             "Choose the max number 🔢 of people (excluding yourself) for the meal.",
        parse_mode="Markdown",
        reply_markup=reply_markup
        )
    return REMARKS


# User to input other remarks after selecting max number of pax
def location(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    if query.data.isnumeric():
        context.user_data['Pax'] = int(query.data)
    keyboard = [
        [InlineKeyboardButton("Back🔙", callback_data="back")],
        [InlineKeyboardButton("Main Menu🍱", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="*Session Location*\n\n"
             "Please indicate the location 🧭 of the meal.\n"
             "_Example:Fine Food_",
        parse_mode="Markdown",
        reply_markup=reply_markup
        )
    return CONFIRM


# User to confirm session details before the bot sends to channel
def confirm(update: Update, context: CallbackContext) -> None:
    text = update.effective_message.text
    context.user_data['Location'] = text
    logger.debug(f"\t{context.user_data['Telegram Handle']} remarked {text}")

    keyboard = [
        [InlineKeyboardButton("Confirm✔", callback_data="confirm")],
        [InlineKeyboardButton("Back🔙", callback_data="back")],
        [InlineKeyboardButton("Main Menu🍱", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.effective_message.reply_text(f"*Session Confirmation*\n\nPlease confirm your session details:{facts_to_str(context.user_data)}",
                                        parse_mode="Markdown",
                                        reply_markup=reply_markup
                                        )
    return END


# Bot sends session details to channel after confirmation
def end(update: Update, context: CallbackContext) -> int:
    global COUNT
    query = update.callback_query
    text = update.effective_message.text
    logger.debug(f"\t{context.user_data['Telegram Handle']} has just confirmed the following details:\n{text}")

    # Add event to CHANNEL
    event = Event(COUNT,
                  context.user_data["Description"],
                  context.user_data["Telegram Handle"],
                  context.user_data["dt"],
                  context.user_data["Pax"],
                  context.user_data["Location"])
    add_to_channel(event, context)
    COUNT += 1

    keyboard = [
            [InlineKeyboardButton("Main Menu🍱", callback_data="main")],
            [InlineKeyboardButton("View Session🔍", url=CHANNEL_URL)]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text("*Session created successfully!*\n\n"
                            "Select _Main Menu🍱_ to return to the menu\n"
                            "Select _View Session🔍_ to view your session!",
                            parse_mode="Markdown",
                            reply_markup=reply_markup
                            )
    return RESTART


#############################
# DELETING SESSION SEQUENCE #
#############################

def delete(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user = context.user_data['Telegram Handle']
    user_events = get_user_events(user)
    event_str = ""
    for event in user_events:
        event_str += (str(event) + "\n\n")

    keyboard = [
        [InlineKeyboardButton("Back🔙", callback_data="back")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Show "No session found" message if there are no sessions created by user is found
    if not user_events:
        query.edit_message_text(
            text="*ERROR*: No sessions found, please create a session first.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return DELETE

    query.edit_message_text(
        text=f"These are your sessions:\n"
             f"{event_str}\n"
             f"Please select a session to delete by typing the session id.\n"
             f"For example, you want to delete [Session 7] so type:_7_ ",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return DELETE


# Deletes the session chosen by user
def clear(update: Update, context: CallbackContext) -> None:
    text = update.effective_message.text

    # If input ID is invalid, display ERROR and ask for input again
    if not text.isnumeric() or int(text) not in [event.id for event in get_user_events(context.user_data['Telegram Handle'])]:
        user = context.user_data['Telegram Handle']
        user_events = get_user_events(user)
        event_str = ""
        for event in user_events:
            event_str += (str(event) + "\n\n")

        keyboard = [
            [InlineKeyboardButton("Back🔙", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.effective_message.reply_text(
            text=f"Sorry, a valid session id was not registered\n"
                 f"{event_str}\n"
                 f"Please send us a session id from the list above\n"
                 f"For example, you want to delete [Session 7] so type:_7_ ",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return RET_DEL

    id = int(text)
    del_from_channel(id, context)

    keyboard = [
        [InlineKeyboardButton("Main Menu🍱", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text(
        text=f"Session {text} deleted successfully!",
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
        [InlineKeyboardButton("Main Menu🍱", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="<b>Help</b>\n\n"
             "This bot assists in creating meal sessions and publish the details to the telegram channel.\n"
             "To create a meal session, you will need to input 5 details: Description✍, Date📅, Time🕔, Pax🔢 and Location🧭 of the meal.\n"
             "You can start by selecting _Create🍳_ and the bot will guide you along the way to input the 5 required details.\n"
             f"To view a meal session, you can just proceed to the telegram channel:{CHANNEL_URL}.\n"
             "In order to join a meal session, you would need to access the telegram channel and contact the host of the listed session you want to join.\n\n"
             "Contact @Uxinnn, @mukundrs, @bryanwhl or @Albunist if you need further assistance.",
        parse_mode="HTML",  # Using HTML as channel url has _ which parses wrongly on markdown
        reply_markup=reply_markup
    )

    return MENU


def themes(update: Update, context: CallbackContext) -> None:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Main Menu🍱", callback_data="main")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=f"{random_theme_generator()}",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

    return MENU


def main():
    # Create the Updater and pass it your bot token.
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
                CallbackQueryHandler(menu, pattern='^main$'),
            ],
            OPTIONS: [
                CallbackQueryHandler(description, pattern='^create$'),
                CallbackQueryHandler(delete, pattern='^delete$'),
                CallbackQueryHandler(themes, pattern='^themes$'),
                CallbackQueryHandler(help, pattern='^help$'),
            ],
            DELETE: [
                MessageHandler(Filters.text & ~Filters.command, clear),
                CallbackQueryHandler(menu, pattern='^back$'),
            ],
            RET_DEL: [
                MessageHandler(Filters.text & ~Filters.command, clear),
                CallbackQueryHandler(delete, pattern='^back$')
            ],
            DAYS: [
                MessageHandler(Filters.text & ~Filters.command, days),
                CallbackQueryHandler(menu, pattern='^main$'),
            ],
            TIME: [
                CallbackQueryHandler(time, pattern='^0$'),
                CallbackQueryHandler(time, pattern='^1$'),
                CallbackQueryHandler(time, pattern='^2$'),
                CallbackQueryHandler(time, pattern='^3$'),
                CallbackQueryHandler(time, pattern='^4$'),
                CallbackQueryHandler(time, pattern='^5$'),
                CallbackQueryHandler(time, pattern='^6$'),
                CallbackQueryHandler(description, pattern='^back$'),
                CallbackQueryHandler(menu, pattern='^main$')
            ],
            RET_TIME: [
                MessageHandler(Filters.text & ~Filters.command, pax),
                CallbackQueryHandler(days, pattern='^back$')
            ],
            PAX: [
                MessageHandler(Filters.text & ~Filters.command, pax),
                CallbackQueryHandler(days, pattern='^back$'),
                CallbackQueryHandler(menu, pattern='^main$')
            ],
            REMARKS: [
                CallbackQueryHandler(location, pattern='^2$'),
                CallbackQueryHandler(location, pattern='^3$'),
                CallbackQueryHandler(location, pattern='^4$'),
                CallbackQueryHandler(location, pattern='^5$'),
                CallbackQueryHandler(location, pattern='^6$'),
                CallbackQueryHandler(location, pattern='^7$'),
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
                CallbackQueryHandler(location, pattern='^back$'),
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
    updater.job_queue.run_daily(daily_update, DAILY_UPDATE_TIME)
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
