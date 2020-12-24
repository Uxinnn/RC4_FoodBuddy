from typing import List


class Event:
    def __init__(self, id: int, handle: str, day: str, time_slot: str, pax: str, food_place: str) -> None:
        self.id = id  # id of event
        self.handle = handle  # handle of organizer
        self.day = day  # day of event (mon/tues/wed etc)
        self.time_slot = time_slot  # start time
        self.pax = pax
        self.food_place = food_place  # place of event

    def __str__(self) -> str:
        txt = f"Session {self.id}: @{self.handle}\n" \
              f"\t\tTime: {self.time_slot}\n"\
              f"\t\tPax: {self.pax}\n"\
              f"\t\tRemarks: {self.food_place}"
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

    # Get events associated with input user
    def get_user_events(self, user):
        ...

    # Check if input id is the id of one of the events in the object
    def check_event_id(self, id):
        ...

    # delete event from object
    def del_event(self, id):
        ...
