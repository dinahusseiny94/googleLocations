from selenium import webdriver
from time import sleep
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)

# Inputs
sourceLocation = []
targetLocation = []
shortestRouteTitle = []
shortestRouteDistance = []
parallel_templates = []


def find(chrome, destination, cf):
    sleep(2)
    source_location = cf.source_location
    chrome.get("https://www.google.com/maps/dir/" + source_location)
    minDistance = 10000
    minIndex = 0
    routeTitleCol = []
    sleep(5)
    targetLocationInput = chrome.find_element_by_xpath(
        '/html/body/jsl/div[3]/div[9]/div[3]/div[1]/div[2]/div/div[3]/div[1]/div[2]/div[2]/div/div/input')
    targetLocationInput.send_keys(destination)
    sleep(5)
    searchButton = chrome.find_element_by_xpath(
        '/html/body/jsl/div[3]/div[9]/div[3]/div[1]/div[2]/div/div[3]/div[1]/div[2]/div[2]/button[1]')
    searchButton.click()
    sleep(5)
    routes = chrome.find_elements_by_class_name('section-directions-trip-title')
    routes_distances = chrome.find_elements_by_class_name('section-directions-trip-distance')
    while len(routes) == 0:
        routes = chrome.find_elements_by_class_name('section-directions-trip-title')
        routes_distances = chrome.find_elements_by_class_name('section-directions-trip-distance')
    for routeTitle in routes:
        routeTitleText = routeTitle.text
        if routeTitleText != '':
            routeTitleCol.append(routeTitleText)
    count = 0
    for routeDistance in routes_distances:
        routeDistanceText = routeDistance.text
        routeDistanceText = routeDistanceText.replace('m', '')
        routeDistanceText = routeDistanceText.replace('م', '')
        if 'k' not in routeDistanceText and 'ك' not in routeDistanceText :
            routeDistanceText = str(float(routeDistanceText.strip())/1000)
        routeDistanceText = routeDistanceText.replace('k', '')
        routeDistanceInKM = routeDistanceText.replace('ك', '')
        if routeDistanceInKM == '':
            routeDistanceInKM = '10000'
        minRouteDistance = float(routeDistanceInKM.strip())
        if minRouteDistance < minDistance:
            minDistance = minRouteDistance
            minIndex = count
        count = count + 1
    sourceLocation.append(source_location)
    targetLocation.append(destination)
    shortestRouteDistance.append(minDistance)
    shortestRouteTitle.append(routeTitleCol[minIndex])


def parse_file(cf):
    chrome_path = os.path.join(BASE_DIR, "chromedriver")
    driver = webdriver.Chrome(chrome_path)

    target_locations = pd.read_csv(cf.destination_location)
    for target_location in target_locations['Target Locations']:
        find(driver, target_location, cf)

    df = pd.DataFrame(
        {'Source Location': sourceLocation,
         'Target Location': targetLocation,
         'Route Name': shortestRouteTitle,
         'Route Distance': shortestRouteDistance})

    export_file_path = cf.output_folder_path + '/' + cf.output_folder_name + '.csv'
    df.to_csv(export_file_path, index=False, header=True, encoding='utf-8-sig')
    driver.quit()
