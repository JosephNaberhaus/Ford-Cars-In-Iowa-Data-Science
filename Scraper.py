from lxml import etree
import requests
from io import BytesIO, StringIO
import csv
import pycurl

carDetailDict = {
    "price":"/html/body/div[1]/div[2]/section[2]/section[1]/div[2]/div[1]/span",
    "miles":"/html/body/div[1]/div[2]/section[2]/section[1]/div[2]/div[2]",
    "fuel_type":"/html/body/div[1]/div[2]/section[2]/section[2]/div[4]/div/ul/li[1]/span",
    "exterior_color":"/html/body/div[1]/div[2]/section[2]/section[2]/div[4]/div/ul/li[2]/span",
    "interior_color":"/html/body/div[1]/div[2]/section[2]/section[2]/div[4]/div/ul/li[3]/span",
    "drivetrain":"/html/body/div[1]/div[2]/section[2]/section[2]/div[4]/div/ul/li[5]/span",
    "transmission":"/html/body/div[1]/div[2]/section[2]/section[2]/div[4]/div/ul/li[6]/span",
    "engine":"/html/body/div[1]/div[2]/section[2]/section[2]/div[4]/div/ul/li[7]/span",
    "VIN":"/html/body/div[1]/div[2]/section[2]/section[2]/div[4]/div/ul/li[8]/span",
    "name":'//*[@id="vdpOverview"]/h1',
    "sellerAddress":'//*[@id="vdpDealer"]/div/div[2]/div/div[1]/p[2]'
}

zipCodes = [50009, 50010, 50021, 52722, 50036, 52601, 51401, 50613, 52732, 52101, 50322, 50325, 50265, 52001, 50501, 50125, 52240, 52241, 50131, 52632, 51031, 52302, 50158, 50401, 52761, 50208, 52317, 52577, 52501, 50219, 51301, 50588, 50701, 50263, 51501]

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

makeId = 20015

def scrapeCarDataFromURL(url):
    page = requests.get(url).content
    tree = etree.parse(BytesIO(page), etree.HTMLParser())

    carData = {};

    for detail, xpath in carDetailDict.items():
        xpathResp =  tree.xpath(xpath)
        carData[detail] = xpathResp[0].text if len(xpathResp) > 0 else ""
    
    return carData

def scrapeCarData(id):
    return scrapeCarDataFromURL("https://www.cars.com/vehicledetail/detail/" + str(id) + "/overview/")

headers = {"User-Agent":  UserAgent().chrome}
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


def scrapeAllIdsFromSearch(makeId, modelId, zipCode, distance):

    prevResult = None
    for i in range(1,51):
        result = scrapeCarIdsFromSearch(makeId, modelId, zipCode, distance, i)
        if prevResult == result: break
        print("makeId: " + str(makeId) + " modelId: " + str(modelId) + " zipCode: " + str(zipCode) + " disance: "+ str(distance) + " page: " + str(i))
        yield result
        prevResult = result

def scrapeIds():
    with open('carIds.csv', 'w', newline='') as file:
        carIds = csv.writer(file)
        carIds.writerow(["id", "makeId", "modelName", "zipCode"])
        for zip in zipCodes:
            for modelName, modelId in modelIdDict.items():
                for ids in scrapeAllIdsFromSearch(makeId, modelId, zip, 100):
                    for id in ids:
                        carIds.writerow([id, makeId, modelName, zip])

scrapeIds()