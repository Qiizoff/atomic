import requests
import eospy.cleos
import eospy.keys
import config
import time

from datetime import datetime
from colors import Colors


def get_delphi_median():
    now = datetime.now()
    # url = "https://wax.eosphere.io/v1/chain/get_table_rows"
    # url = "https://wax.greymass.com/v1/chain/get_table_rows"
    url = "https://wax.pink.gg/v1/chain/get_table_rows"

    jsonobj = {
        "code": "delphioracle",
        "index_position": 1,
        "json": True,
        "key_type": "",
        "limit": "1",
        "lower_bound": None,
        "reverse": False,
        "scope": "waxpusd",
        "show_payer": False,
        "table": "datapoints",
        "upper_bound": None
    }

    data = requests.post(url, json=jsonobj).json()
    median = data['rows'][0]['median']
    print(f"{now.strftime('%H:%M:%S')} median: {median}")
    return median


def purchasesale(sale_id, listing_symbol):
    now = datetime.now()
    print(f"{Colors.MAGENTA}{now.strftime('%H:%M:%S')} purchasesale:{Colors.RESET} sale_id: {Colors.MAGENTA}{sale_id}{Colors.RESET} listing_symbol: {Colors.MAGENTA}{listing_symbol}{Colors.RESET}")
    intended_delphi_median = 0
    if listing_symbol != "WAX":
        intended_delphi_median = get_delphi_median()

    try:
        # ce = eospy.cleos.Cleos(url="https://wax.greymass.com")
        ce = eospy.cleos.Cleos(url=" https://wax.pink.gg")
        private_key = eospy.keys.EOSKey(config.API_PR_KEY)
        payload = [
            {
                "args": {
                    "buyer": "crazyfrog.gm",
                    "sale_id": sale_id,
                    "intended_delphi_median": intended_delphi_median,
                    "taker_marketplace": "",
                },
                "account": "atomicmarket",
                "name": "purchasesale",
                "authorization": [{"actor": "crazyfrog.gm", "permission": "active"}],
            }
        ]

        data = ce.abi_json_to_bin(payload[0]["account"], payload[0]["name"], payload[0]["args"])
        data = str(data["binargs"])

        actions = [
            {
                "account": "atomicmarket",
                "name": "purchasesale",
                "authorization": [{"actor": "crazyfrog.gm", "permission": "active"}],
                "data": data
            }
        ]

        trx = {"actions": actions}

        print(f"{Colors.MAGENTA}{now.strftime('%H:%M:%S')} purchasesale: https://wax.atomichub.io/market/sale/{sale_id} start{Colors.RESET}")
        ce.push_transaction(trx, keys=[private_key])
        print(f"{Colors.MAGENTA}{now.strftime('%H:%M:%S')} purchasesale: complete{Colors.RESET}")

    except Exception as e:
        print(f"\n{now.strftime('%H:%M:%S')} ========URL_purchasesale========")
        print(f"Ошибка: {e}")
        print(f"========URL_purchasesale========")
        pass


# purchasesale(110978223, "USD")
