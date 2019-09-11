from flask import Flask, redirect, render_template, url_for, request, send_file
import requests, json
import pandas as pd
import re

app = Flask(__name__)

@app.route("/",methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route("/upload.html", methods=['GET', 'POST'])
def upload_route_summary():
    if request.method == 'POST':
        f = request.files['fileupload']
        data = pd.read_csv(f)
        for index, row in data.iterrows():
            num = row['Phone']
            print(num)
            if not isinstance(num,str):
                num = str(num)
                #num = num[1:]
            justNum = re.sub('[^0-9]','',num)
            print(justNum)
            if len(justNum) < 10 or len(justNum) > 11:
                print('invalid US number')
            if len(justNum) ==10:
                justNum = '+1' + justNum
                data['Phone'] = justNum;
            if len(justNum) == 11:
                if justNum[0] != '1':
                    print('invalid US number')
                else:
                    justNum = '+' + justNum
                    data['Phone'] = justNum;
        data.to_csv("updated.csv")
    return send_file('updated.csv',
                     mimetype='text/csv',
                     attachment_filename='updated.csv',
                     as_attachment=True)

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

# @app.route("/ddip", methods=['GET', 'POST'])
# def dip():
#     if request.method == 'POST':
#         jsonFile2 = request.json
#         crm = jsonFile2['crm']
#         code jsonFile2['code']
#         if crm == 'Salesforce':
#             ddip_url = ''
#             headers = {}





if __name__ == "__main__":
    app.run(debug=True)
