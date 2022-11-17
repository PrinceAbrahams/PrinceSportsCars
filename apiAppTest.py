'''

Author: Daniel Abrahams
Synopsis: I am builing a unit test
for the apiApp using request

'''

#import libs
import requests
import json

#login
response = requests.post(
    'http://127.0.0.1:5000/login',
    auth=('DanielAbrahams', 'password'))
token = response.json().get('token')

#create sporst car
payload = {"make": "Aston Martin", "model" : "Vantage", "year" : 2016,
                   "miles" : 17000, "vin" : "ZHWUR1ZF0GLA05138"}
createSportscarResult = requests.post('http://127.0.0.1:5000/sportscar',
      headers={'Content-Type':'application/json',
               'X_ACCESS_TOKENS': token}, data=json.dumps(payload))

#getsportscars sporst car
getSportscarResult = requests.get('http://127.0.0.1:5000/sportscars',
      headers={'Content-Type':'application/json',
               'X_ACCESS_TOKENS': token})
sportsCars = getSportscarResult.json()


