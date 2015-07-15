import plotly.plotly as py
from plotly.graph_objs import *
import csv
import math

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
    py.image.save_as({'data': data}, 'ISPTotal.png')
    
def drawTldPolar(fpath, gname):
    with open(fpath) as tldCsv:
        reader = csv.DictReader(tldCsv)
        tld = []
        count = []
        total = 0
        for row in reader:
            tld.append(row['Top Level Domain'])
            count.append(float(row['count']))
            total += float(row['count'])
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
        py.image.save_as({'data': data}, gname + '.png')

def main():
    csvDir = 'HKSWROutput/report/'    
    drawIspAll(csvDir + 'ISPAll.csv')
    drawTldPolar(csvDir + 'DefacementTld.csv', 'Defacement - ISP Distribution')

if __name__ == "__main__":    
    main()    