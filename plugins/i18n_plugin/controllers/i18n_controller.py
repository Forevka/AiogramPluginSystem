import gettext
import os
import typing

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

from ..utils import store_locales


class LocaleController:
    def __init__(self, keyboard: types.InlineKeyboardMarkup, config: dict):
        self.locales: typing.Dict[str, gettext.gettext] = self.load_locales()
        self.config: dict = config
        self.langcodes: dict = config['langcodes']
        self.emoji_flags: dict = config['emoji_flags']

        logger.debug("locales: " + ', '.join(self.locales))
        self.opt = keyboard
        self.locale_markup = self.generate_keyboard()

    def load_locales(self,) -> typing.Dict[str, gettext.gettext]:
        try:
            locales = os.listdir("locales")
            local: typing.Dict[str, gettext.gettext] = {}
            for i in locales:
                if os.path.isdir("locales/"+i):
                    local[i] = gettext.translation(
                        'base', localedir='locales', languages=[i]).gettext

            return local
        except:
            return {}

    def all_possible_translets(self, text) -> typing.Generator:
        for i in self.locales.values():
            yield i(text)

    async def download_locale(self) -> typing.List[str]:
        return await store_locales(self.config["poeditor_token"],
                                   self.config["poeditor_project_id"])

    async def reload_locales(self) -> bool:
        await self.download_locale()
        self.locales = self.load_locales()
        self.locale_markup = self.generate_keyboard()
        return True

    def get_locale(self, lang: str) -> gettext.gettext:
        return self.locales.get(lang, self.locales['ru'])

    def generate_keyboard(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        for i in list(self.locales.keys()):
            markup.add(InlineKeyboardButton(self.langcodes.get(i)+" "+self.emoji_flags.get(i, ""),
                                            callback_data=self.opt.new(type='lang_choice', value=i)))
        return markup

    def get_markup(self) -> InlineKeyboardMarkup:
        return self.locale_markup
