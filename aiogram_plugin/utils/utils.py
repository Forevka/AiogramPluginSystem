import enum
from inspect import iscoroutinefunction, isfunction, getfullargspec
import re
import typing

from aiogram import Dispatcher, types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.mixins import DataMixin, ContextInstanceMixin
from loguru import logger

class WhenToCall(enum.IntEnum):
    BEFORE_MIDDLEWARES = AT_START = 1
    BEFORE_HANDLERS = AFTER_MIDDLEWARES = 2
    AFTER_HANDLERS = AFTER_ALL = 3

def convert_to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()