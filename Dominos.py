from bs4 import BeautifulSoup
import re
import math
import requests
import datetime

class Dominos:
    safe_postcode = ""
    headers = ""
    storeid = 0
    jar = None

    def __init__(self, postcode, headers):
        safe_postcode = postcode.replace(" ", "+")
        self.safe_postcode = safe_postcode
        self.headers = headers
        base_url = 'https://www.dominos.co.uk'
        # Make request to homepage, obtain cookie
        res = requests.get(base_url)
        jar = res.cookies
        # Send postcode
        res = requests.get(base_url + '/storefindermap/storesearch?searchText=' + safe_postcode, cookies=jar, headers=headers)
        storeid = res.json()['localStore']['id']
        self.storeid = storeid
        print('Ordering from: ' + res.json()['localStore']['name'])
        # res = requests.post(base_url + '/Journey/Initialize', data = {'fulfilmentMethod':'delivery', 'storeid': storeid, 'postcode': postcode, : storeid}, cookies=jar, headers=headers)
        self.jar = jar


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
        print(self.jar)
        new_headers = self.headers
        new_headers['Content-Type'] = 'application/json'
        current_time = datetime.datetime.now(datetime.timezone.utc)
        unix_timestamp = str(round(current_time.timestamp()))
        # res = requests.get('https://www.dominos.co.uk/ProductCatalog/GetStoreContext', cookies=self.jar, headers=self.headers)
        menuVersion = str(1)
        res = requests.get('https://www.dominos.co.uk/ProductCatalog/GetStoreCatalog?collectionOnly=false&menuVersion=' + menuVersion + '&storeId=' + str(self.storeid), cookies=self.jar, headers=self.headers).json()
        # Get pizza part of menu
        pizzas = []
        for menu in res:
            if menu['name'] == 'Pizza':
                for sc in menu['subcategories']:
                    for product in sc['products']:
                        bases = []
                        sizes = []
                        for sku in product['productSkus']:
                            print(sku['name'])
                            size = re.search('([A-z]+)', sku['name']).group(1)
                            size_measure = re.search('([0-9]*(.[0-9]?))"', sku['name']).group(1)
                            price = sku['price']
                            area = math.pi * math.pow((float(size_measure) / 2), 2)
                            cost_per_area = float(price) / area
                            sizes.append({'size': size, 'size_measure': size_measure, 'price': price, 'cost_per_area': cost_per_area})
                        bases.append({'name': 'Italian', 'sizes': sizes})
                        description = re.search('[^.]+', product['description']).group(0)
                        description = map(lambda x: x.strip(), description.split(','))
                        pizzas.append({'name': product['name'], 'bases': bases, 'description': description})
        return pizzas
