import plotly.plotly as py
from plotly.graph_objs import *
from selenium import webdriver
from pyvirtualdisplay import Display
import csv
import requests
import shutil
import os
import sys

# returns filename from complete path
# strips path and extension
def get_file_name(file_path):
    strSplit = file_path.split('/')
    return (strSplit[len(strSplit) - 1]).split('.')[0]
    
    
# file_path: relative file path to .csv file
# max: optional maximum number of bars
# bar_mode: 'overlay', 'stack', 'group'
def draw_bar_chart(file_path, max, bar_mode='stack'):
    # method scoped variables assigned in 'with' scope
    data = []
    headers = []
    
    # reading from csv file
    with open(file_path) as csv_file:
        dreader = csv.DictReader(csv_file)
        headers = dreader.fieldnames
        for row in dreader:
            for i in range(len(headers)):
                if (len(data) < len(headers)):
                    data.append([])
                if (i == 0):
                    data[0].append(row[headers[0]])
                else:
                    data[i].append(float(row[headers[i]]))
                    
    # converting raw data to plotly 'Bar' class
    bars = []
    for i in range(1,len(data)):
        if (max == -1):
            bars.append(Bar(
                            x=data[0],
                            y=data[i],
                            name=headers[i]
                        ))
        else:
            bars.append(Bar(
                            x=(data[0])[:10],
                            y=(data[i])[:10],
                            name=headers[i]
                        ))
                        
    # misc. chart setup
    chart_data = Data(bars)
    chart_title = get_file_name(file_path)
    layout = Layout(
        title=chart_title,
        font=Font(
            size=16
        ),
        barmode=bar_mode
    )
    fig = Figure(data=chart_data,layout=layout)
    
    # plot and download chart
    plot_url = py.plot(fig, chart_title)
    download_png(plot_url, 'graphs/' + chart_title + '.png')      

    
# url: html url to .png file
# output: output relative file location        
def download_png(url, output):
    r = requests.get(url + '.png', stream=True)
    print_no_newline('Saving image: ' + output)
    if r.status_code == 200:
        dir = os.path.dirname(output)
        if not os.path.exists(dir): # Check that parent dir exists
            os.makedirs(dir)
        with open(output, 'w+b') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        print_done()   

        
# util function for printing to terminal without newline char 
def print_no_newline(text):
    sys.stdout.write(text + (' ' * (74 - len(text))))
    sys.stdout.flush()     
    
    
# util function for printing "[DONE]" 
def print_done():
    print('[DONE]')    
        
# main function        
def main():
    # bar charts
    bar_chart_max_bars = 10           # Number of bars in bar chart  
    bar_chart_dir = os.getcwd() + '/data/bar'
    for file in os.listdir(bar_chart_dir):
        draw_bar_chart(bar_chart_dir + '/' + file, bar_chart_max_bars)
        
    # pie charts     
    print_no_newline('Starting virtual display...')
    display = Display(visible=0, size=(1024, 768))
    display.start()
    print_done()
    print_no_newline('Initializing Selenium webdriver...')        
    driver = webdriver.Firefox()
    print_done()
    print_no_newline('Rendering Google Charts...')
    driver.get("http://localhost/graph.html")
    print_done() 
    print_no_newline('Downloading Google Charts...')
    while ("Done" not in driver.title):
        time.sleep(1);
    print_done()              

if __name__ == "__main__":    
    main()    