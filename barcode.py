#!/usr/bin/python3

import requests
import json
from scanner import barcode_reader
import RPi.GPIO as GPIO
import mysql.connector
from datetime import datetime

GPIO.setmode(GPIO.BCM)

mydb = mysql.connector.connect(
    host="localhost", user="user", password="password", database="pans_data"
)
mycursor = mydb.cursor()

port = 17
GPIO.setup(port, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def database(barcode_results):
    upc = barcode_results[0]
    name = barcode_results[1]

    switch_value = GPIO.input(port)

    sql = "SELECT quantity FROM items_item WHERE upc = %s"
    val = (upc,)
    mycursor.execute(sql, val)
    quantity = mycursor.fetchone()

    if switch_value == 0:
        if quantity is None:
            sql = "INSERT INTO items_item (name, upc, quantity, weight, date) VALUES (%s, %s, %s, %s, %s)"
            val = (name, upc, 1, 0, datetime.now())
        else:
            sql = "UPDATE items_item SET quantity = %s WHERE name = %s"
            val = (quantity[0] + 1, name)
    else:
        if quantity[0] == 1:
            sql = "DELETE FROM items_item WHERE name = %s"
            val = (name,)
        elif quantity is not None:
            sql = "UPDATE items_item SET quantity = %s WHERE name = %s"
            val = (quantity[0] - 1, name)

    mycursor.execute(sql, val)
    mydb.commit()


def UPC_lookup(upc):
    # '''V3 API'''

    headers = {
        "cache-control": "no-cache",
    }

    url = "https://api.upcitemdb.com/prod/trial/lookup?upc=" + upc
    print(url)
    resp = requests.get(url, headers=headers)
    data = json.loads(resp.text)
    for item in data["items"]:
        return upc, item["title"]


if __name__ == "__main__":
    try:
        while True:
            upcnumber = barcode_reader()
            print(upcnumber)
            info = UPC_lookup(upcnumber)
            print(info)
            database(info)
            print("done")
    except KeyboardInterrupt:
        logging.debug("Keyboard interrupt")
    except Exception as err:
        logging.error(err)
