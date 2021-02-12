from typing import List
from datetime import datetime


class Event:
    def __init__(self, id: int, description: str, handle: str, dt: datetime, pax: int, food_place: str) -> None:
        self.id = id  # id of event
        self.description = description  # name of the user
        self.handle = handle  # handle of organizer
        self.dt = dt
        # self.day = day  # day of event (mon/tues/wed etc)
        # self.time_slot = time_slot  # start time
        self.pax = pax
        self.food_place = food_place  # place of event

    def __str__(self) -> str:
        txt = f"[Session {self.id}]\n"\
              f"\t\t\tDescription: {self.description}\n"\
              f"\t\t\tContact: @{self.handle}\n" \
              f"\t\t\tTime: {self.dt.strftime('%H%M')}\n"\
              f"\t\t\tPax: {self.pax}\n"\
              f"\t\t\tLocation: {self.food_place}"
        return txt


class ChannelEntry:
    def __init__(self, date: datetime, events: List[Event]) -> None:
        self.date = date
        self.events = events

    def __str__(self) -> str:
        txt = f"<b>{self.date.strftime('%A')}, {self.date.strftime('%d/%m/%y')}</b>\n"
        for event in self.events:
            txt += (str(event) + "\n\n")
        return txt

    def sort_events(self) -> None:
        self.events.sort(key=lambda event: event.dt)

    def add_event(self, event) -> None:
        self.events.append(event)
        self.sort_events()

    def get_user_events(self, user) -> list:
        return [event for event in self.events if event.handle == user]

    def check_event_id(self, id) -> bool:
        return id in [event.id for event in self.events]

    def del_event(self, id) -> bool:
        if not self.check_event_id(id):
            return False
        idx = 0
        for i in range(len(self.events)):
            if self.events[i].id == id:
                idx = i
                break
        del self.events[idx]
        return True
