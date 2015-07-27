from flask import Flask
from flask import send_from_directory
from multiprocessing import Process
import requests
import os
import csv
from pyvirtualdisplay import Display
from selenium import webdriver

app = Flask(__name__, static_url_path='')
report = '/home/samuelwong/Report/HKSWROutput/1505/report'

@app.route("/graph/<fname>")
def serve(fname):
    print(os.path.join(report, fname +'.csv'))
    html = '''<html><head>
<script type="text/javascript" src="https://www.google.com/jsapi"></script>
<script type="text/javascript">
google.load("visualization", '1', {packages:['corechart']}); 
google.setOnLoadCallback(drawChart); 
  function drawChart() { 
    var arr = ['''    
    f_path = os.path.join(report, fname + '.csv')
    if not os.path.isfile(f_path):
        return 'File not found.'
    try:
        with open(f_path) as csv_file:
            dreader = csv.DictReader(csv_file)
            header = dreader.fieldnames
            count = 0 
            other = 0
            html += "['" + header[0] + "', '" + header[1] + "'],\n      "
            for row in dreader:
                if count > 9:
                    other += int(row[header[1]])
                else: 
                    html += "['" + row[header[0]].replace("'", "") + "', " + row[header[1]] + "],\n      "
                count += 1
    
            html += "['Other', " + str(other) + "]];\n"
    except:
        print "Unexpected error:", sys.exc_info()[0]
    html += '''
    var data = google.visualization.arrayToDataTable(arr);
    var options = {
      //is3D: true,
      pieHole: 0.35,
      offset: 0.1,
      width: 800,
      height: 800
    };
    var chart_div = document.getElementById('chart');
    var chart = new google.visualization.PieChart(chart_div);
    chart.draw(data, options);
    document.getElementById("png").innerHTML = chart.getImageURI();
  }
  </script>
  </head>
<body>
  <div id="png" class="png"></div>
  <div id="chart" style="width: 900px; height: 600px;"></div>
</body>
</html>'''
    with open('debug.html', 'w+') as f:
        f.write(html)
    return(html)

def set_input_dir(dir):
    global report
    report = dir

    
def start_flask():
    app.run('0.0.0.0')
     

server = Process(target=start_flask)   
 
 
def start_flask_process():
    server.start()

    
if __name__ == '__main__':
    server.start()