from bs4 import BeautifulSoup
import re
import math
import requests
import datetime
import urllib.parse

class PizzaHut:
    safe_postcode = ""
    headers = ""
    jar = None

    def __init__(self, postcode, headers):
        safe_postcode = urllib.parse.quote_plus(postcode)
        self.safe_postcode = safe_postcode
        self.headers = headers
        base_url = 'https://www.pizzahut.co.uk'
        # Make request to homepage, obtain cookie
        res = requests.get(base_url)
        jar = res.cookies
        # Send postcode
        res = requests.get(base_url + '/delivery/ordernowvalidated?postcode=' + safe_postcode, cookies=jar, headers=headers)
        # Get stores
        current_time = datetime.datetime.now(datetime.timezone.utc)
        unix_timestamp = str(round(current_time.timestamp()))
        time = current_time.strftime('%Y-%m-%d')
        res = requests.get(base_url + '/store/storesearchjson?clientOrderType=2&orderTime=' + time + '%2015%3A11&postcode=' + safe_postcode + '&longitude=0&latitude=0&isAsap=true&selectedStoreId=&_=' + unix_timestamp, cookies=jar, headers=headers).json()
        store = res[0]
        print('Ordering from: ' + store['StoreName'])
        store_id = store['StoreId']
        res = requests.get(base_url + '/store/storeopencheck?storeId=' + str(store_id) + '&orderDateTime=' + time + '%2015%3A11&isAsap=true&isDelivery=true&_=' + unix_timestamp, cookies=jar, headers=headers)
        res = requests.get(base_url + '/store/getmenuandstartorderjson?storeId=' + str(store_id) + '&orderClassId=2&fulfillmentTimeTypeId=1&orderTime=' + time + '%2015%3A37&currentMenuId=0&postCode=' + safe_postcode + '&addressId=&platformType=&changePreviousSelection=&isAsap=true&voucherCode=&_=' + unix_timestamp, cookies=jar, headers=headers)
        res = requests.get(base_url + '/menu/startyourorder?redirectTo=Pizza', cookies=jar, headers=headers)
        self.jar = jar


    def parse_base_size(self, base):
        p = '([A-z]*)_([0-9]*)_([0-9]*)_([0-9]*)_([0-9]*.[0-9]*)_([0-9]*)'
        m = re.search(p, base)
        size_measure = 9.5
        if m.group(1) == 'Medium':
            size_measure = 11.5
        if m.group(1) == 'Large':
            size_measure = 13.5
        area = math.pi * math.pow((size_measure / 2), 2)
        cost_per_area = float(m.group(5)) / area
        return {'size': m.group(1), 'size_measure': size_measure, 'sku': m.group(2), 'product_id': m.group(3), 'half_half_product_id': m.group(4), 'price': m.group(5), 'cost_per_area': cost_per_area, 'favourite': m.group(6)}


    def parse_bases(self, base_html):
        bases = []
        for base in base_html.find(attrs={'class': 'pizzabase'}).find_all('option'):
            title = base.get_text()
            sizes = []
            for size in base:
                if 'data-large' in base.attrs:
                    sizes.append(self.parse_base_size(base['data-large']))
                if 'data-medium' in base.attrs:
                    sizes.append(self.parse_base_size(base['data-medium']))
                if 'data-small' in base.attrs:
                    sizes.append(self.parse_base_size(base['data-small']))
            bases.append({'name': title, 'sizes': sizes})
        return bases


    def parse_pizzas(self, pizza_html):
        pizzas_raw = pizza_html.find(id='pizza-product-list')
        pizzas = []
        for pizza in pizzas_raw.find_all(attrs={'class': 'pizza-product'}):
            title = pizza.find(attrs={'class': 'product-title'}).get_text()
            description = map(lambda x: x.strip(), pizza.find(attrs={'class': 'product-description'}).get_text().split(','))
            bases = self.parse_bases(pizza)
            pizzas.append({'name': title, 'description': description, 'bases': bases})
        return pizzas


    def print_pizzas(pizzas):
        for pizza in pizzas:
            print('=============')
            print(pizza['name'])
            for desc in pizza['description']:
                print('"' + desc + '"')
            print('-------------')
            for base in pizza['bases']:
                print(base['name'])
                for size in base['sizes']:
                    print('> ' + str(size['size']) + ' - £' + str(size['price']) + ' (' + str(size['cost_per_area']) + 'pounds per square inch)')


    def get_pizzas(self):
        res = requests.get('https://www.pizzahut.co.uk/menu/pizza', cookies=self.jar, headers=self.headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        return self.parse_pizzas(soup)
