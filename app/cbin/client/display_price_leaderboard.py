# python -m pip install requests

import json
import requests
import time

URL = "http://20.76.107.117:443"

if __name__ == '__main__':    

    while True:
        # Fetch data from the URL
        data_raw = requests.get(URL + "/normalizedCapitals")
        data = json.loads(data_raw.content.decode('utf-8'))

        # Sorting the JSON by value in descending order
        sorted_data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))

        price_raw = requests.get(URL + "/price/EURGBP")
        price = json.loads(price_raw.content.decode('utf-8'))["price"]

        # Output the sorted JSON
        print('PRICE: ' + str(price))
        print('LEADERBOARD')
        print(json.dumps(sorted_data, indent=2))

        # Wait for 10 seconds before the next iteration
        time.sleep(10)