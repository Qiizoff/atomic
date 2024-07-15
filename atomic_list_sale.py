import eospy.cleos
import eospy.keys
import config
import time
import requests

from datetime import datetime
from colors import Colors


def atomicsale(asset_id, listing_price):
    now = datetime.now()
    print(f"{Colors.BLUE}{now.strftime('%H:%M:%S')} atomicsale:{Colors.RESET} asset_id: {Colors.BLUE}{asset_id}{Colors.RESET} listing_price: {Colors.BLUE}{listing_price}{Colors.RESET}")
    # ce = eospy.cleos.Cleos(url="https://wax.greymass.com")
    ce = eospy.cleos.Cleos(url=" https://wax.pink.gg")
    private_key = eospy.keys.EOSKey(config.API_PR_KEY)

    payload = {
        "announcesale": {
            "account": "atomicmarket",
            "args": {
                "asset_ids": [asset_id],
                "listing_price": listing_price,
                "maker_marketplace": "",
                "seller": "crazyfrog.gm",
                "settlement_symbol": "8,WAX",
            },
            "authorization": [{
                "actor": "crazyfrog.gm",
                "permission": "active",
            }],
        },
        "createoffer": {
            "account": "atomicassets",
            "args": {
                "memo": "sale",
                "recipient": "atomicmarket",
                "recipient_asset_ids": [],
                "sender": "crazyfrog.gm",
                "sender_asset_ids": [asset_id],
            },
            "authorization": [{
                "actor": "crazyfrog.gm",
                "permission": "active",
            }],
        },
    }

    data = {k: str(ce.abi_json_to_bin(v["account"], k, v["args"])["binargs"]) for k, v in payload.items()}

    actions = [{
        "account": v["account"],
        "name": k,
        "authorization": v["authorization"],
        "data": data[k],
    } for k, v in payload.items()]

    transaction = {"actions": actions}

    try:
        print(f"{Colors.BLUE}{now.strftime('%H:%M:%S')} atomicsale: https://wax.atomichub.io/explorer/asset/wax-mainnet/{asset_id} start{Colors.RESET}")
        ce.push_transaction(transaction, keys=[private_key])
        print(f"{Colors.BLUE}{now.strftime('%H:%M:%S')} atomicsale: complete{Colors.RESET}")
        time.sleep(1)
    except requests.exceptions.HTTPError as e:
        print(f"\n{now.strftime('%H:%M:%S')} ========URL_atomicsale========")
        print(f"asset: https://wax.atomichub.io/explorer/asset/wax-mainnet/{asset_id}")
        print(f"{e}")
        print(f"{now.strftime('%H:%M:%S')} ========URL_atomicsale========")
