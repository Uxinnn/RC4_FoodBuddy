from typing import List


class Event:
    def __init__(self, id: int, handle: str, day: str, time_slot: str, pax:str, food_place: str) -> None:
        self.id = id  # id of event
        self.handle = handle  # handle of organizer
        self.day = day  # day of event (mon/tues/wed etc)
        self.time_slot = time_slot  # start time
        self.pax = pax
        self.food_place = food_place  # place of event


    def __str__(self) -> str:
        txt = f"Index {self.id}: @{self.handle}\n" \
              f"Time: {self.time_slot}\n "\
              f"Maximum number of people: {self.pax}\n "\
              f"Remarks: {self.food_place}"
        return txt


class ChannelEntry:
    def __init__(self, day: str, events: List[Event]) -> None:
        self.day = day
        self.events = events

    def __str__(self) -> str:
        txt = f"<b>{self.day}</b>\n"
        for event in self.events:
            txt += str(event)
            txt += "\n"
        return txt

    def sort_events(self):
        self.events.sort(key=lambda event: event.time_slot)

    def add_event(self, event):
        self.events.append(event)
        self.sort_events()
