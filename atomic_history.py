import requests
import statistics
import time
from datetime import datetime, timedelta


def check_price(template_id=1, collection_name=None):
    headers = {
        'accept': 'application/json'}

    params = {
        'limit': 10,
        'order': 'asc',
        'sort': 'price',
        'state': '1',
        'template_id': template_id,
        'collection_name': collection_name}
    
    response = requests.get('https://wax.api.atomicassets.io/atomicmarket/v2/sales', headers=headers, params=params)
    print(f'check_price: {response.url}')
    response.raise_for_status()

    data = response.json().get('data', [])

    price_asc = [round(int(i.get('price', {}).get('amount', 0)) / 100000000, 2) for i in data]
    average_price = round(statistics.mean(price_asc), 2)

    # print(f'price_asc: {price_asc}\nprice_sum: {average_price}')
    return price_asc, average_price

def history_price(collection_name, schema_name, template_id):
    headers = {'accept': 'application/json'}

    params = {
        'collections_name': collection_name,
        'schema_name': schema_name,
        'symbol': 'WAX',
        'template_id': template_id
    }

    response = requests.get('https://wax.api.atomicassets.io/atomicmarket/v1/prices/sales/days', headers=headers, params=params)
    # print(f'response: {response.url}')
    price_sales = []
    old_time = (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')

    data = response.json().get('data', [])
    for i in data[:5]:
        # print(datetime.utcfromtimestamp(i.get('time', '') / 1000).strftime('%Y-%m-%d %H:%M:%S'))
        median = float(i.get('median', 0))/100000000
        median = '{:.2f}'.format(median)
        average = float(i.get('average', 0))/100000000
        average = round(average, 2)
        sales = i.get('sales', '')
        epoch_time = datetime.utcfromtimestamp(i.get('time', '') / 1000).strftime('%Y-%m-%d %H:%M:%S')
        # print(f'average: {average} median: {median} sales: {sales} epoch_time: {epoch_time}')
        if epoch_time <= old_time:
            continue
        if not sales or float(sales) <= 1:
            break
        price_sale = {'median': median, 'average': average, 'sales': sales, 'epoch_time': epoch_time}
        price_sales.append(price_sale)   

    return price_sales

# collection_name = 'dungeonitems'
# template_id = '488449'
# schema_name = 'collabs'

# collection_name = 'alien.worlds'
# template_id = '19553'
# schema_name = 'tool.worlds'

collection_name = 'ntoons.funko'
template_id = '658348'
schema_name = 'series2.drop'
price_wax = 1

price_sales = history_price(collection_name, schema_name, template_id)
if price_sales:
    print(f'2:::::price_sales: {price_sales}')
    price_asc, average_price = check_price(template_id, collection_name)
    print(f'3:::::price_asc: {price_asc} average_price:{average_price}')
    print(f'4:::::price_wax: {price_wax} price_asc:{price_asc[1]}')
    if price_wax < price_asc[1]:
        print(f'price_wax: {price_wax} < average_price: {average_price}')
    else:
        print(f'average_price is low')