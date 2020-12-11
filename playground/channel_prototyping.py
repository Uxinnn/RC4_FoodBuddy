from __future__ import annotations

from telegram import ParseMode, Message
from telegram.ext import Updater, CommandHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from datetime import datetime, timedelta, time
import logging
from typing import Set, Union

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Event:
  def __init__(self):
    ...

  def __str__(self):
    ...


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


CHANNEL = "@test_channel1233"
CHANNEL_INFO = []
UPDATE_TIME = time(hour=15, minute=3, second=0)  # UTC time
TOKEN = "1424694577:AAHm2GzdSee-WHyIj-tYn6zTf8TTCbuYKE4"


def start(update: Update, context: CallbackContext) -> None:
  ...


def init_channel(updater: Updater) -> None:
  logging.debug("Initializing channel...")

  date = datetime.today()
  while len(CHANNEL_INFO) != 7:
    day = date.strftime('%A')
    logging.debug(f"\tCreating entry for {day}...")
    msg = updater.bot.send_message(text=f"*{day}*\n", chat_id=CHANNEL, parse_mode=ParseMode.MARKDOWN_V2)
    CHANNEL_INFO.append(ChannelEntry(msg, day, set()))
    date += timedelta(days=1)


def update_channel(context: Union[CallbackContext, Updater]) -> None:
  logging.debug("Updating Channel...")
  for entry in CHANNEL_INFO:
    logging.debug(f"\t{entry.day} updating...")
    # Will raise error if message is not different!
    context.bot.edit_message_text(chat_id=entry.msg.chat_id,
                                  message_id=entry.msg.message_id,
                                  text=str(entry),
                                  parse_mode=ParseMode.MARKDOWN_V2)


def main():
  updater = Updater(TOKEN, use_context=True)
  init_channel(updater)
  update_channel(updater)

  # To run channel update daily
  updater.job_queue.run_daily(update_channel, UPDATE_TIME)

  # bot dispatcher to register command handlers
  dp = updater.dispatcher
  dp.add_handler(CommandHandler("start", start))

  updater.start_polling()
  updater.idle()


if __name__ == "__main__":
  main()
