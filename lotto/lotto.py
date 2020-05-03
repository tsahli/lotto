import eel
import sqlite3
import secrets
from datetime import date
import os

eel.init('web')

def database():
    global conn, cursor
    try:
        appDataRoaming = os.getenv('APPDATA')
        conn = sqlite3.connect(appDataRoaming + "\\lottery.db")
    except sqlite3.Error as e:
        print("Error connecting to the database!\n" + str(e))
        return
    cursor = conn.cursor()

# 0-9 inclusive, no repetition, descending order
def generatePicks():
    pickList = []
    while len(pickList) < 3:
        num = secrets.choice(range(0, 10))
        if num not in pickList:
            pickList.append(num)
        else:
            continue
    pickList.sort(reverse=True)
    return pickList

def read(query):
    database()
    cursor.execute(query)
    fetch = cursor.fetchall()
    cursor.close()
    conn.close()
    return fetch

@eel.expose
def addUser(person):
    personT = person.title()
    userNames = getUserNames()
    if personT not in userNames:
        database()
        cursor.execute("INSERT INTO `Users` (`Name`) VALUES (?)", (personT,))
        conn.commit()

@eel.expose
def getUserNames():
    fetch = read("SELECT * FROM `Users` ORDER BY `Name`")
    nameList = []
    for row in fetch:
        name = row[1]
        nameList.append(name)
    return nameList

@eel.expose
def makeTicket(obj):
    name = obj['name']
    numTickets = obj['numberOfTickets']
    fetch = read("SELECT `Numbers` FROM `Lottery`")
    existingPickList = []
    for row in fetch:
        existingPickList.append(row[0])
    i = 0
    today = date.today()
    userPicks = []

    while i < int(numTickets):
        picks = generatePicks()
        pickStr = str(picks[0]) + ", " + str(picks[1]) + ", " + str(picks[2])
        if pickStr not in existingPickList and pickStr not in userPicks:
            userPicks.append(pickStr)
            database()
            cursor.execute("INSERT INTO `Lottery` (`Name`, `Numbers`, `Date`) VALUES (?,?,?)", (name, pickStr, str(today)))
            conn.commit()
            i += 1
        else:
            continue
    cursor.close()
    conn.close()

    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
    userPicks.sort(reverse=True)
    filename = desktop + "\\" + name + " Picks on " + str(today) + ".txt"
    with open(filename, "a") as txtFile:
        txtFile.write(name + "\t" + str(today) + "\n\n")
        for pick in userPicks:
            txtFile.write(pick + "\n")
    os.startfile(filename)

@eel.expose
def getSoldTickets():
    fetch = read("SELECT * FROM `Lottery` ORDER BY `Date`")
    return fetch

@eel.expose
def resetLottery():
    database()
    cursor.execute("DELETE FROM `Lottery`")
    conn.commit()
    cursor.close()
    conn.close()
    return "Lottery has been reset."

@eel.expose
def runLottery():
    winningNumbers = generatePicks()
    winningNumbersStr = str(winningNumbers[0]) + ", " + str(winningNumbers[1]) + ", " + str(winningNumbers[2])
    database()
    fetch = read("SELECT `Name`, `Date` FROM `Lottery` WHERE `Numbers` = '" + winningNumbersStr + "'")
    winnersName = ""
    ticketDate = ""
    if len(fetch) != 0:
        for row in fetch:
            winnersName = row[0]
            ticketDate = row[1]
        return winnersName, winningNumbersStr, ticketDate
    else:
        return "There was no winner!", winningNumbersStr, "N/A"



eel.start('ticket.html', size=(800,800))


