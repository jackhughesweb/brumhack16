#!/usr/bin/env python3
import urllib.parse
from PizzaHut import PizzaHut

postcode = 'B15 2TT'
safe_postcode = urllib.parse.quote_plus(postcode)

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'
headers = {'User-Agent': user_agent}

ph = PizzaHut(safe_postcode, headers)
phz = ph.get_pizzas()
PizzaHut.print_pizzas(phz)