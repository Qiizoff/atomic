# -*- coding: utf-8 -*-
import asyncio
import json

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold, hlink

from atomic_main import start_data
from wax_get_send_contract_balances import start_depo

import config

# bot = Bot(token=config.API_START_TOKEN, parse_mode=types.ParseMode.HTML)
# dp = Dispatcher()
bot = Bot(token=config.API_START_TOKEN)

async def scheduled(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        start_data()

        # Read the JSON data from the file
        with open("start.json", 'r', encoding="utf_8", errors="ignore") as f:
            data = json.load(f)
            # data = await asyncio.to_thread(json.load, f)

        # If the data is empty, repeat start_data()
        if not any(data):
            continue

        # Process and send the data to the bot
        start_cards = []
        for items in data:
            start_card = (
                f'{hlink(items.get("coll_name"), items.get("sale_url"))}\n'
                f'{hbold("Шаблон: ")}{items.get("template")}\n'
                f'{hbold("Цена: ")}{items.get("price_wax")}\n'
                f'{hbold("Ближайшие цены: ")}{items.get("price_asc")}\n'
                f'{hbold("Средняя цена: ")}{items.get("average_price")}\n'
                f'{hbold("Рекомендованая цена: ")}{items.get("suggested_average")}\n'
                f'{hbold("Медианная цена: ")}{items.get("suggested_median")}\n'
                f'{hbold("Мин цена продажи: ")}{items.get("min")}\n'
                f'{hbold("Продаж: ")}{items.get("sales")}\n'
                f'{hlink(items.get("seller"), items.get("seller_url"))}\n'
                f'{hbold("Backed Tokens: ")}{items.get("amount")}\n'
                f'{hbold("ID: ")}{items.get("sale_id")}\n'
            )
            start_cards.append(start_card)

        # Send the messages to the bot
        for card in start_cards:
            try:
                await bot.send_message(
                    chat_id=-1001629909246,
                    text=card,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
                await asyncio.sleep(1)
            except Exception as e:
                print(e)
                await asyncio.sleep(3)

        # Clearing the "start.json" file
        with open("start.json", 'w') as f:
            json.dump([], f)

        print(f'SAVE CLEAR')


async def scheduled_start_depo(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        start_depo()


async def run_main():
    await asyncio.gather(scheduled(5), scheduled_start_depo(12*3600))


def main():
    asyncio.run(run_main())


if __name__ == "__main__":
    main()
