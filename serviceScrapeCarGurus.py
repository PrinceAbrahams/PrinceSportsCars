'''
Author: Daniel Abrahams

Synopsis:

Use This Emulator to Scrape
CarGurus Cars
And Send to DB using API

'''

#import standard libraries
import pdb
import time
import json

#import outside libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import requests


def serviceCarGurus():

    driver = webdriver.Chrome(executable_path=r'/Users/princeabrahams/Desktop/Demo/JARFILES/chromedriver')

    carInfoMaster = {}
    carInfo = {}

    #get LAMBO URL
    driver.get('https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?zip=33615&distance=50000&entitySelectingHelper.selectedEntity=m34#resultsPage=1')

    time.sleep(5)

    #iterate through each page using page variable - append 1 to page after page scrape is complete
    page = 1
    time.sleep(5)
    windows_before = driver.window_handles[0]

    #try n times
    for n in range (1):

        #get all cars on page
        cars = driver.find_elements(By.CLASS_NAME, "wFZMAc")
        for x in range(0, len(cars)):
            try:
                time.sleep(5)

                #if car is displaye4d
                if cars[x].is_displayed():

                    #click car and swtich to window
                    time.sleep(5)
                    ActionChains(driver).move_to_element(cars[x]).key_down(Keys.COMMAND).click(cars[x]).key_up(Keys.COMMAND).perform()
                    window_after = driver.window_handles[1]
                    driver.switch_to.window(window_after)

                    '''
                    START OF GET ALL CAR FEATURES
                    '''
                    carName = driver.find_element(By.CLASS_NAME, "IpF2YF")
                    carInfo.update({'CarMakeModelPriceYear': carName.text})

                    dealername = driver.find_element(By.CLASS_NAME, "iLt7Kj")
                    carInfo.update({'DealerName': dealername.text})

                    dealernumber = driver.find_element(By.CLASS_NAME, "RVr5Hy")
                    carInfo.update({'DealerNumber': dealernumber.text})

                    cardata = driver.find_elements(By.CLASS_NAME, "RB5wfO")
                    carDatalist = []
                    for i in cardata:
                        carDatalist.append(i.text)

                    carDataDict = dict()
                    carDataDict["CarInfo"] = carDatalist
                    carInfo.update(carDataDict)

                    carFax = driver.find_elements(By.XPATH, "//div[@class='sc-crXcEl ikVVZC']//h4")
                    carFaxlist = []
                    for i in carFax:
                        carFaxlist.append(i.text)

                    carFaxDict = dict()
                    carFaxDict["CarFax"] = carFaxlist
                    carInfo.update(carFaxDict)

                    deal = driver.find_element(By.CLASS_NAME, "FRs1wh")
                    dealdecision = deal.text
                    dealdecision = dealdecision.split(" at ")
                    dealdecisionList = []
                    for i in dealdecision:
                        #print(i)
                        dealdecisionList.append(i)

                    dealDecisionDict = dict()
                    dealDecisionDict["DealDecision"] = dealdecisionList
                    carInfo.update(dealDecisionDict)

                    daysOnMarket = driver.find_elements(By.CLASS_NAME, "PaczrG")
                    daysonMarketList = []
                    for i in daysOnMarket:
                        #print(i.text)
                        daysonMarketList.append(i.text)

                    daysonMarketDict = dict()
                    daysonMarketDict["DaysOnMarket"] = daysonMarketList
                    carInfo.update(daysonMarketDict)

                    '''
                    END OF GET ALL CAR FEATURES
                    '''

                    #CLOSE DRIVER AND SWITCH TO PRIOR WINDOW
                    driver.close()
                    driver.switch_to.window(windows_before)
                    carInfoMaster.update(carInfo)


                    # login AND SEND data to DB with API
                    response = requests.post(
                        'http://127.0.0.1:5000/login',
                        auth=('DanielAbrahams', 'password'))
                    token = response.json().get('token')
                    createSportscarResult = requests.post('http://127.0.0.1:5000/cargurussportscar',
                                                          headers={'Content-Type': 'application/json',
                                                                   'X_ACCESS_TOKENS': token}, data=json.dumps(carInfo))

                    #clear dict for nex tinteration loop
                    carInfo.clear()

            except Exception as e:
                driver.switch_to.window(window_after)
                driver.close()
                driver.switch_to.window(windows_before)

                continue


        #add page + 1 and get URL
        page += 1
        URL = 'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?zip=33615&distance=50000&entitySelectingHelper.selectedEntity=m34#resultsPage=' + str(page)
        driver.get(URL)
        #driver.get(URL)

        # check if a popup comes if does click out of it
        time.sleep(30)
        try:
            driver.execute_script("document.getElementsByClassName('_4KkQxL')[0].click()")
        except Exception as e:
            #exceptions not occuring so passing
            pass

serviceCarGurus()
