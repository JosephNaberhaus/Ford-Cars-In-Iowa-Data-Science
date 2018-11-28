from lxml import etree
import lxml.html
import requests
from io import BytesIO, StringIO
import csv
import pycurl
from random import randint
import time

# Dict of the name of the data piece to the XPath of the detail
carDetailDict = {
    "price":"//span[contains(@class, 'vehicle-info__price-display')]",
    "miles":"//div[contains(@class, 'vdp-cap-price__mileage--mobile vehicle-info__mileage')]",
    "fuel_type":"//li[strong[text()='Fuel Type:']]/span",
    "exterior_color":"//li[strong[text()='Exterior Color:']]/span",
    "interior_color":"//li[strong[text()='Interior Color:']]/span",
    "drivetrain":"//li[strong[text()='Drivetrain:']]/span",
    "transmission":"//li[strong[text()='Transmission:']]/span",
    "engine":"//li[strong[text()='Engine:']]/span",
    "VIN":"//li[strong[text()='VIN:']]/span",
    "name":'//*[@id="vdpOverview"]/h1',
    "sellerAddress":"//p[contains(@class, 'vdp-dealer-location__address')]"
}

carAttributeIds = list(carDetailDict.keys()) + ["id", "modelName"]

# Zip codes to scrape
zipCodes = [50009, 50010, 50021, 52722, 50036, 52601, 51401, 50613, 52732, 52101, 50322, 
            50325, 50265, 52001, 50501, 50125, 52240, 52241, 50131, 52632, 51031, 52302, 
            50158, 50401, 52761, 50208, 52317, 52577, 52501, 50219, 51301, 50588, 50701, 50263, 51501]

# Dict of each Ford model to the Cars.com internal id number  
modelIdDict = {
    "C-Max Energi":50243,
    "C-Max Hybrid":49085,
    "Crown Victoria":20906,
    "E150":21050,
    "E250":26506,
    "E350":26502,
    "E350 Super Duty":26507,
    "EcoSport":36284899,
    "Edge":21039,
    "Escape":21088,
    "Excursion":21102,
    "Expedition":21104,
    "Expedition EL":21085,
    "Expedition Max":36324071,
    "Explorer":21105,
    "Explorer Sport Trac":21107,
    "F-150":21095,
    "F-250":21115,
    "F-350":21097,
    "Fiesta":21146,
    "Five Hundred":21156,
    "Flex":21136,
    "Focus":21138,
    "Focus ST":48704,
    "Freestar":21169,
    "Freestyle":21144,
    "Fusion":21175,
    "Fusion Energi":53027,
    "Fusion Hybrid":27661,
    "Mustang":21712,
    "Probe":21752,
    "Ranger":21874,
    "Sedan Police Interceptor":57387,
    "Shelby GT350":30021281,
    "Taurus":22164,
    "Thunderbird":22263,
    "Transit Connect":28203,
    "Transit-150":56747,
    "Transit-250":56748,
    "Transit-350":56749,
    "Model Unknown":29629
}

# The Cars.com internal id for Ford model cars
makeId = 20015

'''
Loads details about car found at the given URL

Parameters
----------
url : str 
    Full URL to the Cars.com car overview page

Returns
-------
dict 
    Dictionary of each Car detail as key and the cars value for the detail or a blank string
        if no value was provided for that value    
'''
def scrapeCarDataFromURL(url):
    # Load the page and use LXML etree to parse the html
    buffer = BytesIO()

    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()

    status = c.getinfo(pycurl.RESPONSE_CODE)
    if status != 200: return None

    html = lxml.html.fromstring(buffer.getvalue().decode('UTF-8'))

    # Iterate through every detail to xpath mapping and find the value for this car for each
    carData = {};
    for detail, xpath in carDetailDict.items():
        xpathResp =  html.xpath(xpath)
        carData[detail] = xpathResp[0].text_content() if len(xpathResp) > 0 else ""
    
    return carData

'''
Loads details about car from internal Cars.com ID

Parameters
----------
id : str 
    Internal Cars.com ID number of the car to retrieve details for

Returns
-------
dict 
    Dictionary of each Car detail as key and the cars value for the detail or a blank string
        if no value was provided for that value    
'''
def scrapeCarDataFromId(id):
    return scrapeCarDataFromURL("https://www.cars.com/vehicledetail/detail/" + str(id) + "/overview/")

'''
Emulates performing a search on Cars.com and retrieves the internal Cars.com ID for every result

Parameters
----------
makeId : str 
    Cars.com ID for the make of car to search for
modelId : str
    Cars.com ID for the model of car to search for
zipCode : str
    The ZipCode to center the search around
distance : str
    Max distance from ZipCode for the search results
page : str
    The page number of the search to provide the results from
perPage : str
    The number of items see on each page
    MAX = 20

Returns
-------
list[str] 
    List of each ID on this search page    
'''
def scrapeCarIdsFromSearch(makeId, modelId, zipCode, distance, page, perPage = 20):
    searchPostfix = "?mkId=" + str(makeId) +"&mdId=" + str(modelId) + "&zc=" + str(zipCode) + "&rd=" + str(distance) + "&page=" + str(page) + "&perPage=" + str(perPage)
    
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'https://www.cars.com/for-sale/searchresults.action/?' + searchPostfix)
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()

    tree = etree.parse(StringIO(buffer.getvalue().decode('UTF-8')), etree.HTMLParser())

    entries = tree.xpath("//*[contains(@class, 'shop-srp-listings__listing')]")
    return [entry.get("data-goto-vdp") for entry in entries]

'''
Emulates performing a search and looking at each avaiilible page

Parameters
----------
makeId : str 
    Cars.com ID for the make of car to search for
modelId : str
    Cars.com ID for the model of car to search for
zipCode : str
    The ZipCode to center the search around
distance : str
    Max distance from ZipCode for the search results

Yields
-------
list[str] 
    List of Car.com internal ids for each page    
'''
def scrapeAllIdsFromSearch(makeId, modelId, zipCode, distance):

    prevResult = None
    for i in range(1,51):
        result = scrapeCarIdsFromSearch(makeId, modelId, zipCode, distance, i)
        if prevResult == result: break
        print("makeId: " + str(makeId) + " modelId: " + str(modelId) + " zipCode: " + str(zipCode) + " disance: "+ str(distance) + " page: " + str(i))
        yield result
        prevResult = result
        time.sleep(randint(1,3))

'''
Scrapes the search results of Cars.com for all of the zipcodes and models 
specified and writes the ids to a CSV file
'''
def scrapeIds(path):
    with open(path, 'w', newline='') as file:
        carIds = csv.writer(file)
        
        carIds.writerow(["id", "makeId", "modelName", "zipCode"])
        # Go through each zipcode and model id combination and ad each id as a row to the csv
        for zip in zipCodes:
            for modelName, modelId in modelIdDict.items():
                for ids in scrapeAllIdsFromSearch(makeId, modelId, zip, 100):
                    for id in ids:
                        carIds.writerow([id, makeId, modelName, zip])

def scrapeCarData(readPath, writePath):
    with open(readPath) as readFile, open(writePath, 'w', newline='', buffering=1) as writeFile:
        readCSV = csv.DictReader(readFile)
        writeCSV = csv.DictWriter(writeFile, carAttributeIds)
        writeCSV.writeheader()
        for car in readCSV:
            print(car)
            carData = scrapeCarDataFromId(car["id"])
            if carData != None:            
                carData["id"] = car["id"]
                carData["modelName"] = car["modelName"]
                #carData['model'] = car["modelName"]
                writeCSV.writerow(carData)
            # Add reasonable delay between requests
            time.sleep(randint(1,3))

'''
Called when the Python file is executed and controls
what the app should do. This is not setup as a command
line argument as it is unnecesary for the scop of the project
'''
def initiate():
    scrapeCarData("carIdsClean.csv", "carData.csv")
    
initiate()
