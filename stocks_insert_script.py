#!/usr/bin/env python3

from influxdb import InfluxDBClient
import json
import requests
import time


client = InfluxDBClient(host='localhost', port=8086)
client.create_database('stocks')

measurement_name = 'stocks_data'
data_end_time = int(time.time() * 1000)
data = []


def get_stock_prices():
    quotes_data = requests.get("https://financialmodelingprep.com/api/v3/"
                               "stock/real-time-price/AAPL,FB,GOOG,MSFT,NFLX")
    quotes_json = quotes_data.json()
    companies = quotes_json["companiesPriceList"]
    for company in companies:
        data.append(
            {
                "measurement": "stocks_data",
                "tags": {
                    "company": company["symbol"]
                },
                "fields": {
                    "price": company["price"]
                },
                "time": data_end_time
            }
        )

    client.write_points(data, database='stocks', time_precision='ms',
                        protocol='json')


def run(interval=60*60*24):  # interval in seconds
    while 1:
        try:
            get_stock_prices()
            sleep(interval)
        except KeyboardInterrupt:
            quit()
        except:
            pass


run()

