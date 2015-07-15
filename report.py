import plotly.plotly as py
from plotly.graph_objs import *
import csv
import math
import requests
import shutil
import os

# file_path: relative file path to .csv file
# max: optional maximum number of bars
# chart_title: header of the chart and filename of .png
# bar_mode: 'overlay', 'stack', 'group'
def drawBarChart(file_path, max, chart_title, bar_mode):
    data = []
    headers = []
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
    chartData = Data(bars)
    layout = Layout(
        title=chart_title,
        font=Font(
            size=16
        ),
        barmode=bar_mode
    )
    fig = Figure(data=chartData,layout=layout)
    plot_url = py.plot(fig, chart_title)
    downloadPng(plot_url, 'graphs/' + chart_title + '.png')      
            
def drawIspAll(fpath):
    isp = []
    dfc = []
    phi = []
    mal = []
    bot = []
    with open(fpath) as ispCsv:
        reader = csv.DictReader(ispCsv)
        rowCount = 0
        for row in reader:
            if (rowCount < 10):         # Only top 10
                isp.append(row['ISP'])
                dfc.append(row['Defacement Count'])
                phi.append(row['Phishing Count'])
                mal.append(row['Malware Count'])
                bot.append(row['Botnet Count'])    
                # row['Total Count']    Not used as bar chart stacks        
                rowCount += 1
            else:
                break
    dfcBar = Bar(
        x=isp,  
        y=dfc,
        name='Defacement'
    )
    phiBar = Bar(
        x=isp,
        y=phi,
        name='Phishing'
    )
    malBar = Bar(
        x=isp,
        y=mal,
        name='Malware'
    )
    botBar = Bar(
        x=isp,
        y=bot,
        name='Botnet'
    )
    data = Data([dfcBar,phiBar,malBar,botBar])
    layout = Layout(barmode='stack')
    fig = Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename='ISP_Total')
    print("ISP Total URL: " + plot_url)
    downloadPng(plot_url, 'graphs/ISP_Total.png')
    
def drawTldPolar(fpath, gname, fields):
    with open(fpath) as tldCsv:
        reader = csv.DictReader(tldCsv)
        tld = []
        count = []
        total = 0
        for row in reader:
            tld.append(row[fields[0]])
            count.append(float(row[fields[1]]))
            total += float(row[fields[1]])
        wedges = []
        for i in range(len(count)):
            wedges.append(
                Area(
                    r=[0]*i + [math.log(count[i]+2)] + [0]*(len(count)-i-1),
                    t=tld,
                    name=tld[i] + ' - ' + str(int(count[i]/total*100)) + '%',
                    marker=Marker(
                        color='rgb(' + str(i*256/len(count)) + str((len(count)-i)*256/len(count)) + ',100)'
                    )
                ))
        data = Data(wedges)
        layout = Layout(
            title=gname,
            font=Font(
                size=16
            ),
            legend=Legend(
                font=Font(
                    size=16
                )
            ),
            orientation=270
        )
        fig = Figure(data=data, layout=layout)
        plot_url = py.plot(fig, filename=gname)
        print(gname + ': ' + plot_url)
        downloadPng(plot_url, 'graphs/' + gname + '.png')
        
def downloadPng(url, output):
    r = requests.get(url + '.png', stream=True)
    if r.status_code == 200:
        dir = os.path.dirname(output)
        if not os.path.exists(dir): # Check that parent dir exists
            os.makedirs(dir)
        with open(output, 'w+b') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        print('Saving image\nFROM: ' + url + '.png\nTO:   ' + output)

def main():
    csvDir = 'HKSWROutput/report/'    # Relative path to .csv data files  
    drawIspAll(csvDir + 'ISPAll.csv')
    drawTldPolar(csvDir + 'DefacementTld.csv', 'Defacement - ISP Distribution',
                    ['Top Level Domain', 'count'])
    drawTldPolar(csvDir + 'MalwareTld.csv', 'Malware - ISP Distribution',
                    ['Top Level Domain', 'count'])
    drawTldPolar(csvDir + 'PhishingTld.csv', 'Phishing - ISP Distribution',
                    ['Tld', 'Count'])

def test():
    csvDir = 'HKSWROutput/report/'    # Relative path to .csv data files  
    drawBarChart(csvDir + 'ISPAll.csv', 10, 'ISP_Total', 'stack')
    
if __name__ == "__main__":    
    test() #main()   