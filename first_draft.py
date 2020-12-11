from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
import datefinder
import datetime
import pytz
import random
from typing import List

time_zone = pytz.timezone("Asia/Singapore")

class Event:
    def __init__(self, name, handle, day, time_slot, food_place):
        self.name = name #name of event
        self.handle = handle #handle of organizer
        self.day = day #day of event (mon/tues/wed etc)
        self.time_slot = time_slot #start time
        self.food_place = food_place #place of event

day_dict = {"Monday":0, "Tuesday":1, "Wednesday":2, "Thursday":3, "Friday":4, "Saturday":5, "Sunday":6}

events_list = []

def sort_function(event_instance):
    return event_instance.time_slot

class ChannelEntry:
  def __init__(self, msg: Message, day: str, events: List[Event]) -> None:
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

  def add_to_channel(self, event_instance):
    now = datetime.datetime.now()
    time_now = time_zone.localize(now)
    index = (day_dict[event_instance.day] - today) % 7

    events_list[index].append(event_instance)
    events_list[index].sort(key=sort_function)

 #  def remove_from_channel(self, event_instance):
 #      now = datetime.datetime.now()
    # time_now = time_zone.localize(now)
 #      index = (day_dict[event_instance.day] - today) % 7

 #      for i in events_list[index]:
 #          if (i.handle == event_instance.handle && i.)

 #      events_list[index].append(event_instance)
 #      events_list[index].sort(key=sort_function)

def event_update(events_array):
    master_string = ""
    for day in events_array:
        for event in day:
            master_string += event.to_string()
        #bot.edit that current day's chat

def daily_update(events_array):
    for i in range(len(events_array)-1):
       events_array[i] = events_array[I+1]
    events_array[6] = ChannelEntry([])


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
