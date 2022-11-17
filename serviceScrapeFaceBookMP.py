'''
Author: Daniel Abrahams

Synopsis:

Use This Emulator to Scrape
Facebook Marketplace Cars
And Send to DB using API
'''

#import outside libs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import requests

#import standard libs
import time
import json

#create dictionary to store car info from Facebook Marketplace
carInfoMaster = {}
carInfo = {}

#connect to driver
driver = webdriver.Chrome(executable_path=r'/Users/princeabrahams/Desktop/Demo/JARFILES/chromedriver')

#set login url and get
loginurl =  "https://www.facebook.com/"
driver.get(loginurl)

#set login credentionals and login
phone = '2014521981'
password = 'password'
inputPhone = driver.find_element(By.ID, "email")
inputPhone.send_keys(phone)
inputPassword = driver.find_element(By.ID, "pass")
inputPassword.send_keys(password)
driver.execute_script("document.getElementsByClassName('_42ft _4jy0 _6lth _4jy6 _4jy1 selected _51sy')[0].click()")

#get marketplace cars BMW in tampa
url = "https://www.facebook.com/marketplace/tampa/search?minPrice=1000&maxPrice=85000&daysSinceListed=7&sortBy=price_descend&query=bmw&exact=false"
driver.get(url)
time.sleep(10)
#get url again just in case
driver.get(url)

#create scroll parmaters
SCROLL_PAUSE_TIME = 0.5
timeout = time.time() + 45*1   # 2 minutes from now

#scroll until time runs out - shoudl scroll whole page so items are vissible
while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    # if new_height == last_height:
    #     break
    # last_height = new_height
    test = 0
    if time.time() > timeout:
        break

#get initial window
windows_before = driver.window_handles[0]

#try n times
for n in range(1):

    #get all cars
    cars = driver.find_elements(By.XPATH, '//img')

    #for each car
    for x in range(0, len(cars)):
        try:
            #if car is displayed
            if cars[x].is_displayed():

                #click & switch to new window
                ActionChains(driver).move_to_element(cars[x]).key_down(Keys.COMMAND).click(cars[x]).key_up(Keys.COMMAND).perform()
                time.sleep(5)
                window_after = driver.window_handles[1]
                driver.switch_to.window(window_after)

                #get facebook data
                fbMarketPlaceData = driver.find_element(By.XPATH, "/html/body").text
                fbMarketPlaceData = fbMarketPlaceData.split('\n')
                carData = fbMarketPlaceData[32:56]

                #change car data to dict
                carDataDict = dict()
                carDataDict["CarInfo"] = carData
                carInfo.update(carDataDict)

                #close driver and send data to carInfoMaster
                driver.close()
                driver.switch_to.window(windows_before)
                carInfoMaster.update(carInfo)
                print(carInfoMaster)

                # login to api and send carInfo
                response = requests.post(
                    'http://127.0.0.1:5000/login',
                    auth=('DanielAbrahams', 'password'))
                token = response.json().get('token')
                createSportscarResult = requests.post('http://127.0.0.1:5000/facebooksportscar',
                                                      headers={'Content-Type': 'application/json',
                                                               'X_ACCESS_TOKENS': token}, data=json.dumps(carInfo))
                #clear dictionary for next iteration
                carInfo.clear()

        except Exception as e:
            driver.switch_to.window(windows_before)

            continue



