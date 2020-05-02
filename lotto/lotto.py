import eel
import sqlite3
import secrets
from datetime import date
import os

eel.init('web')

def database():
    global conn, cursor
    try:
        conn = sqlite3.connect("lottery.db")
    except sqlite3.Error as e:
        print("Error connecting to the database!\n" + str(e))
        return
    cursor = conn.cursor()

# 1-10 inclusive, no repetition, ascending order
def generatePicks():
    pickList = []
    while len(pickList) < 3:
        num = secrets.choice(range(1, 11))
        if num not in pickList:
            pickList.append(num)
        else:
            continue
    pickList.sort()
    return pickList

def read(query):
    database()
    cursor.execute(query)
    fetch = cursor.fetchall()
    cursor.close()
    conn.close()
    return fetch

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
        if pickStr not in existingPickList:
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
    userPicks.sort()
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
def runLottery():
    #winningNumbers = generatePicks()
    winningNumbers = [8, 9, 10]
    winningNumbersStr = str(winningNumbers[0]) + ", " + str(winningNumbers[1]) + ", " + str(winningNumbers[2])
    database()
    fetch = read("SELECT `Name` FROM `Lottery` WHERE `Numbers` = '" + winningNumbersStr + "'")
    if fetch is not None:
        for row in fetch:
            winnersName = row[0]
        return winnersName, winningNumbersStr
    else:
        return "There was no winner!", winningNumbersStr



eel.start('ticket.html', size=(800,800))

