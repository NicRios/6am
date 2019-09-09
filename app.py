from flask import Flask, redirect, render_template, url_for, request
import requests, json

app = Flask(__name__)

@app.route("/",methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route("/upload.html", methods=['GET', 'POST'])
def upload_route_summary():
    if request.method == 'POST':
        f = request.files['fileupload']
        fstring = f.read()
        print fstring
    return "success"

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
        if crm == 'Salesforce':
            ddip_url = 



if __name__ == "__main__":
    app.run(debug=True)
