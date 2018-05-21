__author__ = 'Keifer'

from card import Card
import requests
import csv


# global dictionary object that stores current inventory
# is read from and saved to a CSV file
##TODO quantities?
##TODO other dict groups
inventory = {}
inventory["default"] = []


def addCard():
    try:
        # enter card name, version, condition, buy price
        cardName = raw_input("Enter card name: ")
        cardVersion = raw_input("Enter card version: ")
        cardCondition = raw_input("Enter card condition: ")
        buyPrice = input("Enter card purchase price: ")
        quantity = input("Enter number of cards purchased: ")

    except NameError:
        print "Input error."
        return

    # cardName must be deliminated by "+" and all lowercase
    cardName = cardName.replace(' ', '+')
    cardName = cardName.lower()

    # create and store object
    card = Card(cardName, cardVersion, cardCondition, buyPrice, quantity)
    inventory["default"].append(card)

    return


# makes a network request to TCG player API
def fetchCardPrice(card, token):
    # format rest call to fetch productConditionId
    headers = {
        "Authorization": "bearer " + token }#"hKLEpcHIvOKSFKNNk31xXAsk9qEH7LpLc6jbdeVfN4yPbYSGBUBp92JVdiEHI8MaoCvLvWHvjMU_RP9zxVDgDGDOzen-jRUt7jLhekZzyd6TGA7p7czsGWkOnzmfUUB9GuWJ-gzwjxWvSleUxgQ4onoH2CXHJHtakajQZp05iq61SmcUBCQHIiZGh0Qtn1cNc02o4AVyoiWWRJXdzRlZZWr_1ac2tD23RJrtj1oI6kzA5Qbasap7TVKs8CPaFMXCZqLlzGgPNirPEgenqU9aCDoI_B-2FdMGWsUMBif8o8EiJRaH6YUfi_-wmI0AdmUfHw8qGQ"}
    url = "http://api.tcgplayer.com/catalog/products?categoryId=1&productTypes=Cards&productName=" + card.name

    response = requests.get(url, headers=headers)
    returnData = response.json()

    # return format == dictionary of lists of dictionaries of lists of dictionaries

    ##TODO index errs?
    ##TODO condition

    # print(returnData["results"])
    # print(returnData["results"][0])
    # print(returnData["results"][0]["productConditions"])
    # print(returnData["results"][0]["productConditions"][0])
    # print(returnData["results"][0]["productConditions"][0]["productConditionId"])

    # for each listed card item, check url for a matching set type
    count = 0
    for cardVersion in returnData["results"]:
        if card.version in returnData["results"][count]["url"]:
            productConditionId = returnData["results"][count]["productConditions"][0]["productConditionId"]

            # format rest call to fetch market price
            url = "http://api.tcgplayer.com/pricing/marketprices/" + str(productConditionId)
            response = requests.get(url, headers=headers)
            returnData = response.json()

            return returnData["results"][0]["price"]
        count += 1

    print("No match found for card: " + card.name + ".")
    return 0


# calls fetchCardPrice which makes a network request
def printTotals(token):
    totalBuyPrice = 0
    totalValue = 0

    for card in inventory["default"]:
        totalBuyPrice += int(card.buyPrice) * int(card.quantity)
        totalValue += int(fetchCardPrice(card, token)) * int(card.quantity)

    print("Total purchase cost: " + str(totalBuyPrice))
    print("Total value: " + str(totalValue))

    return


def save():
    w = csv.writer(open("inventory.csv", "w"))
    for key in inventory["default"]:
        w.writerow([key.name, key.version, key.condition, key.buyPrice, key.quantity])


def load():
    try:
        reader = csv.reader(open('inventory.csv', 'r'))
        cardList = []
        for row in reader:
            card = Card(row[0], row[1], row[2], row[3], row[4])
            cardList.append(card)
        inventory["default"] = cardList
    except IOError:
        print("Import file not found - creating.")
        outfile = open('inventory.csv', 'w')


# loads config from textfile
def boot():
    configFile = open('config.txt')
    configText = configFile.read().splitlines()
    configFile.close()

    # format rest call to grab token
    url = "https://api.tcgplayer.com/token"
    data = "grant_type=client_credentials&client_id=" + str(configText[0]) + "&client_secret=" + str(configText[1])
    headers = {"Content-type": "application/x-www-form-urlencoded"}

    respsonse = requests.post(url=url, data=data, headers=headers)
    returnData = respsonse.content

    # dirty way to grab token
    return returnData[17:343]

##### MAIN #####
token = boot()
load()

while True:
    command = raw_input("Enter a command: ")

    # quit
    if command[0] == 'q':
        break
    # add
    elif command[0] == 'a':
        addCard()
        save()
    # print
    elif command[0] == 'p':
        printTotals(token)
