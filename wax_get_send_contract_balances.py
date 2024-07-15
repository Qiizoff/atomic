import requests
import eospy.cleos
import eospy.keys
from wax_make_deposit import make_deposit

depo = 100


def get_contract_balances():
    url = "https://wax.pink.gg/v1/chain/get_table_rows"

    jsonobj = {
        "code": "atomicmarket",
        "json": True,
        "limit": 100,
        "lower_bound": "crazyfrog.gm",
        "scope": "atomicmarket",
        "table": "balances",
        "upper_bound": "crazyfrog.gm"
    }

    data = requests.post(url, json=jsonobj).json()
    data = data['rows'][0]['quantities'][0]
    print(f"Contract Balances: {data}")
    return data


def start_depo():
    balances = get_contract_balances()
    balances = float(balances.split()[0])
    if balances <= depo - 5:
        quantity = depo - balances
        quantity_str = str(quantity) + " WAX"
        print(f"Make deposit: {quantity_str}")
        make_deposit(quantity)
    else:
        return


def main():
    start_depo()


if __name__ == "__main__":
    main()