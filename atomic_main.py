# -*- coding: utf-8 -*-
import requests
import json
import io
import time
import logging
import statistics
from collections import deque
from datetime import datetime, timedelta
from atomic_buy_v2 import purchasesale
from atomic_list_sale import atomicsale
from contextlib import suppress
from colors import Colors
from pprint import pprint


class UniqueDeque:
    def __init__(self, maxlen=0):
        self.deque = deque(maxlen=maxlen)
        self.set = set()

    def append(self, element):
        if element not in self.set:
            self.deque.append(element)
            self.set.add(element)

    def __iter__(self):
        return iter(self.deque)

all_id = UniqueDeque(maxlen=200)
all_id_list = set()

sale_id_link = "https://wax.atomichub.io/market/sale/"
account_link = "https://wax.atomichub.io/explorer/account/"
count = 0

def timer():
    tcx = datetime.now().strftime('%d %B %H:%M:%S')
    return tcx

def logg(msg):
    logging.basicConfig(level = logging.INFO , filename = "miner.log", format = '%(asctime)s %(message)s')  # include timestamp
    logging.info(msg)

def history_price(collection_name=None, schema_name=None, template_id=1):
    headers = {"accept": "application/json"}

    params = {
        "collections_name": collection_name,
        "schema_name": schema_name,
        # "symbol": "WAX",
        "template_id": template_id
    }

    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = requests.get("https://wax.api.atomicassets.io/atomicmarket/v1/prices/sales/days", headers=headers, params=params)
            # print(f"{timer()} history_price: {response.url}")
            response.raise_for_status()
            count = 0
            sales = 0
            week = 4
            total_sales = 0
            average_sales = 0
            history = []
            old_time = (datetime.today() - timedelta(days=week)).strftime('%Y-%m-%d')
            data = response.json().get("data", [])
            for i in data[:week]:
                median = float(i.get("median", 0))/100000000
                median = "{:.2f}".format(median)
                average = float(i.get("average", 0))/100000000
                average = "{:.2f}".format(average)
                sales = int(i.get("sales", ""))
                epoch_time = datetime.utcfromtimestamp(i.get("time", "") / 1000).strftime('%Y-%m-%d')
                if epoch_time < old_time:
                    continue
                if not sales or float(sales) <= 1:
                    break
                history.append((f"{epoch_time} sales: {sales} median: {median} average: {average}"))
                total_sales += sales
                count += 1
                if count >= week:
                    average_sales = total_sales/week
                    for i in history:
                        print(f"{Colors.YELLOW}{timer()}{Colors.RESET} i in history: {Colors.YELLOW}{i}{Colors.RESET}")
            print(f"{Colors.YELLOW}{timer()}{Colors.RESET} count: {Colors.YELLOW}{count}{Colors.RESET} average_sales: {Colors.YELLOW}{average_sales}{Colors.RESET}")
            return count, average_sales

        except requests.exceptions.RequestException as e:
            retry_count += 1
            print(f"Ошибка соединения: {e}")
            print(f"Повторная попытка через 5 секунд...")
            time.sleep(5)
            continue
    return (0, 0)


def check_price(template_id=1, collection_name=None):
    headers = {
        "accept": "application/json"}

    params = {
        "limit": 5,
        "order": "asc",
        "sort": "price",
        "state": 1,
        "template_id": template_id,
        "collection_name": collection_name,
        # "symbol": "WAX",
        "page": 1}

    url = "https://wax.api.atomicassets.io/atomicmarket/v2/sales"

    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        now = datetime.now()
        try:
            response = requests.get(url, headers=headers, params=params)
            # print(f"{timer()} check_price: {response.url}")
            response.raise_for_status()
            data = response.json().get("data", [])
            price_asc = [int(i.get("price", {}).get("amount", 0)) / 100000000 for i in data]
            round_price_asc = [round(int(i.get("price", {}).get("amount", 0)) / 100000000, 2) for i in data]
            if len(price_asc) >= 2:
                average_price = round(statistics.mean(price_asc), 2)
                print(f"{Colors.RED}{timer()} if price_asc:{Colors.RESET} {Colors.RED}{price_asc}{Colors.RESET} round_price_asc: {Colors.RED}{round_price_asc}{Colors.RESET} average_price: {Colors.RED}{average_price}{Colors.RESET}")
                print(f"{Colors.RED}{timer()} if round_price_asc:{Colors.RESET} {Colors.RED}{round_price_asc}{Colors.RESET} average_price: {Colors.RED}{average_price}{Colors.RESET}")
                return price_asc, round_price_asc, average_price
            else:
                print(f"{timer()} else round_price_asc: {round_price_asc}")
                return None

        except requests.exceptions.RequestException as e:
            retry_count += 1
            print(f"{timer()} Ошибка соединения: {e}")
            print(f"{timer()} Повторная попытка через 5 секунд...")
            time.sleep(5)
            continue
    return None


def get_response():
    headers = {
        "accept": "application/json"}

    params = {
        "max_assets": 1,
        "order": "desc",
        "sort": "created",
        "state": 1,
        "symbol": "WAX"}

    url = "https://wax.api.atomicassets.io/atomicmarket/v1/sales"

    while True:
        now = datetime.now()
        try:
            response = requests.get(url, headers=headers, params=params)
            # print(f"{timer()} get_response: {response.url}")
            response.raise_for_status()
            data = response.json().get("data", [])
            return data
        except requests.exceptions.RequestException as e:
            print(f"{timer()} Ошибка #1 соединения: {e}")
            print(f"{timer()} Повторная попытка через 5 секунд...")
            time.sleep(5)
            continue


def save_results(result_start):
    with suppress(PermissionError):
        with io.open("start.json", "w", encoding="utf_8", errors="ignore") as f:
            json.dump(result_start, f, indent=4, ensure_ascii=False)
            print(f"Сохраняю в файл...")


def start_data():
    global all_id
    global all_id_list
    price_multiplier = 1.1
    result_start = []
    data = get_response()
    for i in data:
        now = datetime.now()
        sale_id = i.get("sale_id")
        listing_symbol = i.get("listing_symbol")
        if sale_id in all_id_list:
            continue
        sale_url = sale_id_link + sale_id
        seller = i.get("seller")
        seller_url = account_link + seller
        collection_name = i.get("collection_name")
        coll_name = i.get("collection", "").get("name", "")
        price_wax = int(i.get("price", "").get("amount", ""))/100000000
        assets = i.get("assets", "")
        for a in assets:
            asset_id = a.get("asset_id")
            schema_name = a.get("schema", "").get("schema_name", "")
            template = a.get("template", "")
            if template is not None:
                template = (a.get("template", "").get("immutable_data", "").get("name", ""))
                template_id = a.get("template", "").get("template_id", "")
            prices = a.get("prices", "")
            amount = 0
            suggested_average = 0
            suggested_median = 0
            if prices is not None:
                for p in prices:
                    if a.get("backed_tokens", ""):
                        backed_tokens = a.get("backed_tokens", "")
                        for b in backed_tokens:
                            amount = int(b.get("amount", ""))/100000000

                    suggested_average = int(p.get("suggested_average", ""))/100000000
                    suggested_median = int(p.get("suggested_median", ""))/100000000
                    min = int(p.get("min", ""))/100000000
                    sales = p.get("sales", "")

        if 1 < price_wax * 1.3 < suggested_median and int(sales) > 100:
            print(f"\n{Colors.GREEN}{timer()}{Colors.RESET} 1 < {Colors.GREEN}{sale_url}{Colors.RESET} price: {Colors.GREEN}{price_wax}{Colors.RESET} < suggested_median: {Colors.GREEN}{suggested_median}{Colors.RESET}")
            count, average_sales = history_price(collection_name, schema_name, template_id)
            if count >= 3 and average_sales > 4:
                result = check_price(template_id, collection_name)
                if result is not None:
                    price_asc, round_price_asc, average_price = result
                    print(f"{Colors.GREEN}{timer()}{Colors.RESET} {Colors.GREEN}{price_wax:.2f}{Colors.RESET} price: {Colors.GREEN}{price_wax*price_multiplier:.2f}{Colors.RESET} < price_asc: {Colors.GREEN}{round_price_asc[1]}{Colors.RESET} average_price: {Colors.GREEN}{average_price}{Colors.RESET}")
                    if price_wax * price_multiplier < price_asc[1]:
                        purchasesale(sale_id, listing_symbol)
                        listing_price = "{:.8f} WAX".format(float(price_asc[1]*99)/100)
                        atomicsale(asset_id, listing_price)
                        if price_wax >= 1:
                            result_start.append(
                                {
                                    "coll_name": coll_name,
                                    "sale_url": sale_url,
                                    "template": template,
                                    "price_wax": "{:.2f}".format(price_wax),
                                    "price_asc": round_price_asc,
                                    "average_price": average_price,
                                    "suggested_average": "{:.2f}".format(suggested_average),
                                    "suggested_median": "{:.2f}".format(suggested_median),
                                    "min": min,
                                    "sales": sales,
                                    "seller": seller,
                                    "seller_url": seller_url,
                                    "sale_id": sale_id,
                                    "amount": amount
                                }
                            )

        elif 1 > price_wax * 10 < suggested_median:
            print(f"\n{Colors.RED}{timer()} 1> {Colors.RED}{sale_url} price: {Colors.RED}{price_wax} < suggested_median: {Colors.RED}{suggested_median}{Colors.RESET}")
            count, average_sales = history_price(collection_name, schema_name, template_id)
            if count >= 3 and average_sales > 4:
                result = check_price(template_id, collection_name)
                if result is not None:
                    price_asc, round_price_asc, average_price = result
                    print(f"{Colors.RED}{timer()}{Colors.RESET} {Colors.RED}{price_wax:.2f}{Colors.RESET} price: {Colors.RED}{price_wax*price_multiplier:.2f}{Colors.RESET} < price_asc: {Colors.RED}{round_price_asc[1]}{Colors.RESET} average_price: {Colors.RED}{average_price}{Colors.RESET}")
                    if price_wax * price_multiplier < price_asc[1]:
                        purchasesale(sale_id, listing_symbol)
                        listing_price = "{:.8f} WAX".format(float(price_asc[1]*99)/100)
                        atomicsale(asset_id, listing_price)
                        result_start.append(
                            {
                                "coll_name": coll_name,
                                "sale_url": sale_url,
                                "template": template,
                                "price_wax": "{:.2f}".format(price_wax),
                                "price_asc": round_price_asc,
                                "average_price": average_price,
                                "suggested_average": "{:.2f}".format(suggested_average),
                                "suggested_median": "{:.2f}".format(suggested_median),
                                "min": min,
                                "sales": sales,
                                "seller": seller,
                                "seller_url": seller_url,
                                "sale_id": sale_id,
                                "amount": amount
                            }
                        )

        all_id.append(sale_id)
        all_id_list = list(all_id)

    if len(result_start) > 0:
        print(f':::::::::::::::::::::::::price_wax_3: {price_wax}')
        # pprint(result_start)
        save_results(result_start)


def main():
    start_data()


if __name__ == "__main__":
    main()
