__author__ = 'Keifer'

from card import Card
import requests
import csv
from os import listdir
from os.path import isfile, join
from time import gmtime, strftime


# global dictionary object that stores current inventory
# is read from and saved to a CSV file
inventory = {}


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

    # return format == dictionary of lists of dictionaries of lists of dictionaries:
    # print(returnData["results"])
    # print(returnData["results"][0])
    # print(returnData["results"][0]["productConditions"])
    # print(returnData["results"][0]["productConditions"][0])
    # print(returnData["results"][0]["productConditions"][0]["productConditionId"])

    # for each listed card item, check url for a matching set type
    count = 0
    for cardVersion in returnData["results"]:
        if card.version in returnData["results"][count]["url"]:

            # grab condition value, error if not found
            condition = -1
            if (card.condition == "nm"): condition = 0
            elif (card.condition == "nm f"): condition = 1
            elif (card.condition == "damaged"): condition = 2
            elif (card.condition == "mp"): condition = 3
            elif (card.condition == "hp"): condition = 4
            elif (card.condition == "lp"): condition = 5
            elif (card.condition == "damaged f"): condition = 6
            elif (card.condition == "mp f"): condition = 7
            elif (card.condition == "hp f"): condition = 8
            elif (card.condition == "lp f"): condition = 9

            productConditionId = returnData["results"][count]["productConditions"][condition]["productConditionId"]

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

    # aggregate total card value
    for key, list in inventory.iteritems():
        for card in list:
            totalBuyPrice += int(card.buyPrice) * int(card.quantity)
            totalValue += int(fetchCardPrice(card, token)) * int(card.quantity)

    # write data to file (named by today's date)
    filename = "output/" + strftime("%Y-%m-%d", gmtime()) + ".txt"
    f = open(filename, 'w')
    f.write("Total purchase cost: " + str(totalBuyPrice) + '\n')
    f.write("Total value: " + str(totalValue) + '\n')

    return


def save():
    # dump inventory dictionary to file
    w = csv.writer(open("output/inventory.csv", "w"))
    for key, list in inventory.iteritems():
        for card in list:
            w.writerow([card.name, card.version, card.condition, card.buyPrice, card.quantity])


def load():
    # read all files in input/
    # create inventory dictionary based on these input files
    try:
        inputFiles = [f for f in listdir("input/") if isfile(join("input/", f))]

        for file in inputFiles:
            #reader = csv.reader(open('inventory.csv', 'r'))
            reader = csv.reader(open("input/" + file, 'r'))
            cardList = []
            for row in reader:
                card = Card(row[0], row[1], row[2], row[3], row[4])
                cardList.append(card)
            inventory[file] = cardList
    except IOError:
        print("Import file not found.")


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
printTotals(token)
save()

print("Complete.")
###### END! #####
