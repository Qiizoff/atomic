import eospy.keys
import eospy.cleos
import config


def make_deposit(quantity):
    quantity = "{:.8f} WAX".format(int(quantity*100)/100)
    # ce = eospy.cleos.Cleos(url="https://api.waxsweden.org/")
    ce = eospy.cleos.Cleos(url=" https://wax.pink.gg")
    private_key = eospy.keys.EOSKey(config.API_PR_KEY)
    payload = [
        {
            "args": {
                "from": "crazyfrog.gm",
                "to": "atomicmarket",
                "quantity": quantity,
                "memo": "deposit",
            },
            "account": "eosio.token",
            "name": "transfer",
            "authorization": [{"actor": "crazyfrog.gm","permission": "active"}],
        }
    ]
    data = ce.abi_json_to_bin(payload[0]["account"], payload[0]["name"], payload[0]["args"])
    data = str(data["binargs"])
    actions = [
        {
        "account": "eosio.token",
        "name": "transfer",
        "authorization": [{"actor": "crazyfrog.gm", "permission": "active"}],
        "data": data
        }
    ]

    trx = {"actions": actions}
    print (f'trx {trx}')

    try:
        print(f"make_deposit: {quantity} start")
        ce.push_transaction(trx, keys=[private_key])
        print(f"make_deposit: {quantity} complete")
    except Exception as e:
        print(f"make_deposit: {quantity} error: {e}")


# quantity = 1
# make_deposit(quantity)