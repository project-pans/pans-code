#!/usr/bin/python3

import RPi.GPIO as GPIO
import mysql.connector
from datetime import datetime
from hx711 import HX711
import time
import sys
import os

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

    filepath = "/home/ubuntu/weight_data.txt"
    tolerance = 150
    skip_flag = False

    referenceUnit1 = -64
    referenceUnit2 = -41
    referenceUnit3 = -50
    referenceUnit4 = -46

    weight1 = weight(5, 6, "", "", 0, 0, -1)
    weight2 = weight(9, 10, "", "", 0, 0, -1)
    weight3 = weight(23, 24, "", "", 0, 0, -1)
    weight4 = weight(17, 27, "", "", 0, 0, -1)
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

    now = datetime.now()
    sql = "INSERT INTO items_item (name, upc, quantity, percent, date, weight) VALUES (%s, %s, %s, %s, %s, %s)"
    val = [
        ("", "", 1, 0, now, 1),
        ("", "", 1, 0, now, 2),
        ("", "", 1, 0, now, 3),
        ("", "", 1, 0, now, 4),
    ]
    mycursor.executemany(sql, val)
    mydb.commit()

    val = []
    while (True):
        try:
            if(os.stat(filepath).st_size != 0):
                with open(filepath, 'r+') as fp:
                    results = fp.read()
                    fp.truncate(0)
                    data = results.strip('()').split(',')
                    data=[x.strip().strip('\'') for x in data]
                    upc = data[0]
                    name = data[1]
                if (len(upc) != 0):
                    print("Item scanned")
                    while (True):
                        if (hx1.get_weight(5) - weight1.last_weight >= tolerance):
                            time.sleep(3)
                            weight1.initial_weight = hx1.get_weight(5)
                            weight1.curr_weight = weight1.initial_weight
                            print("Initial Weight 1: ", weight1.initial_weight)
                            weight1.name = name
                            weight1.upc = upc
                            sql = "UPDATE items_item SET percent = %s, name = %s, upc = %s, date = %s WHERE weight = %s"
                            val = (100, weight1.name, weight1.upc, datetime.now(), 1)
                            hx1.power_down()
                            hx1.power_up()
                            time.sleep(0.1)
                            mycursor.execute(sql, val)
                            skip_flag = True
                            break
                        elif (hx2.get_weight(5) - weight2.last_weight >= tolerance):
                            time.sleep(3)
                            weight2.initial_weight = hx2.get_weight(5)
                            weight2.curr_weight = weight2.initial_weight
                            print("Initial Weight 2: ", weight2.initial_weight)
                            weight2.name = name
                            weight2.upc = upc
                            sql = "UPDATE items_item SET percent = %s, name = %s, upc = %s, date = %s WHERE weight = %s"
                            val = (100, weight2.name, weight2.upc, datetime.now(), 2)
                            hx2.power_down()
                            hx2.power_up()
                            time.sleep(0.1)
                            mycursor.execute(sql, val)
                            skip_flag = True
                            break
                        elif (hx3.get_weight(5) - weight3.last_weight >= tolerance):
                            time.sleep(3)
                            weight3.initial_weight = hx3.get_weight(5)
                            weight3.curr_weight = weight3.initial_weight
                            print("Initial Weight 3: ", weight3.initial_weight)
                            weight3.name = name
                            weight3.upc = upc
                            sql = "UPDATE items_item SET percent = %s, name = %s, upc = %s, date = %s WHERE weight = %s"
                            val = (100, weight3.name, weight3.upc, datetime.now(), 3)
                            hx3.power_down()
                            hx3.power_up()
                            time.sleep(0.1)
                            mycursor.execute(sql, val)
                            skip_flag = True
                            break
                        elif (hx4.get_weight(5) - weight4.last_weight >= tolerance):
                            time.sleep(3)
                            weight4.initial_weight = hx4.get_weight(5)
                            weight4.curr_weight = weight4.initial_weight
                            print("Initial Weight 4: ", weight4.initial_weight)
                            weight4.name = name
                            weight4.upc = upc
                            sql = "UPDATE items_item SET percent = %s, name = %s, upc = %s, date = %s WHERE weight = %s"
                            val = (100, weight4.name, weight4.upc, datetime.now(), 4)
                            hx4.power_down()
                            hx4.power_up()
                            time.sleep(0.1)
                            mycursor.execute(sql, val)
                            skip_flag = True
                            break

            weight1.last_weight = weight1.curr_weight
            weight2.last_weight = weight2.curr_weight
            weight3.last_weight = weight3.curr_weight
            weight4.last_weight = weight4.curr_weight

            if (skip_flag != True):
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

            if skip_flag:
                skip_flag = False

            if weight1.curr_weight - weight1.last_weight >= tolerance and weight1.initial_weight != 0:
                time.sleep(3)
                print("Weight 1: ", weight1.curr_weight)
                weight1.curr_weight = hx1.get_weight(5)
                sql = "UPDATE items_item SET percent = %s WHERE weight = %s"
                percent = weight1.curr_weight / weight1.initial_weight
                if percent > 1:
                    val = (100, 1)
                else:
                    val = (percent * 100, 1)
                mycursor.execute(sql, val)

            if weight1.last_weight - weight1.curr_weight >= tolerance:
                time.sleep(3)
                print("Weight 1: ", weight1.curr_weight)
                sql = "UPDATE items_item SET percent = %s WHERE weight = %s"
                val = (0, 1)
                mycursor.execute(sql, val)

            if weight2.curr_weight - weight2.last_weight >= tolerance and weight2.initial_weight != 0:
                time.sleep(3)
                print("Weight 2: ", weight2.curr_weight)
                weight2.curr_weight = hx2.get_weight(5)
                sql = "UPDATE items_item SET percent = %s WHERE weight = %s"
                percent = weight2.curr_weight / weight2.initial_weight
                if percent > 1:
                    val = (100, 2)
                else:
                    val = (percent * 100, 2)
                mycursor.execute(sql, val)
            if weight2.last_weight - weight2.curr_weight >= tolerance:
                time.sleep(3)
                print("Weight 2: ", weight2.curr_weight)
                sql = "UPDATE items_item SET percent = %s WHERE weight = %s"
                val = (0, 2)
                mycursor.execute(sql, val)

            if weight3.curr_weight - weight3.last_weight >= tolerance and weight3.initial_weight != 0:
                time.sleep(3)
                weight3.curr_weight = hx3.get_weight(5)
                print("Weight 3: ", weight3.curr_weight)
                sql = "UPDATE items_item SET percent = %s WHERE weight = %s"
                percent = weight3.curr_weight / weight3.initial_weight
                if percent > 1:
                    val = (100, 3)
                else:
                    val = (percent * 100, 3)
                mycursor.execute(sql, val)

            if weight3.last_weight - weight3.curr_weight >= tolerance:
                time.sleep(3)
                print("Weight 3: ", weight3.curr_weight)
                sql = "UPDATE items_item SET percent = %s WHERE weight = %s"
                val = (0, 3)
                mycursor.execute(sql, val)

            if weight4.curr_weight - weight4.last_weight >= tolerance and weight4.initial_weight != 0:
                time.sleep(3)
                weight4.curr_weight = hx4.get_weight(5)
                print("Weight 4: ", weight4.curr_weight)
                sql = "UPDATE items_item SET percent = %s WHERE weight = %s"
                percent = weight4.curr_weight / weight4.initial_weight
                if percent > 1:
                    val = (100, 4)
                else:
                    val = (percent * 100, 4)
                mycursor.execute(sql, val)

            if weight4.last_weight - weight4.curr_weight >= tolerance:
                time.sleep(3)
                print("Weight 4: ", weight4.curr_weight)
                sql = "UPDATE items_item SET percent = %s WHERE weight = %s"
                val = (0, 4)
                mycursor.execute(sql, val)

            mydb.commit()

        except (KeyboardInterrupt, SystemExit):
            GPIO.cleanup()
            sys.exit()


if __name__ == "__main__":
    main()
