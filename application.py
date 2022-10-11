from copyreg import constructor
from lib2to3.pgen2 import driver
from re import A
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

application = Flask(__name__)
# app.config['JSON_SORT_KEYS'] = False #
app = application
CORS(app)


HOST = os.getenv('HOST')
PORT = 3306
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
DB = os.getenv('DB')


# HOST = 'f1-fantasy.cxitdoz2usg3.us-east-2.rds.amazonaws.com'
# PORT = 3306
# USER = 'admin'
# # PASSWORD = os.environ['PASSWORD']
# PASSWORD = os.getenv('PASSWORD')
# DB = 'Table1'

@app.route('/')
def root():
    return "DONE"

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
    fastf1.Cache.enable_cache('./cache')

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
    
    fastf1.Cache.enable_cache('./cache')
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
    
    fastf1.Cache.enable_cache('./cache')

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

    conn = pymysql.connect(
            host= HOST, 
            port = PORT,
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

    conn = pymysql.connect(
            host= HOST, 
            port = PORT,
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

    conn = pymysql.connect(
            host= HOST, 
            port = PORT,
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

    conn = pymysql.connect(
            host= HOST, 
            port = PORT,
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

    conn = pymysql.connect(
            host= HOST, 
            port = int(PORT),
            user = USER, 
            password = PASSWORD,
            db = DB,
            )

    cur=conn.cursor()
    cur.execute("SELECT * FROM teams WHERE teamName = %s", (data["teamName"]))
    isTeam = len(cur.fetchall())
    
    teamList = {"slot1":"", "slot2":"", "slot3":"", "slot4":"", "slot5":"", "slot6":""}
    i = 1

    for info in data["team"]:
        if (info["id"] < 21):
            teamList["slot" + str(i)] = info["id"]
            i += 1
        elif (info["id"] > 100):
            teamList["slot6"] = info["id"]
            i += 1

    # print(isTeam)
    if (isTeam==0):

        cur.execute("INSERT INTO teams (slot1, slot2, slot3, slot4, slot5, slot6, maxBudget, teamName) VALUES (%s, %s, %s, %s, %s, %s, %s, %s )", (teamList["slot1"], teamList["slot2"], teamList["slot3"], teamList["slot4"], teamList["slot5"], teamList["slot6"], data["budget"], data["teamName"]))
        conn.commit()

        # gets the most recent teamID
        cur.execute("SELECT * FROM teams")
        teamID = cur.fetchall()[len(cur.fetchall())-1][0]

# TESTING --------------------------------------------------------

        cur.execute("SELECT userID FROM users WHERE token = %s", (data["token"]))
        userID = cur.fetchall()[0][0]
        cur.execute("INSERT INTO league_teams (userID, leagueID, teamID) VALUES (%s, null, %s)", (userID, teamID))

# TESTING --------------------------------------------------------

        
# TO DELETE --------------------------------------------
        #gets user's current list of teams
        cur.execute("SELECT teamID FROM users WHERE token = %s", (data["token"]))
        currentTeams = cur.fetchall()[0][0]

        newTeamList = str(currentTeams)+ "," + str(teamID)

        if (currentTeams)!=None:
            cur.execute("UPDATE users SET teamID = %s WHERE token = %s", (newTeamList, data["token"]))
            conn.commit()
        elif (currentTeams)==None:
            cur.execute("UPDATE users SET teamID = %s WHERE token = %s", (teamID, data["token"]))
            conn.commit()
# TO DELETE --------------------------------------------

    elif (isTeam>0):
        
        cur.execute("UPDATE teams SET slot1 = %s, slot2 = %s, slot3 = %s, slot4 = %s, slot5 = %s, slot6 = %s, maxBudget = %s WHERE teamName = %s", (teamList["slot1"], teamList["slot2"], teamList["slot3"], teamList["slot4"], teamList["slot5"], teamList["slot6"], data["budget"], data["teamName"]))
        conn.commit()

    return jsonify(teamList=data)  

@app.route('/getUsersTeams', methods = ['POST'])
def getUsersTeams():

    data = request.get_json()
    
    load_dotenv()

    conn = pymysql.connect(
            host= HOST, 
            port = int(PORT),
            user = USER, 
            password = PASSWORD,
            db = DB,
            )

    teamList = {}

    cur=conn.cursor()
    
    budget = 100,000,000

# DELETE ------------------------------------------
    # # Gets list of user's teams
    # cur.execute("SELECT teamID FROM users WHERE token = %s", (data["token"]))
    # result=cur.fetchall()
    # userTeams = result[0][0]
    # newuserTeams = tuple(userTeams.split(','))

    


    # cur.execute("SELECT * FROM teams WHERE teamID IN %s;", (newuserTeams,))
    # # cur.execute("SELECT * FROM Table1.`teams(old)` WHERE userID = 3;")
    
    # result=cur.fetchall()
    # print(result)
# DELETE ------------------------------------------

    cur.execute("SELECT userID FROM users WHERE token = %s", (data["token"]))
    userID=cur.fetchall()[0][0]
    cur.execute("SELECT teamID FROM league_teams WHERE userID = %s", (userID))
    userTeamss = [i[0] for i in cur.fetchall()]
    cur.execute("SELECT * FROM teams WHERE teamID IN %s;", (userTeamss,))
    result=cur.fetchall()


    currentTeam = []
    
    for team in result:
        for i in range(2,10):
            if (i<7):
                #driver
                if (team[i] != 0):
                    cur.execute("SELECT * FROM drivers WHERE id = %s", (team[i]))
                    result=cur.fetchall()[0]
                    currentTeam.append({"cost":result[3], "driver":result[1], "driverImg":result[2], "id":result[0]})

            elif (i==7):
                #constructor
                if (team[i] != 0):
                    cur.execute("SELECT * FROM constructors WHERE id = %s", (team[i]))
                    result=cur.fetchall()[0]
                    currentTeam.append({"cost":result[3], "constructor":result[1], "constructorImg":result[2], "id":result[0]})

            elif (i==8):
                #budget
                budget=team[i]
                currentTeam.append({"budget":budget})

            elif (i==9):
                #teamName
                teamName = str(team[i])   
                teamList[teamName] = currentTeam 
                currentTeam = []

    return jsonify(teamList=teamList, budget=budget)  

@app.route('/deleteTeam', methods = ['POST'])
def deleteTeam():

    data = request.get_json()
    
    load_dotenv()

    conn = pymysql.connect(
            host= HOST, 
            port = int(PORT),
            user = USER, 
            password = PASSWORD,
            db = DB,
            )

    cur=conn.cursor()
    cur.execute("SELECT teamID FROM teams WHERE teamName = %s", (data["teamName"]))
    teamID = cur.fetchall()[0][0]


    cur.execute("DELETE FROM league_teams WHERE teamID = %s", (teamID))
    conn.commit()


# Delete -------------------------------------
    cur.execute("SELECT teamID FROM users WHERE token = %s", (data["token"]))
    userTeams = cur.fetchall()[0][0]

    # removes team from list of user teams
    userTeams = userTeams.split(",")
    userTeams.remove(str(teamID))
    newTeamsList = ""
    for i in userTeams:
        newTeamsList += i+","

    cur.execute("UPDATE users SET teamID = %s WHERE token = %s", (newTeamsList[:-1], data["token"]))
    conn.commit()
# Delete -------------------------------------

    cur.execute("DELETE FROM teams WHERE teamName = %s", (data["teamName"]))
    conn.commit()

    return "done"

@app.route('/createLeague', methods = ['POST'])
def createLeague():

    data = request.get_json()
    
    load_dotenv() 

    conn = pymysql.connect(
            host= HOST, 
            port = PORT,
            user = USER, 
            password = PASSWORD,
            db = DB,
            )

    cur=conn.cursor()
    cur.execute("SELECT * FROM leagues WHERE leagueName = %s", (data["leagueName"]))
    isLeague = len(cur.fetchall())
    
    if (isLeague==0):

        cur.execute("INSERT INTO leagues (leagueName, leaguePass) VALUES (%s, %s)", (data["leagueName"], data["leaguePass"]))
        conn.commit()

        #gets the most recent leagueID
        cur.execute("SELECT * FROM leagues")
        leagueID = cur.fetchall()[len(cur.fetchall())-1][0]

# TESTING --------------------------------------------------------

        cur.execute("SELECT userID FROM users WHERE token = %s", (data["token"]))
        userID = cur.fetchall()[0][0]
        cur.execute("INSERT INTO league_teams (userID, leagueID, teamID) VALUES (%s, %s, null)", (userID, leagueID))
        conn.commit()

# TESTING --------------------------------------------------------


# DELETE --------------------------------------------------------
        # #gets user's current list of leagues
        # cur.execute("SELECT leagueID FROM users WHERE token = %s", (data["token"]))
        # currentLeagues = cur.fetchall()[0][0]
        # newLeagueList = str(currentLeagues)+ "," + str(leagueID)


        # if (currentLeagues)!=None:
        #     cur.execute("UPDATE users SET leagueID = %s WHERE token = %s", (newLeagueList, data["token"]))
        #     conn.commit()
        # elif (currentLeagues)==None:
        #     cur.execute("UPDATE users SET leagueID = %s WHERE token = %s", (leagueID, data["token"]))
        #     conn.commit()
# DELETE --------------------------------------------------------

    elif (isLeague>0):
        
        print("already league")

    return "done"


@app.route('/getUsersLeagues', methods = ['POST'])
def getUsersLeagues():

    data = request.get_json()
    
    load_dotenv()

    conn = pymysql.connect(
            host= HOST, 
            port = int(PORT),
            user = USER, 
            password = PASSWORD,
            db = DB,
            )

    cur=conn.cursor()

    cur.execute("SELECT userID FROM users WHERE token = %s", (data["token"]))
    userID=cur.fetchall()[0][0]
    cur.execute("SELECT leagueID FROM league_teams WHERE userID = %s", (userID))
    userleagues = [i[0] for i in cur.fetchall()]
    cur.execute("SELECT * FROM leagues WHERE leagueID IN %s;", (userleagues,))
    result=cur.fetchall()

# DELETE ------------------------------------------
    # # Gets list of user's leagues
    # cur.execute("SELECT leagueID FROM users WHERE token = %s", (data["token"]))
    # result=cur.fetchall()
    # userLeagues = result[0][0]
    # newuserLeagues = tuple(userLeagues.split(','))


    # cur.execute("SELECT * FROM leagues WHERE leagueID IN %s;", (newuserLeagues,))
    
    # result=cur.fetchall()
# DELETE ------------------------------------------

    leaguesList = []

    for league in result:
        leaguesList.append({"leagueID": league[0], "leagueName":league[1]})

    return jsonify(leaguesList=leaguesList)  

@app.route('/leaveLeague', methods = ['POST'])
def leaveLeague():

    data = request.get_json()
    
    load_dotenv()

    conn = pymysql.connect(
            host= HOST, 
            port = int(PORT),
            user = USER, 
            password = PASSWORD,
            db = DB,
            )

    cur=conn.cursor()

# DELETE ----------------------------------------------
    # cur.execute("SELECT leagueID FROM users WHERE token = %s", (data["token"]))
    # userLeagues = cur.fetchall()[0][0]

    # # removes team from list of user teams
    # userLeagues = userLeagues.split(",")
    # userLeagues.remove(str(data["leagueID"]))
    # newLeaguesList = ""
    # for i in userLeagues:
    #     newLeaguesList += i+","

    # cur.execute("UPDATE users SET leagueID = %s WHERE token = %s", (newLeaguesList[:-1], data["token"]))
    # conn.commit()
# DELETE ----------------------------------------------

    cur.execute("DELETE FROM league_teams WHERE leagueID = %s", (data["leagueID"]))
    conn.commit()

    return "done"

@app.route('/joinLeague', methods = ['POST'])
def joinLeague():

    data = request.get_json()
    
    load_dotenv() 

    conn = pymysql.connect(
            host= HOST, 
            port = PORT,
            user = USER, 
            password = PASSWORD,
            db = DB,
            )

    cur=conn.cursor()
    cur.execute("SELECT * FROM leagues WHERE leaguePass = %s", (data["leaguePass"]))
    league = cur.fetchall()

    if (league!=()):

        leagueID = league[0][0]

        cur.execute("SELECT userID FROM users WHERE token = %s", (data["token"]))
        userID = cur.fetchall()[0][0]
        cur.execute("INSERT INTO league_teams (userID, leagueID, teamID) VALUES (%s, %s, null)", (userID, leagueID))
        conn.commit()

        # #gets user's current list of leagues
        # cur.execute("SELECT leagueID FROM users WHERE token = %s", (data["token"]))
        # currentLeagues = cur.fetchall()[0][0]
        # newLeagueList = str(currentLeagues)+ "," + str(leagueID)


        # if (currentLeagues)!=None:
        #     cur.execute("UPDATE users SET leagueID = %s WHERE token = %s", (newLeagueList, data["token"]))
        #     conn.commit()
        # elif (currentLeagues)==None:
        #     cur.execute("UPDATE users SET leagueID = %s WHERE token = %s", (leagueID, data["token"]))
        #     conn.commit()

    elif (league==()):
        
        return "There is no league"


    return "done"

@app.route('/getLeagueInfo', methods = ['POST'])
def getLeagueInfo():

    data = request.get_json()
    
    load_dotenv() 

    conn = pymysql.connect(
            host= HOST, 
            port = PORT,
            user = USER, 
            password = PASSWORD,
            db = DB,
            )

    cur=conn.cursor()
    cur.execute("SELECT leagueName FROM leagues WHERE leagueID = %s", (data["leagueID"]))
    leagueName = cur.fetchall()[0][0]


    cur.execute("SELECT userID FROM league_teams WHERE leagueID = %s", (data["leagueID"]))
    leagueMembers = [i[0] for i in cur.fetchall()]

    cur.execute("SELECT fname FROM users WHERE userID IN %s", (leagueMembers,))
    leagueMembersNames = [i[0] for i in cur.fetchall()]



    # print(leagueMembers)
    # print(leagueMembersNames)

    memberTeamsList = {}

    for member in leagueMembers:
        cur.execute("SELECT teamID FROM league_teams WHERE userID = %s AND leagueID = %s",(member, data["leagueID"]))
        memberTeam = cur.fetchall()[0][0]
        
        if memberTeam != None:
            cur.execute("SELECT slot1, slot2, slot3, slot4, slot5, slot6 FROM teams WHERE teamID = %s",(memberTeam))
            teamList = cur.fetchall()[0]
            # print(teamList)

            cur.execute("SELECT driver, driverImg FROM drivers WHERE id IN %s",(teamList,))
            # print([{i[0]:i[1]} for i in cur.fetchall()])
            memberTeamsList[leagueMembersNames[leagueMembers.index(member)]] = [{i[0]:i[1]} for i in cur.fetchall()]

            cur.execute("SELECT constructor, constructorImg FROM constructors WHERE id = %s", (teamList[5]))
            constructor = cur.fetchall()
            
            
            if constructor!=():
                memberTeamsList[leagueMembersNames[leagueMembers.index(member)]].append({constructor[0][0]:constructor[0][1]})


    # print(memberTeamsList)

    return jsonify(memberTeamsList=memberTeamsList, leagueName=leagueName)  

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(ssl_context='adhoc')


