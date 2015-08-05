import csv
import os
import sys

from flask import Flask
from flask import send_from_directory
from multiprocessing import Process

# Global variables
app = Flask(__name__, static_url_path='')
report = '/home/samuelwong/Report/HKSWROutput/1505/report'

@app.route("/graph/<fname>")
def serve(fname): 
    html = ''
    f_path = os.path.join(report, fname + '.csv')
    if not os.path.isfile(f_path):
        return 'File not found.'
    try:
        with open(f_path) as csv_file:
            dreader = csv.DictReader(csv_file)
            header = dreader.fieldnames
            count = 0 
            other = 0
            html += "['" + header[0] + "', '" + header[len(header)-1] + "'],\n      "
            for row in dreader:
                if count > 9:
                    if row[header[len(header)-1]] != '':
                        other += int(row[header[len(header)-1]])
                else: 
                    html += "['" + row[header[0]].replace("'", "") + "', " + row[header[len(header)-1]] + "],\n      "
                count += 1
    
            html += "['Other', " + str(other) + "]];\n"
    except:
        print "Unexpected error:", sys.exc_info()[0]
    
    with open('gchart.html') as f:
        html = f.read().replace('__DATA_ARRAY__',html)
    
    return(html)

    
def set_input_dir(dir):
    global report
    report = dir
    
    
def start_flask():
    f = open(os.devnull, 'w')
    sys.stdout = f
    sys.stderr = f
    app.run('0.0.0.0')
  
 
def start_flask_process():
    server.start()

def stop_flask_process():
    server.terminate()
    server.join()
    
    
server = Process(target=start_flask) 
    
    
if __name__ == '__main__':
    if (len(sys.argv) > 1):
        report = sys.argv[1]
    server.start()