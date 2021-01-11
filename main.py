from selenium import webdriver
import os.path
from time import *
from datetime import *
from bs4 import BeautifulSoup
import os



def writeToCsv(outList, csvPath):
    if os.path.isfile(csvPath):
        outList.remove(outList[0])

    f = open(csvPath, "a")
    for l in outList:
        f.write(",".join(l) + '\n')
    f.close()

def getValuesFromLocalWunderground(htmlCode):
    resp = []

    # Beautifulsoup
    soup = BeautifulSoup(htmlCode, "html.parser")

    # find table
    soupTable = soup.find("table", class_="mat-table cdk-table mat-sort ng-star-inserted")
    if soupTable is None:
        return []

    # find name and location
    listPos = soup.find_all("strong")
    if listPos is None:
        return []

    lat = listPos[0].get_text().replace(',', '')
    lon = listPos[1].get_text().replace(',', '')
    temp_atual = soup.find("lib-display-unit", attrs={"type": "temperature"}).get_text()
    station_name = soup.find("a", class_="station-name").get_text()
    station_name = station_name.replace(temp_atual + " ", "")

    # find date
    listDate = soup.find("link", attrs={"rel": "canonical"})
    dt_list = listDate.attrs["href"].split("/")[-1].split("-")
    try:
        dt = datetime(int(dt_list[0]), int(dt_list[1]), int(dt_list[2])).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return []

    # find header
    listHeader = soupTable.find("thead").find_all("button")

    listBody = soupTable.find("tbody").find_all("span")

    header = []
    header.append("Date")
    header.append("Station_Name")
    header.append("lat")
    header.append("lon")

    for l in listHeader:
        header.append(l.get_text())

    resp.append(header)
    lheader = len(listHeader)

    line = []
    line.append(dt)
    line.append(station_name)
    line.append(lat)
    line.append(lon)

    i = 0
    skip = False

    for l in listBody:
        cel = l.renderContents().decode("utf-8")
        if not (cel[0:4] == "<!--" or skip):
            if cel[0:5] == "<span":
                skip = True
            else:
                line.append(cel.replace(',', ''))
                i += 1
                if i > lheader - 1:
                    resp.append(line)
                    line = []
                    line.append(dt)
                    line.append(station_name)
                    line.append(lat)
                    line.append(lon)
                    i = 0
        else:
            skip = False

    return resp


startDate = datetime.strptime("01/01/2015", "%d/%m/%Y")
endDate =  datetime.strptime("31/01/2020", "%d/%m/%Y")
partial_url_address = "ny/new-york-city/KLGA"
finalCsv = "wunderground.csv"
sleepTime = 3

#partial_url_address represents the below partial URL - between []
#https://www.wunderground.com/history/daily/us/[ny/new-york-city/KLGA]/date/2014-9-13


try:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("prefs",  {"profile.managed_default_content_settings.images": 2})
    driver = webdriver.Chrome("chromedriver.exe", chrome_options=chrome_options)

    captureDate = startDate
    capture_url = ""
    while captureDate <= endDate:
        capture_url = "https://www.wunderground.com/history/daily/us/" + partial_url_address + "/date/{}-{}-{}".format(captureDate.year, captureDate.month, captureDate.day)
        driver.get(capture_url)
        sleep(sleepTime)
        respList = getValuesFromLocalWunderground(driver.page_source)

        if len(respList) > 0:
            writeToCsv(respList, finalCsv)

        captureDate += timedelta(days=1)
finally:
    driver.close()



