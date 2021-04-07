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

in_out_port = 16
weight_port = 4
GPIO.setup(in_out_port, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(weight_port, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def main():
    try:
        while True:
            upcnumber = barcode_reader()
            print(upcnumber)
            info = UPC_lookup(upcnumber)
            print(info)
            if GPIO.input(weight_port) == 1:
                with open("/home/ubuntu/weight_data.txt", "a") as weight_file:
                    weight_file.write(str(info))
            else:
                database(info)
            print("done")
    except KeyboardInterrupt:
        logging.debug("Keyboard interrupt")
    except Exception as err:
        logging.error(err)


def database(barcode_results):
    upc = barcode_results[0]
    name = barcode_results[1]

    switch_value = GPIO.input(in_out_port)

    sql = "SELECT quantity FROM items_item WHERE upc = %s"
    val = (upc,)
    mycursor.execute(sql, val)
    quantity = mycursor.fetchone()

    if switch_value == 0:
        if quantity is None:
            sql = "INSERT INTO items_item (name, upc, quantity, percent, date, weight_num) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (name, upc, 1, 0, datetime.now(), 0)
        else:
            sql = "UPDATE items_item SET quantity = %s WHERE name = %s"
            val = (quantity[0] + 1, name)

        mycursor.execute(sql, val)
        mydb.commit()

    else:
        if quantity is not None:
            if quantity[0] == 1:
                sql = "DELETE FROM items_item WHERE name = %s"
                val = (name,)
            else:
                sql = "UPDATE items_item SET quantity = %s WHERE name = %s"
                val = (quantity[0] - 1, name)
                
            mycursor.execute(sql, val)
            mydb.commit()


def UPC_lookup(upc):

    headers = {
        "cache-control": "no-cache",
    }

    url = "https://api.upcitemdb.com/prod/trial/lookup?upc=" + upc
    print(url)
    resp = requests.get(url, headers=headers)
    data = json.loads(resp.text)
    if data["code"] == "OK":
        for item in data["items"]:
            return upc, item["title"]
    else:
        url = "https://api.upcdatabase.org/product/" + upc + "?apikey=apikey"
        print(url)
        resp = requests.get(url, headers=headers)
        data = json.loads(resp.text)
        if data["success"] == True:
            return upc, data["title"]
        else:
            print ("Item Not Found")
            #url = "https://api.barcodespider.com/v1/lookup?token=apikey&upc=" + upc
            #print(url)
            #resp = requests.get(url, headers=headers)
            #data = json.loads(resp.text)
            #if data["code"] == 200:
                #for item in data["item_attributes"]:
                    #return upc, item["title"]
            #else:
                #print("item not found")

if __name__ == "__main__":
    main()
