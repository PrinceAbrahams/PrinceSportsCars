'''
Author: Daniel Abrahams

Synopsis:

Use CarGurusData to Create
Prince Sports Cars Speed To Sale Dash Application

'''

#import outside libs
import dash
import dash_bootstrap_components as dbc
from flask import Flask
import pandas as pd
import dash_table
import dash_html_components as html

#import standard libs
from datetime import timedelta, date
import sqlite3
import ast


'''
Section 1: Scaling Functions for Dependent Variables For PSC Grade Calculation
'''

#creating scaling models to scale dependent car attributes
def Scale_Year(year):

    if year >= 2023:
        return 1
    elif year == 2022:
        return 0.9
    elif year == 2021:
        return 0.8
    elif year == 2020:
        return 0.7
    elif year == 2019:
        return 0.6
    elif year == 2018:
        return 0.5
    elif year == 2017:
        return 0.4
    elif year == 2016:
        return 0.3
    elif year == 2015:
        return 0.2
    elif year <= 2014:
        return 0.1
    else:
        return 0

#creating scaling models to scale dependent car attributes
def Scale_Mileage(Mileage):

    if Mileage < 5000:
        return 1
    elif Mileage >= 5001 and Mileage < 10000:
        return 0.9
    elif Mileage >= 10001 and Mileage < 15000:
        return 0.8
    elif Mileage >= 15001 and Mileage < 20000:
        return 0.7
    elif Mileage >= 20001 and Mileage < 25000:
        return 0.6
    elif Mileage >= 25001 and Mileage < 30000:
        return 0.5
    elif Mileage >= 30001 and Mileage < 35000:
        return 0.4
    elif Mileage >= 35001 and Mileage < 40000:
        return 0.3
    elif Mileage >= 40001 and Mileage < 45000:
        return 0.2
    elif Mileage >= 45001:
        return 0.1
    else:
        return 0

#creating scaling models to scale dependent car attributes
def Scale_Deal(Deal):

    if 'Great' in Deal:
        return 1
    elif 'Good' in Deal:
        return .75
    elif 'Fair' in Deal:
        return .5
    elif 'Overpriced' in Deal or 'No Dealer Rating' in Deal or 'High Price' in Deal:
        return 0
    else:
        return 0

#creating scaling models to scale dependent car attributes
def Scale_Title(Title):

    if 'Clean' in Title:
        return 1
    elif 'Lemon' in Title or 'Salvage' in Title or 'No' in Title or 'Thief' in Title:
        return 0
    else:
        return 0

#creating scaling models to scale dependent car attributes
def Scale_Accidents(Accidents):

    if '0 accidents' in Accidents:
        return 1
    else:
        return 0

#creating scaling models to scale dependent car attributes
def Scale_Owners(Owners):

    if '1 previous owner' in Owners:
        return 1
    elif '2 previous owners' in Owners:
        return .6
    elif '3 previous owners' in Owners:
        return .4
    else:
        return 0

#creating scaling models to scale dependent car attributes
def Scale_ViewRating(DaysOnCarGurus, Saves):

    ViewRating = int(Saves) / int(DaysOnCarGurus)

    if ViewRating >1.0:
        return 1
    elif ViewRating <= 1 and ViewRating >= .9:
        return 0.9
    elif ViewRating <= .89 and ViewRating >=  .8:
        return 0.8
    elif ViewRating <= .79 and ViewRating >=  .7:
        return 0.7
    elif ViewRating <= .69 and ViewRating >=  .6:
        return 0.6
    elif ViewRating <=.59 and ViewRating >=  .5:
        return 0.5
    elif ViewRating <= .49 and ViewRating >=  .4:
        return 0.4
    elif ViewRating<= .39 and ViewRating >=  .3:
        return 0.3
    elif ViewRating <= .29 and ViewRating >=  .2:
        return 0.2
    elif ViewRating <= .19 and ViewRating >=  .1:
        return 0.1
    elif ViewRating <= .9 and ViewRating >= .0:
        return 0
    else:
        return 0

#creating scaling models to scale dependent car attributes
def Scale_DaysOnCarGurus(DaysOnCarGurus):

    if DaysOnCarGurus < 30:
        return 1
    elif DaysOnCarGurus >= 30 and DaysOnCarGurus <= 60:
        return 0.5
    elif DaysOnCarGurus >= 61 and DaysOnCarGurus < 90:
        return 0.25
    else:
        return 0

#creating scaling models to scale dependent car attributes
def Scale_TenYearInterestRate(TenYearInterestRate):

    if TenYearInterestRate >= 4:
        return 0
    elif TenYearInterestRate >= 3 and TenYearInterestRate <= 4:
        return 0.25
    elif TenYearInterestRate >= 2 and TenYearInterestRate < 3:
        return .5
    elif TenYearInterestRate >= 2 and TenYearInterestRate < 3:
        return 1
    else:
        return 0

#creating scaling models to scale dependent car attributes
def Scale_TotalVehicleSales(TotalVehicleSales):

    if TotalVehicleSales in "Up":
        return 1
    elif TotalVehicleSales in "Down":
        return 0
    else:
        return 0

#calculate PSC Score based
def Calc_PSCBand(PSC_Score):

    if PSC_Score >= 850 and PSC_Score <= 1000:
        return "A"
    elif PSC_Score >= 800 and PSC_Score < 850:
        return "B"
    elif PSC_Score >= 700 and PSC_Score < 800:
        return "C"
    elif PSC_Score >= 600 and PSC_Score < 700:
        return "D"
    elif PSC_Score >= 500 and PSC_Score < 600:
        return "E"
    elif PSC_Score < 500:
        return "F"
    else:
        "Invalid Score"


'''
Section 2: Loading Data From DB For Later TRANSFORMATION
'''

#PART 1 EXTRACT
#conn to DB - data being fed from apiAPP
conn = sqlite3.connect('/Users/princeabrahams/Desktop/Demo/CONSULTING/PrinceSportsCars/PrinceSportsCars.db')

#create flask server and APP
server = Flask(__name__)
app = dash.Dash(__name__,server = server ,meta_tags=[{ "content": "width=device-width"}], external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

#read carGurusData
carGurusDataMaster = pd.read_sql("select cardata from car_gurus_sports_car", conn)
carGurusDataDF = pd.DataFrame()

#END OF PART 1 EXTRACT

'''
Section 3: Transform the Needed Attributes for Plotly Application
'DealerInfo', 'Year', 'Make', 'Model', 'Price', 'Mileage', 'VIN',
       'DealDecision', 'CarFax', 'DaysOnMarket'
'''

#START OF PART 1 TRANSFORM
for index, row in carGurusDataMaster.iterrows():

    #get data
    json_data = row[0]

    #string replace Data
    json_data = json_data.replace('\\n','-')

    #change to dictionary remove double quotes
    json_data = ast.literal_eval(json_data)
    json_data = dict(json_data)

    #convert dictionary to dataframe & transpose
    carGurusDataSegmentDF = pd.DataFrame(json_data.items())
    carGurusDataSegmentDF = carGurusDataSegmentDF.transpose()

    #create first row as header
    new_header = carGurusDataSegmentDF.iloc[0]  # grab the first row for the header
    carGurusDataSegmentDF = carGurusDataSegmentDF[1:]  # take the data less the header row
    carGurusDataSegmentDF.columns = new_header  # set the header row as the df header

    #concat dataframe
    carGurusDataDF = pd.concat([carGurusDataDF, carGurusDataSegmentDF])

#Prep/Manipulate Cargurus Dataframe to create need for analytics
carGurusDataDF = carGurusDataDF.reset_index(drop=True)
carGurusDataDF = carGurusDataDF.astype(str)

#END OF PART 1 TRANSFORM

#START OF PART 2 TRANSFORM
#create/ manipulate columns columns
carGurusDataDF["DealerInfo"] = carGurusDataDF["DealerName"] + carGurusDataDF["DealerNumber"]
carGurusDataDF['CarMakeModelPriceYear'] = carGurusDataDF['CarMakeModelPriceYear'].astype(str)
carGurusDataDF['Year'] = carGurusDataDF['CarMakeModelPriceYear'].str[0:4]
carGurusDataDF['MakeModel'] = carGurusDataDF['CarMakeModelPriceYear'].str[4:-10]
carGurusDataDF['MakeModel'] = carGurusDataDF['MakeModel'].str.strip()
carGurusDataDF[['Make','Model']] = carGurusDataDF["MakeModel"].str.split(" ", 1, expand=True)
carGurusDataDF['Price'] = carGurusDataDF['CarMakeModelPriceYear'].str[-8:]
#Select Needed Columns
carGurusDataDF = carGurusDataDF[['Year', 'Make', 'Model', 'Price', 'DealerInfo',  'CarInfo','CarFax', 'DealDecision', 'DaysOnMarket']]

#END OF PART 2 TRANSFORM

#START OF PART 3 TRANSFORM

#create/ manipulate carGurusDataDF columns for VIN and Milees
carInfoDF = pd.DataFrame()

#for each row
for index, row in carGurusDataDF.iterrows():

    #parse column
    lst = row[5].strip('][').split(', ')
    lst = [i.replace('\'', '') for i in lst]

    #create list to hold parsed items
    transformedMiles = []
    transformedVin = []

    #retreive VIN and Miles from column 5 lst
    for item in lst:

        #if found append to list
        if len(item) == 17 and item[0] in "Z":
            transformedVin.append(item)

        if 'miles' in item:
            transformedMiles.append(item)

    #if not found append Unknown
    if len(transformedMiles) == 0:
        transformedMiles.append('Unknown')

    #if not found append Unknown
    if len(transformedVin) == 0:
        transformedVin.append('Unknown')

    #change List to DataFrame
    transformedMilesDF = pd.DataFrame(transformedMiles)
    transformedVinDF = pd.DataFrame(transformedVin)

    #clear list for next iteration
    transformedMiles.clear()
    transformedVin.clear()

    #concast Miles and VIN DF in CarInfo
    carInfoDFSegment = pd.concat([transformedMilesDF, transformedVinDF], axis=1)

    #flip carInfoDFSegment DF and Create Column Headers
    carInfoDFSegment.transpose()
    carInfoDFSegment.columns = ['Mileage', 'VIN']

    #concat iteration DF to final carInfoDF
    carInfoDF = pd.concat([carInfoDF, carInfoDFSegment])

#END OF PART 3 TRANSFORMATION

#START OF PART 4 TRANSFORMATION

#reset index
carInfoDF = carInfoDF.reset_index(drop=True)

#concat Car Info Dataframes needed - finalCarData needed later
finalCarData = pd.concat([carGurusDataDF, carInfoDF], axis=1)

#create a copy of finalCarData for more transformation
df = finalCarData[['DealerInfo', 'Year','Make', 'Model', 'Price', 'Mileage', 'VIN', 'DealDecision', 'CarFax', 'DaysOnMarket']]

#create a copy of finalCarData needed for plotly
dfPlotly = finalCarData[['DealerInfo', 'Year','Make', 'Model', 'Price', 'Mileage', 'VIN', 'DealDecision', 'CarFax', 'DaysOnMarket']]

#create current interest rate and total vehicle trend indicator
df['10YearInterestRate'] =  3.729
df['TotalVehicleSales'] =  'Up'

#parse mileage dataframe columns
df[['Mileage','String']] = df["Mileage"].str.split(" ", 1, expand=True)
df['Mileage'] = df["Mileage"].str.replace(",", "")
df[['DaysAtDealership','DaysOnCarGurus']] = df["DaysOnMarket"].str.split(" · ", 1, expand=True)
df[['DaysOnCarGurus', 'Saves']] = df["DaysOnCarGurus"].str.split(" · ", 1, expand=True)
df['DaysOnCarGurus'] = df.DaysOnCarGurus.str.extract('(\d+)')
df['Saves'] = df.Saves.str.extract('(\d+)')

#End OF PART 4 TRANSFORMATION

''' SECTION 4, RUN SCALING MODEL TO CALCULATE: 
PSC Score', 'PSC Grade', 'Car Will Sell By'
'''
# SELECT COLUMNS FOR FINAL ATTRIBUTES
Year = df['Year']
Mileage = df['Mileage']
Deal = df['DealDecision']
Title = df['CarFax']
Accidents = df['CarFax']
Owners = df['CarFax']
DaysOnCarGurus = df['DaysOnCarGurus']
Saves = df['Saves']
TenYearInterestRate = df['10YearInterestRate']
TotalVehicleSales = df['TotalVehicleSales']

#FINAL ATTRIBUTES DATAFRAME
final_attributes = pd.concat([Year, Mileage, Deal, Title, Accidents, Owners, DaysOnCarGurus, Saves, TenYearInterestRate, TotalVehicleSales], axis=1)
final_attributes.columns = ['Year', 'Mileage', 'Deal', 'Title', 'Accidents', 'Owners', 'DaysOnCarGurus', 'Saves', '10YearInterestRate', 'TotalVehicleSales']

#RUN SCORE ANALYSIS
for index in final_attributes.index:
    try:
        final_attributes.loc[index, 'Scaled Year'] = Scale_Year(
            pd.to_numeric(final_attributes.loc[index, 'Year']))
    except ValueError as err1:
        final_attributes.loc[index, 'Scaled Year'] = "invalid text"
    try:
        final_attributes.loc[index, 'Scaled Mileage'] = Scale_Mileage(
            pd.to_numeric(final_attributes.loc[index, 'Mileage']))
    except ValueError as err2:
        final_attributes.loc[index, 'Scaled Mileage'] = "invalid text"
    try:
        final_attributes.loc[index, 'Scaled Deal'] = Scale_Deal((final_attributes.loc[index, 'Deal']))
    except ValueError as err3:
        final_attributes.loc[index, 'Scaled Deal'] = "invalid text"
    try:
        final_attributes.loc[index, 'Scaled Title'] = Scale_Title((final_attributes.loc[index, 'Title']))
    except ValueError as err4:
        final_attributes.loc[index, 'Scaled Title'] = "invalid text"
    try:
        final_attributes.loc[index, 'Scaled Accidents'] = Scale_Accidents((final_attributes.loc[index, 'Accidents']))
    except ValueError as err4:
        final_attributes.loc[index, 'Scaled Accidents'] = "invalid text"
    try:
        final_attributes.loc[index, 'Scaled Owners'] = Scale_Owners((final_attributes.loc[index, 'Owners']))
    except ValueError as err4:
        final_attributes.loc[index, 'Scaled Owners'] = "invalid text"
    try:
        final_attributes.loc[index, 'Scaled View Rating'] = Scale_ViewRating(final_attributes.loc[index, 'DaysOnCarGurus'],final_attributes.loc[index, 'Saves'])
    except ValueError as err4:
        final_attributes.loc[index, 'Scaled View Rating'] = "invalid text"
    try:
        final_attributes.loc[index, 'Scaled DaysOnCarGurus'] = Scale_DaysOnCarGurus(
            pd.to_numeric(final_attributes.loc[index, 'DaysOnCarGurus']))
    except ValueError as err4:
        final_attributes.loc[index, 'Scaled DaysOnCarGurus'] = "invalid text"
    try:
        final_attributes.loc[index, 'Scaled 10YearInterestRate'] = Scale_TenYearInterestRate(
            pd.to_numeric(final_attributes.loc[index, '10YearInterestRate']))
    except ValueError as err4:
        final_attributes.loc[index, 'Scaled 10YearInterestRate'] = "invalid text"

    try:
        final_attributes.loc[index, 'Scaled TotalVehicleSales'] = Scale_TotalVehicleSales((final_attributes.loc[index, 'TotalVehicleSales']))
    except ValueError as err4:
        final_attributes.loc[index, 'Scaled TotalVehicleSales'] = "invalid text"

    try:
        final_attributes.loc[index, 'PSC Score'] = final_attributes.loc[index, 'Scaled Year'] + \
                                                            final_attributes.loc[index, 'Scaled Mileage'] + \
                                                            final_attributes.loc[index, 'Scaled Deal'] + \
                                                            final_attributes.loc[index, 'Scaled Title'] + \
                                                            final_attributes.loc[index, 'Scaled Accidents'] + \
                                                            final_attributes.loc[index, 'Scaled Owners'] + \
                                                            final_attributes.loc[index, 'Scaled View Rating'] + \
                                                            final_attributes.loc[index, 'Scaled DaysOnCarGurus'] + \
                                                            final_attributes.loc[index, 'Scaled 10YearInterestRate'] + \
                                                            final_attributes.loc[index, 'Scaled TotalVehicleSales']

    except:
        final_attributes.loc[index, 'PSC Score'] = 0

    try:
        final_attributes.loc[index, 'PSC Grade'] = Calc_PSCBand(
            pd.to_numeric(final_attributes.loc[index, 'PSC Score'] * 100))
    except ValueError as err1:
        final_attributes.loc[index, 'PSC Grade'] = "F"

#CREATE GRADE FOR SCORE
pscGrade = final_attributes[['PSC Grade', 'PSC Score']]

#CONCAT DFPLOTY AND PSCGRADE FOR LAST** DF
PlotyData = pd.concat([dfPlotly, pscGrade], axis=1)

#CREATE DATES GRADES WILL SELL AT
ADate = date.today() + timedelta(days=30)
BDate = date.today() + timedelta(days=60)
CDate = date.today() + timedelta(days=90)
DDate = date.today() + timedelta(days=120)
EDate = date.today() + timedelta(days=240)
FDate = date.today() + timedelta(days=360)

#CREATE CAR WILL SELL BY GRADE BASED ON PSC GRADE
PlotyData.loc[(PlotyData['PSC Grade'] == 'A') , 'Car Will Sell By'] = '30 Days ' + str(ADate)
PlotyData.loc[(PlotyData['PSC Grade'] == 'B') , 'Car Will Sell By'] = '60 Days ' + str(BDate)
PlotyData.loc[(PlotyData['PSC Grade'] == 'C') , 'Car Will Sell By'] = '90 Days ' + str(CDate)
PlotyData.loc[(PlotyData['PSC Grade'] == 'D') , 'Car Will Sell By'] = '120 Days ' + str(DDate)
PlotyData.loc[(PlotyData['PSC Grade'] == 'E') , 'Car Will Sell By'] = '240 Days ' + str(EDate)
PlotyData.loc[(PlotyData['PSC Grade'] == 'F') , 'Car Will Sell By'] = '360 Days ' + str(FDate)

#MULTIPLE SCORE BY 100 & CHANGE TO INT FOR VIEWING SIMPLICITY
PlotyData['PSC Score'] = PlotyData['PSC Score'] * 100
PlotyData['PSC Score'] = PlotyData['PSC Score'].astype(int)

#SELECT NEEDED COLUMNS
PlotyData = PlotyData[['DealerInfo', 'Year', 'Make', 'Model', 'Price', 'Mileage', 'VIN',
       'DealDecision', 'CarFax', 'DaysOnMarket', 'PSC Score', 'PSC Grade', 'Car Will Sell By']]

#DROP ANY DUPLICATES BASED ON VIN
PlotyData = PlotyData.drop_duplicates(
    subset=['VIN']).reset_index(drop=True)

app = dash.Dash(__name__)

# -------------------------------------------------------------------------------------
# App layout
app = dash.Dash(__name__, prevent_initial_callbacks=True)  # this was introduced in Dash version 1.12.0

app.layout = html.Div([
    dash_table.DataTable(
        id='VIN',
        columns=[{"name": i, "id": i} for i in PlotyData.columns],
        data=PlotyData.to_dict('records'),  # the contents of the table
        editable=True,  # allow editing of data inside all cells
        filter_action="native",  # allow filtering of data by user ('native') or not ('none')
        sort_action="native",  # enables data to be sorted per-column by user or not ('none')
        sort_mode="single",  # sort across 'multi' or 'single' columns
        column_selectable="multi",  # allow users to select 'multi' or 'single' columns
        row_selectable="multi",  # allow users to select 'multi' or 'single' rows
        row_deletable=True,  # choose if user can delete a row (True) or not (False)
        selected_columns=[],  # ids of columns that user selects
        selected_rows=[],  # indices of rows that user selects
        page_action="native",  # all data is passed to the table up-front or not ('none')
        page_current=0,  # page number that user is on
        page_size=100,  # number of rows visible per page
        style_cell={  # ensure adequate header width when text is shorter than cell's text
            'minWidth': 95, 'maxWidth': 95, 'width': 95
        },
        style_data={  # overflow cells' content into multiple lines
            'whiteSpace': 'normal',
            'height': 'auto'
        }
    ),

    html.Br(),
    html.Br(),
    html.Div(id='bar-container'),
    html.Div(id='choromap-container')

])


if __name__ == '__main__':
    app.run_server(debug = True)
