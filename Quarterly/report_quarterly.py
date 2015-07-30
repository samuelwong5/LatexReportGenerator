import csv
import os
import sys

from flask import Flask
from multiprocessing import Process

# Global variables
app = Flask(__name__, static_url_path='')

def read_csv(file, columns=[], max_row=-1):
    header = []
    data = []
    row_count = max_row
    with open(file) as csv_file:
        reader = csv.DictReader(csv_file)
        header = reader.fieldnames
        if columns == []:
            columns = range(len(header))
        data = len(columns) * [[]]
        for row in reader:
            for i in range(len(columns)):
                data[i].append(row[header[columns[i]]])
            row_count -= 1
            if row_count == 0:
                break
    return header, data
                  

def prev_qrtr(year, qrtr, offset):
    new_qrtr = qrtr
    new_year = year
    for i in range(offset):
        if new_qrtr == 1:
            new_qrtr = 4
            new_year -= 1
        else:
            new_qrtr -= 1
    return str(new_year).zfill(2) + str(new_qrtr).zfill(2)

config = {}
    
def main():
    data_dir = 'QOutput/'
    yymm = int(sys.argv[1])
    qrtr = yymm % 10
    year = (yymm - qrtr) / 100
    qrtr_label = map(lambda x: prev_qrtr(year, qrtr, x),
                     range(4,-1,-1))
    data_paths = map(lambda x: data_dir + x + '/report/', qrtr_label)
    qrtr_label = map(lambda x: '20' + str(int(x)/100) + ' Q' + str(int(x)%100),
                     qrtr_label)
    global config
    config = {'data_paths': data_paths, 'qrtr_label': qrtr_label}
    
    server = Process(target=start_flask) 
    server.start()
    print('multithread')
    
@app.route("/urlip/<fname>")
def serve_urlip(fname):
    url_ip_col = {'Defacement': 1,'Phishing': 2, 'Malware': 3}
    url_ip_data = [[],[]]
    for d in config['data_paths']:
        _, data = read_csv(d + 'serverSummary.csv', columns=[url_ip_col[fname]])
        url_ip_data[0].append(data[0][1])
        url_ip_data[1].append(data[0][3])
    data = zip(config['qrtr_label'], url_ip_data[0], url_ip_data[1])
    data_array = ["[['" + fname + "','Unique URL', 'Unique IP']"]
    for d in data:
        data_array.append("['" + d[0] + "'," + d[1] + "," + d[2] + "]")
    data_str = ','.join(data_array) + ']'    
    html = ''
    with open('google_bar_chart.html') as f:
        html = f.read()
    html = html.replace('__DATA_ARRAY__', data_str) \
               .replace('__CHART_TITLE__', 'Trend of ' + fname + ' security events') 
    return html
    
def start_flask():
    #f = open(os.devnull, 'w')
    #sys.stdout = f
    #sys.stderr = f
    app.run('0.0.0.0')
    
main()
