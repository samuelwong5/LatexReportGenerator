import plotly.plotly as py
from plotly.graph_objs import *
import csv

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
    
def main():
    csvDir = 'HKSWROutput/report/'    
    drawIspAll(csvDir + 'ISPAll.csv')

if __name__ == "__main__":    
    main()    