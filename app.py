from flask import Flask, redirect, render_template, url_for, request, send_file
import requests, json
import pandas as pd
import re
from oauth2client import file, client, tools
from googleapiclient.discovery import build
from httplib2 import Http
import pygsheets


Spreadsheet_ID = '1LF4jEET_2RwJrSuCQJy2U5gnVqIbvNDFuLyi9_tLo84'
Range_name = 'Sheet1'

def get_google_sheet(spreadsheet_id, range_name):
    """ Retrieve sheet data using OAuth credentials and Google Python API. """
    scopes = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    # Setup the Sheets API
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', scopes)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API
    gsheet = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    return gsheet

def gsheet2df(gsheet):
    header =  gsheet.get('values', [])[0]   # Assumes first line is header!
    values = gsheet.get('values', [])[1:]  # Everything else is data.
    if not values:
        print('No data found.')
    else:
        all_data = []
        for col_id, col_name in enumerate(header):
            column_data = []
            for row in values:
                column_data.append(row[col_id])
            ds = pd.Series(data=column_data, name=col_name)
            all_data.append(ds)
        df = pd.concat(all_data, axis=1)
        return df

app = Flask(__name__)

@app.route("/",methods=['GET', 'POST'])
def index():
    # gsheet = get_google_sheet(Spreadsheet_ID, Range_name)
    # df = gsheet2df(gsheet)
    # print(df.head())
    # #print('Dataframe size = ', df.shape)
    # if request.method =='GET' and request.get_json() != None:
    #     routeParam = request.get_json()
    #     checkDB = routeParam['param'];
    #     for index, row in df.iterrows():
    #         temp = row['in']
    #         if temp == checkDB:
    #             out = df.at[index, 'out']
    #         #temp_row = df.loc[df['in'] == checkDB ]
    #     #finaloutput = temp_row['out']
    #     return str(out)

    return render_template('index.html')

@app.route("/studio",methods=['GET', 'POST'])
def studio():
    gsheet = get_google_sheet(Spreadsheet_ID, Range_name)
    df = gsheet2df(gsheet)
    print(df.head())
    #print('Dataframe size = ', df.shape)
    if request.method =='POST':
        routeParam = request.get_json()
        checkDB = routeParam['param'];
        for index, row in df.iterrows():
            temp = row['in']
            if temp == checkDB:
                out = df.at[index, 'out']
                return str(out)
            #temp_row = df.loc[df['in'] == checkDB ]
        #finaloutput = temp_row['out']
    #return str(out)


@app.route("/upload.html", methods=['GET', 'POST'])
def upload_route_summary():
    if request.method == 'POST':
        f = request.files['fileupload']
        data = pd.read_csv(f)
        data['Phone'].astype(str)
        for index, row in data.iterrows():
            num = row['Phone']
            print("num is: ", num)
            if not isinstance(num,str):
                num = str(num)
                print("string conversion")
                #num = num[1:]
            justNum = re.sub('[^0-9]','',num)
            print("justNum is: ", justNum)
            if len(justNum) < 10 or len(justNum) > 11:
                print('invalid US number')
            else:
                 if len(justNum) ==10:
                     finalNum = '+1' + str(justNum)
                     print("finalNum is: ", finalNum)
                     data.at[index, 'Phone'] = finalNum
                     print(row)
                     continue;
                 else:
                      if len(justNum) == 11:
                         if justNum[0] != '1':
                             print('invalid US number')
                         else:
                             finalNum = '+' + str(justNum)
                             print("finalNum is: ", finalNum)
                             data.at[index, 'Phone'] = finalNum
                             print(row)
        data.to_csv("updated.csv")
    return send_file('updated.csv', mimetype='text/csv', attachment_filename='updated.csv', as_attachment=True)

@app.route("/format/json", methods=['GET', 'POST'])
def format_json():
    if request.method == 'POST':
        jsonFile = request.json
        final_url = jsonFile['url']
        method = jsonFile['method']
        print(request.json)
        print(method)
        print(final_url)
        # first = jsonFile['first']
        # second = jsonFile['second']
        # third = jsonFile['third']
        # if(first!= 'none'):
        #     firstl = first.split('|', 1)
        #     firstkey = firstl[0]
        #     firstvalue = firstl[1]
        # if(second != 'none'):
        #     secondl = second.split('|', 1)
        #     secondkey = secondl[0]
        #     secondvalue = secondl[1]
        # if(third != 'none'):
        #     thirdl = third.split('|', 1)
        #     thirdkey = thirdl[0]
        #     thirdvalue = thirdl[1]
        # payload = {firstkey: firstvalue, secondkey: secondvalue, thirdkey: thirdvalue}
        payload = {
        	"url": "https://hooks-us.imiconnect.io/events/NFG9Q8Y8G998",
        	"method": "post"
        }
        headers ={"Content-Type": "application/json"}
        if method == 'post':
            r = requests.post(final_url, data = json.dumps(payload), headers = headers)
            output = r.content
        if method == 'get':
            r = requests.get(final_url)
            output = r.content
    return output

@app.route("/ddip", methods=['GET', 'POST'])
def dip():
    if request.method == 'POST':
        jsonFile2 = request.json
        crm = jsonFile2['crm']
        object = jsonFile2['object']
        field = jsonFile2['field']
        filterBy = jsonFile2['filterBy']
        code = 'Select ' + field + ' From ' + object + ' Where ' + filterBy
        #code = jsonFile2['code']
        if crm == 'Salesforce':
            ddip_url = 'http://talkforce.force.com/omnidatadip/services/apexrest/webdatadip/go'
            headers = { 'code': code }
        else:
            ddip_url = ''
            headers = { 'code': code }
        r = requests.get(ddip_url, headers = headers)
        out = r.json()
    return out


if __name__ == "__main__":
    app.run(debug=True)
