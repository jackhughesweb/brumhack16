#!/usr/bin/env python3
from PizzaHut import PizzaHut
from Dominos import Dominos

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'
headers = {'User-Agent': user_agent}

from flask import Flask
from flask import request
from flask import jsonify
app = Flask(__name__)

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/jquery-3.1.1.min.js")
def jquery():
    return app.send_static_file('jquery-3.1.1.min.js')

@app.route("/dominos.ico")
def dominos():
    return app.send_static_file('dominos.ico')

@app.route("/pizzahut.ico")
def pizzahut():
    return app.send_static_file('pizzahut.ico')

@app.route("/res.json")
def json():
    return app.send_static_file('res.json')

@app.route("/lookup")
def lookup():
    postcode = request.args.get('postcode')
    print(postcode)
    ph = PizzaHut(postcode, headers)
    phz = ph.get_pizzas()
    dm = Dominos(postcode, headers)
    dmz = dm.get_pizzas()
    dmd = dm.get_deals()
    arr = {'pizzas': [phz, dmz], 'deals': dmd}
    dm = None
    return jsonify({'response': arr})

if __name__ == "__main__":
    app.run()
