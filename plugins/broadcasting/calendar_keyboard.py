import calendar
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.callback_data import CallbackData

from uuid import UUID

from datetime import datetime

calendar_cb = CallbackData('day_cb', 'time', 'day', 'month', 'year', 'action')
event_cb = CallbackData('br_event_cb', 'event_id', 'action')

def generate_calendar(year: int, month: int) -> InlineKeyboardMarkup:
    if month < 1 or month > 12:
        return []
    markup = InlineKeyboardMarkup()
    
    for week in calendar.monthcalendar(year, month):
        markup.row(*[InlineKeyboardButton(day if day!=0 else '⚪️', callback_data=calendar_cb.new(time = '00', day = day, month=month, year=year, action = "select_day")) for day in week])
    
    l = []
    if month == 1:
        l.append(InlineKeyboardButton("Back", callback_data=calendar_cb.new(time = '00', day = 0, month = 12, year = year - 1, action = "change")))
    else:
        l.append(InlineKeyboardButton("Back", callback_data=calendar_cb.new(time = '00', day = 0, month = month - 1, year = year, action = "change")))
    if month == 12:
        l.append(InlineKeyboardButton("Next", callback_data=calendar_cb.new(time = '00', day = 0, month = 1, year = year+1, action = "change")))
    else:
        l.append(InlineKeyboardButton("Next", callback_data=calendar_cb.new(time = '00', day = 0, month = month + 1, year = year, action = "change")))
    markup.row(*l)
    return markup

def generate_time_kb(year: int, month: int, day: int, line_num = 4) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    line = []
    for t in range(0, line_num, 1):
        column = []
        for tt in range(t * int(24 / line_num) + 1, t * int(24 / line_num) + int(24 / line_num) + 1, 1):
            column.append(InlineKeyboardButton(f"{tt:02d}:00", callback_data=calendar_cb.new(time = tt, day = day, month = month, year = year, action = "select_time")))
        line.append(column)
        

    for l in zip(*line):
        markup.row(*list(l))

    return markup

def generate_event_kb(event_id: UUID, this_date: datetime) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    
    markup.row(
        InlineKeyboardButton("Edit", callback_data=event_cb.new(event_id = str(event_id), action = "edit")),
        InlineKeyboardButton("Delete", callback_data=event_cb.new(event_id = str(event_id), action = "delete")),
        InlineKeyboardButton("Reschedule", callback_data=event_cb.new(event_id = str(event_id), action = "reschedule")),
    )

    markup.row(
        InlineKeyboardButton("To calendar", callback_data=calendar_cb.new(time = '00', day = this_date.day, month = this_date.month, year = this_date.year, action = "change")),
    )

    return markup