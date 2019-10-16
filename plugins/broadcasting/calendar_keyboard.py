import calendar
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.callback_data import CallbackData

calendar_cb = CallbackData('day_cb', 'day', 'month', 'year', 'action')

def generate_calendar(year: int, month: int):
    if month < 1 or month > 12:
        return []
    markup = InlineKeyboardMarkup()
    
    for week in calendar.monthcalendar(year, month):
        markup.row(*[InlineKeyboardButton(day if day!=0 else '⚪️', callback_data=calendar_cb.new(day = day, month=month, year=year, action = "select_day")) for day in week])
    
    l = []
    if month == 1:
        l.append(InlineKeyboardButton("Back", callback_data=calendar_cb.new(day = 0, month = 12, year = year - 1, action = "change")))
    else:
        l.append(InlineKeyboardButton("Back", callback_data=calendar_cb.new(day = 0, month = month - 1, year = year, action = "change")))
    if month == 12:
        l.append(InlineKeyboardButton("Next", callback_data=calendar_cb.new(day = 0, month = 1, year = year+1, action = "change")))
    else:
        l.append(InlineKeyboardButton("Next", callback_data=calendar_cb.new(day = 0, month = month + 1, year = year, action = "change")))
    markup.row(*l)
    return markup