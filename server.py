from lib2to3.pgen2 import driver
from urllib import response
from flask import Flask, jsonify, send_file, request, url_for
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
from flask import Flask
from flask_cors import CORS, cross_origin
import os
import pymysql
from dotenv import load_dotenv
import secrets

app = Flask(__name__)
# app.config['JSON_SORT_KEYS'] = False
CORS(app)



@app.route('/get_races')
def get_races():
    a = fastf1.get_event_schedule(1950,include_testing=False, force_ergast=False)
    # a.load()
    races = []
    for i in a["Location"].tolist():
        nData = unicodedata.normalize('NFKD', i).encode('ASCII', 'ignore')
        races.append(nData.decode())
    
    return jsonify(races=races)

@app.route('/get_image')
def get_image():
    
    return send_file('test.png', mimetype='image/png')


@app.route("/drivers")
# @cross_origin()

def drivers():
    fastf1.Cache.enable_cache('C:/Users/mnobr/Desktop/Projects/F1-Fantasy/flask-server/cache')

    abu_dhabi_race = fastf1.get_session(2022, 'Australia', 'R')

    abu_dhabi_race.load()

    abu_dhabi_race.results.Q1 = abu_dhabi_race.results.Q1.astype(object).where(abu_dhabi_race.results.Q1.notnull(), None)
    abu_dhabi_race.results.Q2 = abu_dhabi_race.results.Q2.astype(object).where(abu_dhabi_race.results.Q2.notnull(), None)
    abu_dhabi_race.results.Q3 = abu_dhabi_race.results.Q3.astype(object).where(abu_dhabi_race.results.Q3.notnull(), None)
    abu_dhabi_race.results.Time = None


    a_dictionary = {}
    
    for title in abu_dhabi_race.results.to_dict():
        if title!="DriverNumber":
            for driverNumber in abu_dhabi_race.results["DriverNumber"].tolist():
                if driverNumber not in a_dictionary:
                    a_dictionary[driverNumber] = [str(abu_dhabi_race.results[title][driverNumber])]
                else:
                    a_dictionary[driverNumber] += [str(abu_dhabi_race.results[title][driverNumber])]



    return jsonify(result= [abu_dhabi_race.results.to_dict()])
 
@app.route('/getRaceResults', methods = ['GET', 'POST'])
def getRaceResults():
    
    fastf1.Cache.enable_cache('C:/Users/mnobr/Desktop/Projects/F1-Fantasy/flask-server/cache')
    data = request.get_json()

    abu_dhabi_race = fastf1.get_session(int(data["year"]), data["race"], 'R')

    abu_dhabi_race.load()
    
    abu_dhabi_race.results.Q1 = abu_dhabi_race.results.Q1.astype(object).where(abu_dhabi_race.results.Q1.notnull(), None)
    abu_dhabi_race.results.Q2 = abu_dhabi_race.results.Q2.astype(object).where(abu_dhabi_race.results.Q2.notnull(), None)
    abu_dhabi_race.results.Q3 = abu_dhabi_race.results.Q3.astype(object).where(abu_dhabi_race.results.Q3.notnull(), None)
    

    times = {}
    for driver in abu_dhabi_race.results["DriverNumber"]: 
        # print(abu_dhabi_race.results.Time[driver]-abu_dhabi_race.results.Time[0])
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
    
    swapedKeyVal = dict(zip(raceResults["Position"].values(), raceResults["Position"].keys()))
    # print(swapedKeyVal) #needs to sort the Java Script racers, also braindrain 
    for key in list(swapedKeyVal.keys()):
        swapedKeyVal[str(key).replace(".0", "")] = swapedKeyVal.pop(key)
        
    # print(swapedKeyVal)
    
    return jsonify(result = [raceResults], position = swapedKeyVal)
 
@app.route('/sendYear', methods = ['GET', 'POST'])
def sendYear():
    
    fastf1.Cache.enable_cache('C:/Users/mnobr/Desktop/Projects/F1-Fantasy/flask-server/cache')

    data = request.get_json()
    
    a = fastf1.get_event_schedule(int(data["year"]),include_testing=False, force_ergast=False)
    # a.load()
    races = []
    for i in a["EventName"].tolist():
        nData = unicodedata.normalize('NFKD', i).encode('ASCII', 'ignore')
        races.append(nData.decode())
    
    # print(races)
    return jsonify(races=races, year=int(data["year"]))

@app.route('/signUp', methods = ['POST'])
def signUp():

    data = request.get_json()
    
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
    cur.execute("INSERT INTO users (fname, lname, email, pass) VALUES (%s, %s, %s, %s )", (data["firstName"], data["lastName"], data["email"], data["pass"]))
    conn.commit()

    return "done"

@app.route('/logIn', methods = ['GET', 'POST'])
def logIn():

    data = request.get_json()
    
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
    cur.execute("SELECT count(*) FROM users WHERE email = %s", (data["email"]))
    result=cur.fetchone()
    email=result[0]
    cur.execute("SELECT count(*) FROM users WHERE pass = %s", (data["pass"]))
    result=cur.fetchone()
    password=result[0]
    # print(email > 0 and password > 0)

    # cur.execute("INSERT INTO test2 (fname, lname, email, pass) VALUES (%s, %s, %s, %s )", (data["firstName"], data["lastName"], data["email"], data["pass"]))
    

    if email > 0 and password > 0:
        token=secrets.token_urlsafe(10)
        cur.execute("UPDATE users SET token = %s WHERE email = %s", (token, data["email"]))
        conn.commit()
        return jsonify(loginVerification=True, token=token)
    else:
        conn.commit()
        return jsonify(loginVerification=False)

@app.route('/getUserName', methods = ['GET', 'POST'])
def getUserName():

    data = request.get_json()
    
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
    # print(data["token"])
    cur.execute("SELECT fname, lname FROM users WHERE token = %s", (data["token"]))
    result=cur.fetchall()

    # cur.execute("INSERT INTO test2 (fname, lname, email, pass) VALUES (%s, %s, %s, %s )", (data["firstName"], data["lastName"], data["email"], data["pass"]))

    return jsonify(name=result[0][0] + " " + result[0][1])  

@app.route('/driversInfo', methods = ['GET', 'POST'])
def driversInfo():

    data = request.get_json()
    
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
    # print(data["token"])
    cur.execute("SELECT * FROM drivers")
    result=cur.fetchall()

    # cur.execute("INSERT INTO test2 (fname, lname, email, pass) VALUES (%s, %s, %s, %s )", (data["firstName"], data["lastName"], data["email"], data["pass"]))

    driversList = []
    constructorsList =[]

    for drivers in result:
        driversList.append({"id": drivers[0], "driver": drivers[1], "driverImg": drivers[2], "cost": drivers[3]})

    cur.execute("SELECT * FROM constructors")
    result=cur.fetchall()

    for constructors in result:
        constructorsList.append({"id": constructors[0], "constructor": constructors[1], "constructorImg": constructors[2], "cost": constructors[3]})


    # print(driversList)
    return jsonify(driverList=driversList, constructorList=constructorsList) 

@app.route('/saveTeam', methods = ['POST'])
def saveTeam():

    data = request.get_json()
    
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
    # print(data["token"])
    cur.execute("SELECT id FROM users WHERE token = %s", (data["token"]))
    result=cur.fetchall()

    userID = result[0][0]
    teamList = {"slot1":"", "slot2":"", "slot3":"", "slot4":"", "slot5":"", "slot6":""}
    i = 1

    for info in data["team"]:
        if (info["id"] < 21):
            teamList["slot" + str(i)] = info["id"]
            i += 1
        elif (info["id"] > 100):
            teamList["slot6"] = info["id"]
            i += 1

    # print(data["teamName"])


    cur.execute("INSERT INTO teams (userID, slot1, slot2, slot3, slot4, slot5, slot6, maxBudget, teamName) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s )", (userID, teamList["slot1"], teamList["slot2"], teamList["slot3"], teamList["slot4"], teamList["slot5"], teamList["slot6"], data["budget"], data["teamName"]))
    conn.commit()

    return jsonify(teamList=data)  

@app.route('/getUsersTeams', methods = ['POST'])
def getUsersTeams():

    data = request.get_json()
    
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

    teamList = {}

    cur=conn.cursor()
    # print(data["token"])
    cur.execute("SELECT id FROM users WHERE token = %s", (data["token"]))
    result=cur.fetchall()

    userID = result[0][0]

    cur.execute("SELECT * FROM teams WHERE userID = %s", (userID))
    result=cur.fetchall()

    # print("result is: " + str(result))
    currentTeam = []
    
    for team in result:
        # print(team)
        # for i in range(2,len(result[1])):
        for i in range(2,10):
            if (i<7):
                #driver
                if (team[i] != 0):
                    # print("driver: " + str(team[i]))
                    cur.execute("SELECT * FROM drivers WHERE id = %s", (team[i]))
                    result=cur.fetchall()[0]
                    currentTeam.append({"cost":result[3], "driver":result[1], "driverImg":result[2], "id":result[0]})

            elif (i==7):
                #constructor
                if (team[i] != 0):
                    # print("constructor: " + str(team[i]))
                    cur.execute("SELECT * FROM constructors WHERE id = %s", (team[i]))
                    result=cur.fetchall()[0]
                    currentTeam.append({"cost":result[3], "constructor":result[1], "constructorImg":result[2], "id":result[0]})

            elif (i==8):
                #budget
                budget=team[i]
                # print("budget: " + str(team[i]))
            elif (i==9):
                teamName = str(team[i])  
                # print("teamName: " + str(team[i]))     
                teamList[teamName] = currentTeam 
                currentTeam = []
                

            

           
    cur.execute("SELECT * FROM drivers WHERE id = 14")
    result=cur.fetchall()[0]

    #cost[3], driver[1], driverIMG[2], id[0]
        
    # print("---------------------------------------------")
    # print(teamList)

    return jsonify(teamList=teamList, budget=budget)  

if __name__ == "__main__":
    app.run(debug=True)


