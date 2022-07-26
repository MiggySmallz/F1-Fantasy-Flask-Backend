from click import password_option
from flask import Flask, jsonify
from wsgiref.validate import validator
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib import cm
import fastf1
from fastf1.core import Laps
from fastf1 import utils
from fastf1 import plotting
plotting.setup_mpl()
from timple.timedelta import strftimedelta
import unicodedata
import json
import boto3
import mysql.connector
import sys
import os
import pymysql
from dotenv import load_dotenv





def raceStats():
    fastf1.Cache.enable_cache('C:/Users/mnobr/Desktop/Projects/F1-Fantasy/flask-server/cache')

    abu_dhabi_race = fastf1.get_session(2022, 'Australia', 'R')

    abu_dhabi_race.load()

    # abu_dhabi_race.results.Q1 = abu_dhabi_race.results.Q1.astype(object).where(abu_dhabi_race.results.Q1.notnull(), None)
    # abu_dhabi_race.results.Q2 = abu_dhabi_race.results.Q2.astype(object).where(abu_dhabi_race.results.Q2.notnull(), None)
    # abu_dhabi_race.results.Q3 = abu_dhabi_race.results.Q3.astype(object).where(abu_dhabi_race.results.Q3.notnull(), None)


    laps_r = abu_dhabi_race.laps


    # driver1 = 'PER'
    # driver2 = 'VER'

    # ham_fastest_lap = laps_r.pick_driver(driver1).pick_fastest()
    # ham_car_data = ham_fastest_lap.get_car_data()
    # ver_fastest_lap = laps_r.pick_driver(driver2).pick_fastest()
    # ver_car_data = ver_fastest_lap.get_car_data()

    # h = ham_car_data['Time']
    # v = ver_car_data['Time']

    # velocityH = ham_car_data['Speed']
    # velocityV = ver_car_data['Speed']
    # fig, ax = plt.subplots(figsize=(12,8))
    # ax.plot(h, velocityH, label=driver1, color='cyan')
    # ax.plot(v, velocityV, label=driver2, color='red')

    # ax.set_xlabel('Time')
    # ax.set_ylabel('Speed [Km/h]')
    # ax.set_title("Hamilton VS Verstappin fastest lap")
    # ax.legend()
    # plt.show()
    # fig.savefig('C:/Users/mnobr/Desktop/Projects/F1-Fantasy/flask-server/test.png')

    a = fastf1.get_event_schedule(2010,include_testing=False, force_ergast=False)
    # a.load()
    races = []
    for i in a["Location"].tolist():
        nData = unicodedata.normalize('NFKD', i).encode('ASCII', 'ignore')
        races.append(nData.decode())
        
    print(abu_dhabi_race.results.to_dict())


def test1():
    fastf1.Cache.enable_cache('C:/Users/mnobr/Desktop/Projects/F1-Fantasy/flask-server/cache')
    
    abu_dhabi_race = fastf1.get_session(2022, 'Australia', 'R')

    abu_dhabi_race.load()

    times = {}
    for driver in abu_dhabi_race.results["DriverNumber"]: 
        print(abu_dhabi_race.results.Time[driver]-abu_dhabi_race.results.Time[0])
        if (abu_dhabi_race.results.Time[driver]!=abu_dhabi_race.results.Time[0]):
            if len(str(abu_dhabi_race.results.Time[driver]-abu_dhabi_race.results.Time[0]).split(" ")) == 3:
                if str(abu_dhabi_race.results.Time[driver]-abu_dhabi_race.results.Time[0]).split(" ")[2][:-3].split(":")[1] == "00":
                    times[driver] = "+"+str(abu_dhabi_race.results.Time[driver]-abu_dhabi_race.results.Time[0]).split(" ")[2][:-3].split(":")[2]+"s"
                else:
                    times[driver] = "+"+str(abu_dhabi_race.results.Time[driver]-abu_dhabi_race.results.Time[0]).split(" ")[2][:-3].split(":")[1]+":"+str(abu_dhabi_race.results.Time[driver]-abu_dhabi_race.results.Time[0]).split(" ")[2][:-3].split(":")[2]
            else: 
                times[driver] = abu_dhabi_race.results.Status[driver]
        else:
            times[driver] = str(abu_dhabi_race.results.Time[driver]).split(" ")[2][:-3]

    raceResults = abu_dhabi_race.results.to_dict()
    raceResults["Time"] = times
    
    
    print(raceResults)

def load_cache(year):
    fastf1.Cache.enable_cache('C:/Users/mnobr/Desktop/Projects/F1-Fantasy/flask-server/cache')
    
    result = None
    race_num = 1

    while result == None:
        try:
            race = fastf1.get_session(year, race_num, 'R')
            race.load()
            a = race.event.EventDate
            print(a)
            race_num += 1
        except:
            result = "error"
    


def testDB():
    

    load_dotenv()

    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    USER = os.getenv('USER')
    PASSWORD = os.getenv('PASSWORD')
    DB = os.getenv('DB')

    conn = pymysql.connect(
            host= HOST, 
            port = int(PORT),
            user = USER, 
            password = PASSWORD,
            db = DB,
            )

    cur=conn.cursor()
    cur.execute("INSERT INTO test2 (id, fname, lname, email, pass) VALUES (1, 'Miguel', 'Nobre', 'mnobre24@gmail.com', '1234qwer')")
    conn.commit()

testDB()
# raceStats()




