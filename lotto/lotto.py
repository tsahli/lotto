import eel
import sqlite3
import secrets

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

#x = 0
#while x < 50:
#    picks = generatePicks()
#    print(picks)
#    x += 1

@eel.expose
def say_hello_py(x):
    print('Hello from ' + x)

eel.start('index.html', size=(700,800))

