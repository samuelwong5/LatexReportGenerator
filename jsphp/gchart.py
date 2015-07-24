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

@app.route("/")
def hello():
    print("shutting down...")
    server.terminate()
    print("terminated")
    server.join()
    print("joined")

    shutdown_server()
    print("wtf")
    return("HOW AM I STILL ALIVE")


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
    try:
        with open(os.path.join(report, fname + '.csv')) as csv_file:
            dreader = csv.DictReader(csv_file)
            header = dreader.fieldnames
            count = 0 
            other = 0
            html += "['" + header[0] + "', '" + header[1] + "'],\n      "
            for row in dreader:
                if count > 9:
                    other += int(row[header[1]])
                else: 
                    html += "['" + row[header[0]] + "', " + row[header[1]] + "],\n      "
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
    return(html)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown/')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


def start_flask():
    app.run('0.0.0.0')

  
server = Process(target=start_flask)
  
    
if __name__ == '__main__':
    # server.start()
    with open('deface.html', 'w+') as f:
        f.write(serve('DefacementTld'))
    display = Display(visible=0, size=(1024, 768))
    display.start()
    print('Initializing Selenium webdriver...')        
    driver = webdriver.Firefox()
    print('Rendering Google Charts...')
    print('file://' + os.getcwd() + os.sep + 'deface.html')
    driver.get(os.getcwd() + os.sep + 'deface.html')
    print('loaded html')
    base = driver.find_element_by_id('png').getText()
    print(base)
