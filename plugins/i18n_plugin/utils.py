import asyncio
import gettext
import os
from shutil import rmtree

import aiohttp
from loguru import logger


async def fetch_post(url, data={}):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            return await response.json()


async def fetch_get_file(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.content.read()


async def get_languages(token, id):
    data = {
        'api_token': token,
        'id': id
    }

    r = await fetch_post('https://api.poeditor.com/v2/languages/list', data=data)
    return [i['code'] for i in r['result']['languages']]


async def download_locale(locale_name, token, id, type='mo'):
    store_in = "locales/{}/LC_MESSAGES".format(locale_name)
    data = {
        'api_token': token,
        'id': id,
        'language': locale_name,
        'type': type
    }
    os.makedirs(store_in, exist_ok=True)
    logger.info("{} locale: searching".format(locale_name))
    r = await fetch_post('https://api.poeditor.com/v2/projects/export', data=data)
    logger.info("{} locale: finded".format(locale_name))
    logger.info("{} locale: downloading".format(locale_name))
    file = await fetch_get_file(r['result']['url'])

    logger.info("{} locale: downloaded".format(locale_name))
    with open(store_in + "/" + "base.mo", 'wb') as f:
        f.write(file)

    logger.info("{} locale: saved to {}".format(
        locale_name, store_in + "/" + "base.mo"))
    return locale_name


async def store_locales(token, id):
    rmtree('locales', ignore_errors=True)
    d_list = []
    for lang in await get_languages(token, id):
        d_list.append(await download_locale(lang, token, id))

    return d_list


if __name__ == "__main__":
    from i18n_config import config
    asyncio.run(store_locales(config["poeditor_token"],
                              config["poeditor_project_id"]))
