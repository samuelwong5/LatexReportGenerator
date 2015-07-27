import csv
import os
import sys

import plotly.plotly as py
from plotly.graph_objs import *
import requests    

def main(file_paths):
    ssfile = 'serverSummary.csv'
    ssfiles = [file_paths[0] + ssfile,
               file_paths[1] + ssfile,
               file_paths[2] + ssfile]
    create(ssfiles)
    bot_data = [['Mar15','Apr15','May15'],[]]   
    ccfile = 'C&CServers.csv'
    ccfiles = [file_paths[0] + ccfile,
               file_paths[1] + ccfile,
               file_paths[2] + ccfile]
    for ccf in ccfiles:
        with open(ccf) as csv_file:
            dreader = csv.DictReader(csv_file)
            hold = []
            for row in dreader:
                if row['ip'] not in hold:
                   hold.append(row['ip'])        
            bot_data[1].append(len(hold))
    generate_chart(bot_data, ['Month', 'Botnet (C&Cs)'], 'BotCCDis', 'Botnet (C&Cs) security event distribution')
    
    cc_data = [['IRC','HTTP','P2P'],[0,0,0]]
    with open(ccfiles[2]) as csv_file:
        dreader = csv.DictReader(csv_file)
        hold = []
        for row in dreader:
            if row['ip'] not in hold:
                if row['channel'] == '-': #HTTP
                    cc_data[1][1] += 1 
                else:                     #IRC
                    cc_data[1][0] += 1  
                hold.append(row['ip'])                 
    generate_chart(cc_data, ['Communication Type', 'Count'], 'BotCCType', 'Botnet (C&Cs) by communication type')
   
    bot_data = [['Mar15','Apr15','May15'],[]]   
    bnfile = 'botnetDailyMax.csv'
    bnfiles = [file_paths[0] + bnfile,
               file_paths[1] + bnfile,
               file_paths[2] + bnfile]
    for bnf in bnfiles:
        with open(bnf) as csv_file:
            dreader = csv.DictReader(csv_file)
            total_count = 0
            for row in dreader:
                if row['Count'] != '':
                    total_count += int(row['Count'])
            bot_data[1].append(total_count)
    generate_chart(bot_data, ['Month', 'Botnet (Bots)'], 'BotBotsDis', 'Botnet (Bots) security event distribution')
    
    
    
def create(file_paths):
    data = []
    headers = []
    for j in range(len(file_paths)):
        data.append([])
        with open(file_paths[j]) as csv_file:
            dreader = csv.DictReader(csv_file)
            headers = dreader.fieldnames
            for row in dreader:
                for i in range(len(headers)):
                    if (len(data[j]) < len(headers)):
                        data[j].append([])
                    data[j][i].append(row[headers[i]])

    server_dis_headers = ['Month','Defacement','Phishing','Malware']                
    server_dis = [['Mar15','Apr15','May15']]
    for i in range(3):
        server_dis.append([])
        for j in range(3):
            server_dis[i+1].append(data[j][i+1][1])
    generate_chart(server_dis, server_dis_headers, 'ServerRelated', 'Server Related security events distribution','stack')

    gen_headers = ['Month','URL','Domain','IP']                
    gen_data = [['Mar15','Apr15','May15'],[],[],[]]
    for i in range(3):
        gen_data[i+1] = []
        for j in range(3):
            gen_data[i+1].append(data[j][1][i+1])
            
    generate_chart(gen_data, gen_headers, 'DefacementGen', 'Defacement General Statistics')
               
    gen_data = [['Mar15','Apr15','May15'],[],[],[]]
    for i in range(3):
        gen_data[i+1] = []
        for j in range(3):
            gen_data[i+1].append(data[j][2][i+1])  
    generate_chart(gen_data, gen_headers, 'PhishingGen', 'Phishing General Statistics')
           
    gen_data = [['Mar15','Apr15','May15'],[],[],[]]
    for i in range(3):
        gen_data[i+1] = []
        for j in range(3):
            gen_data[i+1].append(data[j][3][i+1])  
    generate_chart(gen_data, gen_headers, 'MalwareGen', 'Malware General Statistics')
    
    url_ip_headers = ['Month', 'URL/IP Ratio']
    gen_data = [['Mar15','Apr15','May15'],[]]
    gen_data[1] = []
    for j in range(3):
        gen_data[1].append(round(float(data[j][1][1]) / float(data[j][1][3]),2))  
    generate_chart(gen_data, gen_headers, 'DefacementURLIP', 'Defacement URL/IP Ratio')
    
    gen_data = [['Mar15','Apr15','May15'],[]]
    gen_data[1] = []
    for j in range(3):
        gen_data[1].append(round(float(data[j][2][1]) / float(data[j][2][3]),2))  
    generate_chart(gen_data, gen_headers, 'PhishingURLIP', 'Phishing URL/IP Ratio')  
    
    gen_data = [['Mar15','Apr15','May15'],[]]
    gen_data[1] = []
    for j in range(3):
        gen_data[1].append(round(float(data[j][3][1]) / float(data[j][3][3]),2))  
    generate_chart(gen_data, gen_headers, 'MalwareURLIP', 'Malware URL/IP Ratio')  
 
    

def generate_chart(data, headers, png_name, name, bar_mode='group'):
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
    chart_title = name
    if (len(data)==2 or bar_mode=='stack'):
        total_len = 10 if len(data[0]) > 10 else len(data[0])
        total = map(lambda x: int(x) if (type(x) is str) else x, data[1][:total_len])
        if bar_mode=='stack':
            for i in range(2, len(data)):
                total = map(sum, zip(total, map(int,data[i][:total_len])))
        layout = Layout(
            title=chart_title,
            font=Font(
                size=16
            ),
            barmode=bar_mode,
            annotations=[
                Annotation(
                    x=xi,
                    y=yi,
                    text=str(yi),
                    xanchor='center',
                    yanchor='bottom',
                    showarrow=False,
                ) for xi, yi in zip(data[0], total)
            ]
        )
    else:
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
    print_no_newline('  ' + png_name + '.png')
    download_png(plot_url, 'latex/' + png_name + '.png')    
    
# util function for printing to terminal without newline char 
def print_no_newline(text):
    sys.stdout.write('  ' + text + (' ' * (71 - len(text))))
    sys.stdout.flush()  
    
def download_png(url, output):
    r = requests.get(url + '.png', stream=True)
    if r.status_code == 200:
        dir = os.path.dirname(output)
        if not os.path.exists(dir): # Check that parent dir exists
            os.makedirs(dir)
        with open(output, 'w+b') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    print('[DONE]') 
   
if __name__ == "__main__":    
    main()    
 