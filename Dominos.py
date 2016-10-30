from bs4 import BeautifulSoup
import re
import math
import requests
import datetime

class Dominos:
    session = None
    safe_postcode = ""
    headers = ""
    storeid = 0
    jar = None

    def __init__(self, postcode, headers):
        self.session = requests.session()
        safe_postcode = postcode.replace(" ", "+")
        self.safe_postcode = safe_postcode
        self.headers = headers
        base_url = 'https://www.dominos.co.uk'
        # Make request to homepage, obtain cookie
        res = self.session.get(base_url + '/Home/SessionExpire')
        jar = res.cookies
        # Send postcode
        res = self.session.get(base_url + '/storefindermap/storesearch?searchText=' + safe_postcode, cookies=jar, headers=headers)
        storeid = res.json()['localStore']['id']
        self.storeid = storeid
        print('Ordering from: ' + res.json()['localStore']['name'])
        new_headers = self.headers
        new_headers['X-XSRF-TOKEN'] = jar['XSRF-TOKEN']
        res = self.session.post(base_url + '/Journey/Initialize', data = {'fulfilmentMethod':'delivery', 'storeid': storeid, 'postcode': postcode}, cookies=jar, headers=new_headers)
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
        new_headers = self.headers
        new_headers['Content-Type'] = 'application/json'
        new_headers['X-XSRF-TOKEN'] = self.jar['XSRF-TOKEN']
        current_time = datetime.datetime.now(datetime.timezone.utc)
        unix_timestamp = str(round(current_time.timestamp()))
        # res = self.session.get('https://www.dominos.co.uk/ProductCatalog/GetStoreContext', cookies=self.jar, headers=self.headers)
        menuVersion = str(1)
        new_headers = self.headers
        new_headers['X-XSRF-TOKEN'] = self.jar['XSRF-TOKEN']
        res = self.session.get('https://www.dominos.co.uk/ProductCatalog/GetStoreCatalog?collectionOnly=false&menuVersion=' + menuVersion + '&storeId=' + str(self.storeid), cookies=self.jar, headers=self.headers).json()
        # Get pizza part of menu
        pizzas = []
        for menu in res:
            if menu['name'] == 'Pizza':
                for sc in menu['subcategories']:
                    for product in sc['products']:
                        bases = []
                        sizes = []
                        for sku in product['productSkus']:
                            size = re.search('([A-z]+)', sku['name']).group(1)
                            size_measure = re.search('([0-9]*(.[0-9]?))"', sku['name']).group(1)
                            price = sku['price']
                            area = math.pi * math.pow((float(size_measure) / 2), 2)
                            cost_per_area = float(price) / area
                            sizes.append({'size': size, 'size_measure': size_measure, 'price': price, 'cost_per_area': cost_per_area})
                        bases.append({'name': 'Italian', 'sizes': sizes})
                        desc = re.search('[^.]+', product['description']).group(0)
                        description = []
                        for d in desc.split(','):
                            description.append(d.strip())
                        pizzas.append({'name': product['name'], 'bases': bases, 'description': description})
        return pizzas


    def get_deals(self):
        new_headers = self.headers
        new_headers['Content-Type'] = 'application/json'
        new_headers['X-XSRF-TOKEN'] = self.jar['XSRF-TOKEN']
        res = self.session.get('https://www.dominos.co.uk/Deals/StoreDealGroups', cookies=self.jar, headers=new_headers)
        print(res.headers)
        match = re.search('application\/json', res.headers['Content-Type'])
        if not match:
            self.session = requests.session()
            base_url = 'https://www.dominos.co.uk'
            # Make request to homepage, obtain cookie
            res = self.session.get(base_url + '/Home/SessionExpire', cookies=self.jar, headers=self.headers)
            # Send postcode
            res = self.session.get(base_url + '/storefindermap/storesearch?searchText=' + self.safe_postcode, cookies=self.jar, headers=self.headers)
            storeid = res.json()['localStore']['id']
            self.storeid = storeid
            print('Ordering from: ' + res.json()['localStore']['name'])
            new_headers = self.headers
            new_headers['X-XSRF-TOKEN'] = self.jar['XSRF-TOKEN']
            res = self.session.post(base_url + '/Journey/Initialize', data = {'fulfilmentMethod':'delivery', 'storeid': storeid, 'postcode': self.safe_postcode.replace("+", " ")}, cookies=self.jar, headers=new_headers)
            print('found error')
            print('-----------------')
            res = self.session.get('https://www.dominos.co.uk/Deals/StoreDealGroups', cookies=self.jar, headers=new_headers)
            print(res.text)
        try:
            res = res.json()
        except Exception as e:
            res = [{'storeDeals': []}] 
        deals = []
        for d in res[0]['storeDeals']:
            for e in d['deals']:
                deals.append({'name': e['name'], 'description': e['description']})
        return deals
