#!/usr/bin/python3

import RPi.GPIO as GPIO
import mysql.connector
from datetime import datetime
from hx711 import HX711
from barcode import UPC_lookup
import time
import sys

class weight:
    def __init__(
        self, dt, sck, name, upc, initial_weight, curr_weight, last_weight
    ):
        self.dt = dt
        self.sck = sck
        self.name = name
        self.upc = upc
        self.initial_weight = initial_weight
        self.curr_weight = curr_weight
        self.last_weight = last_weight

def main():
    mydb = mysql.connector.connect(
        host="localhost", user="user", password="password", database="pans_data"
    )
    mycursor = mydb.cursor()

    referenceUnit1 = -68
    referenceUnit2 = 1
    referenceUnit3 = 1
    referenceUnit4 = 1

    weight1 = weight(17, 27, "", "", 0, 0, -1)
    weight2 = weight(13, 19, "", "", 0, 0, -1)
    weight3 = weight(20, 21, "", "", 0, 0, -1)
    weight4 = weight(20, 21, "", "", 0, 0, -1)
    # (DT, SCK)
    hx1 = HX711(weight1.dt, weight1.sck)
    hx2 = HX711(weight2.dt, weight2.sck)
    hx3 = HX711(weight3.dt, weight3.sck)
    hx4 = HX711(weight4.dt, weight4.sck)
    hx1.set_reading_format("MSB", "MSB")
    hx2.set_reading_format("MSB", "MSB")
    hx3.set_reading_format("MSB", "MSB")
    hx4.set_reading_format("MSB", "MSB")

    hx1.set_reference_unit(referenceUnit1)
    hx2.set_reference_unit(referenceUnit2)
    hx3.set_reference_unit(referenceUnit3)
    hx4.set_reference_unit(referenceUnit4)

    hx1.reset()
    hx2.reset()
    hx3.reset()
    hx4.reset()

    hx1.tare()
    hx2.tare()
    hx3.tare()
    hx4.tare()

    weight1.name = "Flour"
    weight2.name = "Sugar"
    weight3.name = "Baking Soda"
    weight4.name = "Syrup"
    weight1.upc = "123"
    weight2.upc = "456"
    weight3.upc = "789"
    weight4.upc = "246"
    weight1.curr_weight = hx1.get_weight(5)
    weight2.curr_weight = hx2.get_weight(5)
    weight3.curr_weight = hx3.get_weight(5)
    weight4.curr_weight = hx4.get_weight(5)
    hx1.power_down()
    hx1.power_up()
    hx2.power_down()
    hx2.power_up()
    hx3.power_down()
    hx3.power_up()
    hx4.power_down()
    hx4.power_up()
    time.sleep(0.1)

    skip = False
    now = datetime.now()
    sql = "INSERT INTO items_item (name, upc, quantity, percent, date) VALUES (%s, %s, %s, %s, %s)"
    val = [
        (weight1.name, weight1.upc, 1, 0, now),
        (weight2.name, weight2.upc, 1, 0, now),
        (weight3.name, weight3.upc, 1, 0, now),
        (weight4.name, weight4.upc, 1, 0, now),
    ]
    mycursor.executemany(sql, val)
    mydb.commit()

    val = []
    while (True):
        try:
            weight1.last_weight = weight1.curr_weight
            weight2.last_weight = weight2.curr_weight
            weight3.last_weight = weight3.curr_weight
            weight4.last_weight = weight4.curr_weight

            weight1.curr_weight = hx1.get_weight(5)
            weight2.curr_weight = hx2.get_weight(5)
            weight3.curr_weight = hx3.get_weight(5)
            weight4.curr_weight = hx4.get_weight(5)
            print(weight1.curr_weight)
            hx1.power_down()
            hx1.power_up()
            hx2.power_down()
            hx2.power_up()
            hx3.power_down()
            hx3.power_up()
            hx4.power_down()
            hx4.power_up()
            time.sleep(0.1)

            #Barcode Idea: Read file that scanner writes to. If last line does not equal previous last line and switch is flipped to weights, new item has been placed. Poll weight values to see which weight
            #item was placed and update initial weight and name accordingly.
            if weight1.curr_weight > weight1.initial_weight and weight1.last_weight < 50 and weight1.curr_weight > 50:
                time.sleep(3)
                weight1.initial_weight = hx1.get_weight(5)
                skip = True
                sql = "UPDATE items_item SET percent = %s WHERE name = %s"
                val = (100, weight1.name)
                mycursor.execute(sql, val)
                hx1.power_down()
                hx1.power_up()
                time.sleep(0.1)
            if weight2.curr_weight > weight2.last_weight and weight2.last_weight < 50 and weight2.curr_weight > 50:
                time.sleep(3)
                weight2.initial_weight = hx2.get_weight(5)
                sql = "UPDATE items_item SET percent = %s WHERE name = %s"
                val = (100, weight2.name)
                mycursor.execute(sql, val)
                hx2.power_down()
                hx2.power_up()
                time.sleep(0.1)
            if weight3.curr_weight > weight3.last_weight and weight3.last_weight < 50 and weight3.curr_weight > 50:
                time.sleep(3)
                weight3.initial_weight = hx3.get_weight(5)
                sql = "UPDATE items_item SET percent = %s WHERE name = %s"
                val = (100, weight3.name)
                hx3.power_down()
                hx3.power_up()
                time.sleep(0.1)
                mycursor.execute(sql, val)
            if weight4.curr_weight > weight4.last_weight and weight4.last_weight < 50 and weight4.curr_weight > 50:
                time.sleep(3)
                weight4.initial_weight = hx4.get_weight(5)
                sql = "UPDATE items_item SET percent = %s WHERE name = %s"
                val = (100, weight4.name)
                mycursor.execute(sql, val)
                hx4.power_down()
                hx4.power_up()
                time.sleep(0.1)

            if weight1.curr_weight < weight1.initial_weight and abs(weight1.last_weight - weight1.curr_weight) >= 20:
                sql = "UPDATE items_item SET percent = %s WHERE name = %s"
                if weight1.curr_weight < 0:
                    percent = 0
                else:
                    percent = weight1.curr_weight / weight1.initial_weight
                val = (percent * 100, weight1.name)
                mycursor.execute(sql, val)
            if weight2.curr_weight < weight2.initial_weight and abs(weight2.last_weight - weight2.curr_weight) >= 20:
                sql = "UPDATE items_item SET percent = %s WHERE name = %s"
                if weight2.curr_weight < 0:
                    percent = 0
                else:
                    percent = weight2.curr_weight / weight2.initial_weight
                val = (percent * 100, weight2.name)
                mycursor.execute(sql, val)
            if weight3.curr_weight < weight3.initial_weight and abs(weight3.last_weight - weight3.curr_weight) >= 20:
                sql = "UPDATE items_item SET percent = %s WHERE name = %s"
                if weight3.curr_weight < 0:
                    percent = 0
                else:
                    percent = weight3.curr_weight / weight3.initial_weight
                val = (percent * 100, weight3.name)
                mycursor.execute(sql, val)
            if weight4.curr_weight < weight4.initial_weight and abs(weight4.last_weight - weight4.curr_weight) >= 20:
                sql = "UPDATE items_item SET percent = %s WHERE name = %s"
                if weight4.curr_weight < 0:
                    percent = 0
                else:
                    percent = weight4.curr_weight / weight4.initial_weight
                val = (percent * 100, weight4.name)
                mycursor.execute(sql, val)

            mydb.commit()

        except (KeyboardInterrupt, SystemExit):
            GPIO.cleanup()
            sys.exit()
main()
