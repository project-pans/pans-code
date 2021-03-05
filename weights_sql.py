#!/usr/bin/python3

import RPi.GPIO as GPIO
import mysql.connector
from datetime import datetime
from hx711 import HX711


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


mydb = mysql.connector.connect(
    host="localhost", user="user", password="password", database="pans_data"
)
mycursor = mydb.cursor()

referenceUnit1 = 1
referenceUnit2 = 1

weight1 = weight(13, 19, "", "", 0, 0, -1)
weight2 = weight(13, 19, "", "", 0, 0, -1)
weight3 = weight(20, 21, "", "", 0, 0, -1)
weight4 = weight(20, 21, "", "", 0, 0, -1)
# (DT, SCK)
hx1 = HX711(weight1.dt, weight1.sck)
hx2 = HX711(weight3.dt, weight3.sck)
hx1.set_reading_format("MSB", "MSB")
hx2.set_reading_format("MSB", "MSB")

hx1.set_reference_unit(referenceUnit1)
hx2.set_reference_unit(referenceUnit2)

hx1.reset()
hx2.reset()

hx1.tare_A()
hx1.tare_B()
hx2.tare_A()
hx2.tare_B()

weight1.name = "Flour"
weight2.name = "Sugar"
weight3.name = "Baking Soda"
weight4.name = "Syrup"
weight1.upc = "123"
weight2.upc = "456"
weight3.upc = "789"
weight4.upc = "246"
weight1.initial_weight = abs(hx1.get_weight_A(5))
weight2.initial_weight = abs(hx1.get_weight_B(5))
weight3.initial_weight = abs(hx2.get_weight_A(5))
weight4.initial_weight = abs(hx2.get_weight_B(5))

now = datetime.now()
sql = "INSERT INTO items_item (name, upc, quantity, percent, date) VALUES (%s, %s, %s, %s, %s)"
val = [
    (weight1.name, weight1.upc, 1, 100, now),
    (weight2.name, weight2.upc, 1, 100, now),
    (weight3.name, weight3.upc, 1, 100, now),
    (weight4.name, weight4.upc, 1, 100, now),
]
mycursor.executemany(sql, val)
mydb.commit()

val = []
for i in range(10):
    weight1.last_weight = weight1.curr_weight
    weight2.last_weight = weight2.curr_weight
    weight3.last_weight = weight3.curr_weight
    weight4.last_weight = weight4.curr_weight

    weight1.curr_weight = abs(hx1.get_weight_A(5))
    weight2.curr_weight = abs(hx1.get_weight_B(5))
    weight3.curr_weight = abs(hx2.get_weight_A(5))
    weight4.curr_weight = abs(hx2.get_weight_B(5))

    if weight1.curr_weight != weight1.last_weight:
        sql = "UPDATE items_item SET percent = %s WHERE name = %s"
        val = (
            (weight1.curr_weight / weight1.initial_weight) * 100,
            weight1.name,
        )
        mycursor.execute(sql, val)

    if weight2.curr_weight != weight2.last_weight:
        sql = "UPDATE items_item SET percent = %s WHERE name = %s"
        val = (
            (weight2.curr_weight / weight2.initial_weight) * 100,
            weight2.name,
        )
        mycursor.execute(sql, val)

    if weight3.curr_weight != weight3.last_weight:
        sql = "UPDATE items_item SET percent = %s WHERE name = %s"
        val = (
            (weight3.curr_weight / weight3.initial_weight) * 100,
            weight3.name,
        )
        mycursor.execute(sql, val)

    if weight4.curr_weight != weight4.last_weight:
        sql = "UPDATE items_item SET percent = %s WHERE name = %s"
        val = (
            (weight4.curr_weight / weight4.initial_weight) * 100,
            weight4.name,
        )
        mycursor.execute(sql, val)

    mydb.commit()

    print("Weight 1: ", weight1.curr_weight)
    print("Weight 2: ", weight2.curr_weight)
    print("Weight 3: ", weight3.curr_weight)
    print("Weight 4: ", weight4.curr_weight)
    print()

GPIO.cleanup()
