from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
import random

class Event:
    def __init__(self, name, handle, time_slot, food_place, quota, current_size):
    	self.name = name
        self.handle = handle
        self.time_slot = time_slot
        self.food_place = food_place
        self.quota = quota
        self.current_size = current_size

    def __str__(self) -> str: #what you return is a string
    	event_text = "-"
    	event_text += self.time_slot
    	event_text += " "
        #return some string



events_list = []

class ChannelEntry:
  def __init__(self, msg: Message, day: str, events: Set[Event]) -> None:
    self.msg = msg
    self.day = day
    self.events = events

  def __str__(self) -> str:
    txt = f"*{self.day}*\n"
    txt += "testing"
    for event in self.events:
      txt += str(event)
      txt += "\n"
    return txt



def event_update(events_array):
    master_string = ""
    for day in events_array:
        for event in day:
            master_string += event.to_string()
        #bot.edit that current day's chat

def daily_update(events_array):
    for i in range(len(events_array)-1):
        events_array[i] = events_array[i+1]
    event_update(events_array)
    




def main():
    # Get telegram bot token from botfather, and do not lose or reveal it
    BOT_TOKEN = "1204602999:AAF7l4-yYtQ2XJFWT6yKz-5VLTe1rnE6s1I"

    # bot updater, refer to https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.updater.html
    updater = Updater(BOT_TOKEN, use_context=True)
    
    # bot dispatcher to register command handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(
        ConversationHandler(
            [CommandHandler("ask", ask)],
            {
                0: [
                        CommandHandler("hail", easter_egg), 
                        MessageHandler(Filters.text, answer)
                    ],
                2: [MessageHandler(Filters.text, show_names)]
            },
            []
        )
    )

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
