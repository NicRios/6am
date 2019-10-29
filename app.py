from flask import Flask, redirect, render_template, url_for, request, send_file, Response, g
import requests, json
import pandas as pd
import re
from oauth2client import file, client, tools
from googleapiclient.discovery import build
from httplib2 import Http
import pygsheets
from datetime import datetime, timedelta
from threading import Timer


Spreadsheet_ID = '1LF4jEET_2RwJrSuCQJy2U5gnVqIbvNDFuLyi9_tLo84'
Range_name = 'Sheet1'
dfs = []
x = datetime.today()
y = x.replace(day=x.day, hour=4, minute=0, second=0, microsecond=0) + timedelta(days=1)
delta_t=y-x
secs=delta_t.total_seconds()
print(secs)


def get_google_sheet(spreadsheet_id, range_name):
    print('entered get_google_sheet again')
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
    print('entered gsheet2df again')
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
def daily():
    print('entered daily again')
    gsheet = get_google_sheet(Spreadsheet_ID, Range_name)
    df = gsheet2df(gsheet)
    if not dfs:
        print('df array empty in daily function')
        dfs.append(df)
    else:
        print('df array has a previous value when daily gets called again')
        dfs.pop()
        if not dfs:
            print('This should get called - empty array')
        dfs.append(df)

app = Flask(__name__)

@app.route("/",methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route("/studio",methods=['GET', 'POST'])
def studio():
    #gsheet = get_google_sheet(Spreadsheet_ID, Range_name)
    #df = gsheet2df(gsheet)
    #print(df.head())
    #print('Dataframe size = ', df.shape)
    if not dfs:
        daily()
    dataframe = dfs[-1]
    if request.method =='POST':
        routeParam = request.get_json()
        checkDB = routeParam['param'];
        if checkDB[0] == '+' and checkDB[1] =='1':
            checkDB = checkDB[2]+ checkDB[3] + checkDB[4]
        print(checkDB)
        for index, row in dataframe.iterrows():
            temp = row['in']
            if temp == checkDB:
                out = dataframe.at[index, 'out']
                a = { 'output': out }
                python2json = json.dumps(a)
                print(python2json)
                return Response(json.dumps(a), mimetype='application/json')

        b = { 'output': 'wrong' }
        print('shouldnt be here')
        return Response(json.dumps(b), mimetype='application/json')


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
        filterby= jsonFile2['filterby']
        filterby2 = jsonFile2['filterby2']
        print(filterby)
        print(filterby2)
        if filterby != '':
            contactphone = re.sub('[^0-9]','',filterby[0])
            print(contactphone)
            code = 'Select ' + field + ' From ' + object + ' Where Phone =\'+'+ contactphone + '\' Limit 1'
            print(code)
        else:
            if filterby2 != '':
                contactemail = filterby2
                print(contactemail)
                code = 'Select ' + field + ' From ' + object + ' Where Email =\' '+ contactemail + '\' Limit 1'
                print(code)
        if crm == 'Salesforce':
            ddip_url = 'http://talkforce.force.com/omnidatadip/services/apexrest/webdatadip/go'
            headers = { 'code': code }
        else:
            ddip_url = ''
            headers = { 'code': code }
        print(ddip_url)
        r = requests.get(ddip_url, headers = headers)
        out = r.json()
        #id = out['Id']
        print(out)
        start = out.find('=') +1
        end = len(out) - 2
        final =out[start:end]
        print(final)
        finalurl = 'https://talkforce.lightning.force.com/lightning/r/Contact/' + final + '/view'
        finalout = {'url': finalurl}
    return finalout

t = Timer(secs, daily)
t.start()

if __name__ == "__main__":
    app.run(debug=True)
