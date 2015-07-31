import csv
import os
import sys

import requests
from plotly.graph_objs import *
import plotly.plotly as py
from pyvirtualdisplay import Display
from selenium import webdriver

import gchart


def read_csv(file, columns=[], max_row=-1):
    header = []
    data = []
    row_count = max_row
    with open(file) as csv_file:
        reader = csv.DictReader(csv_file)
        header = reader.fieldnames
        if columns == []:
            columns = range(len(header))
        data = [[],[]]
        for row in reader:
            for i in range(len(columns)):
                data[i].append(row[header[columns[i]]])
            row_count -= 1
            if row_count == 0:
                break
    return header, data
        
        
def plotly_download_png(url, output):
    if url == '':
        return
    r = requests.get(url + '.png', stream=True)
    if r.status_code == 200:
        dir = os.path.dirname(output)
        if not os.path.exists(dir): 
            os.makedirs(dir)
        with open(output, 'w+b') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    
    
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

    
def plot_line_chart(x_label, data, chart_title=''):
    data = Data([Scatter(x=x_label,y=data_array,mode='lines+markers',
                      name=data_name) for data_array, data_name in data])
    layout = Layout(title=chart_title)
    fig = Figure(data=data,layout=layout)
    return py.plot(fig, chart_title)
    

def sum_array(a, b):
    return map(lambda x:str(int(x[0])+int(x[1])), zip(a, b))   
    
    
def plot_bar_chart(x_label, data, chart_title='', bar_mode='group', annotations=True):
    print(chart_title)
    anno_data = [] 
    if bar_mode=='group' and annotations:
        # Previously calculated offsets for bar labels
        anno_offset = [(0,0), (-0.2,0.4), (-0.27,0.27)]
    
        # Calculating positions for annotations
        offset_array = []
        offset_base, offset_inc = anno_offset[len(data)-1]
        for i in range(len(data)):
            offset_array += map(lambda x: x+offset_base, range(len(data[0][0])))
            offset_base += offset_inc
        y_height = reduce(lambda x,y:x+y, map(lambda z:z[0], data), [])
        anno_data = zip(offset_array, y_height, y_height)
    elif bar_mode=='stack' and annotations:
        y_height = []
        anno_text = []
        for i in range(len(data)):
            y_height += reduce(lambda x,y:sum_array(x,y), map(lambda z:z[0], data[:i]), [])
            anno_text += data[i][0]
        anno_data = zip(range(len(data[0][0])) * len(data), y_height, anno_text)        
    bars = [Bar(x=x_label,y=data_array,name=data_name) for data_array, data_name in data]
    chart_data = Data(bars) 
    layout = Layout(
        title=chart_title,
        font=Font(
            size=16
        ),
        barmode=bar_mode,
        annotations=[Annotation(
            x=xi,
            y=yi,
            text=str(zi),
            xanchor='center',
            yanchor='bottom',
             showarrow=False,
        ) for xi, yi, zi in anno_data]
    )
    fig = Figure(data=chart_data,layout=layout)
    plot_url = py.plot(fig, chart_title)
    return plot_url

    
def create_qrtr_graphs():
    data_dir = 'QOutput/'
    output_dir = os.path.join(os.getcwd(), 'latex/')
    yymm = int(sys.argv[1])
    qrtr = yymm % 10
    year = (yymm - qrtr) / 100
    qrtr_label = map(lambda x: prev_qrtr(year, qrtr, x),
                     range(4,-1,-1))
    data_paths = map(lambda x: data_dir + x + '/report/', qrtr_label)
    qrtr_label = map(lambda x: '20' + str(int(x)/100) + ' Q' + str(int(x)%100),
                     qrtr_label)
    
    # Defacement, Phishing and Malware
    # Trend, URL/IP
    url_data = [[],[],[]]
    url_ip_col = [('Defacement', 1), ('Phishing', 2), ('Malware',3)]
    for type, index in url_ip_col:
        url_ip_unique_data = [[],[]]
        url_ip_ratio_data = [[]]
        for d in data_paths:
            _, data = read_csv(d + 'serverSummary.csv', columns=[index])
            url_count = data[0][1]
            ip_count = data[0][3]
            url_ip_ratio = round(float(url_count) / float(ip_count),2)
            url_ip_unique_data[0].append(url_count)
            url_ip_unique_data[1].append(ip_count)
            url_ip_ratio_data[0].append(str(url_ip_ratio))
        url_data[index-1] = url_ip_unique_data[0]
        plot_url = plot_bar_chart(qrtr_label, 
                       zip(url_ip_unique_data, ['Unique URL', 'Unique IP']), 
                       'Trend of ' + type + ' security events')  
        plotly_download_png(plot_url, output_dir + type + 'UniqueBar.png')        
        plot_url = plot_bar_chart(qrtr_label,
                       [(url_ip_ratio_data[0],'URL/IP ratio')], 
                       'URL/IP ratio of ' + type + ' security events')        
        plotly_download_png(plot_url, output_dir + type + 'RatioBar.png')                 
    
    # Botnet (C&C) Distribution and Trend
    cc_data = [[],[],[]]
    for d in data_paths:
        _, data = read_csv(d + 'C&CServers.csv', columns=[0,3]) 
        ip_list = []
        irc_count = 0
        http_count = 0
        for i in range(len(data[0])):
            ip = data[0][i]
            if ip not in ip_list:
                ip_list.append(ip)
                if data[1][i] == '-':
                    http_count += 1
                else:
                    irc_count += 1
        cc_data[0].append(str(irc_count))
        cc_data[1].append(str(http_count))
        cc_data[2].append(str(irc_count+http_count))
    plot_url = plot_bar_chart(qrtr_label,
                   zip(cc_data[0:2], ['IRC','HTTP']),
                   'Trend and Distribution of Botnet (C&Cs) security events',
                   'stack')
    plotly_download_png(plot_url, output_dir + 'BotnetCCDisBar.png')   
    plot_url = plot_bar_chart(qrtr_label,
                   [(cc_data[2], 'Botnet C&Cs')],
                   'Trend of Botnet (C&Cs) security events')  
    plotly_download_png(plot_url, output_dir + 'BotnetCCBar.png')
    
    # Unique Botnet (Bots) Trend
    bn_data = []
    for d in data_paths:
        _, data = read_csv(d + 'botnetDailyMax.csv', columns=[1]) 
        total_count = 0
        for i in range(len(data[0])):
            if data[0][i] is not '':
                total_count += int(data[0][i])
        bn_data.append(total_count)
    plot_url = plot_bar_chart(qrtr_label,
                   [(bn_data,'Botnet (Bots)')],
                   'Trend of Botnet (Bots) security events')
    plotly_download_png(plot_url, output_dir + 'BotnetBotsBar.png')   
           
    # Top 5 Botnets 
    top_bn_data = [[],[],[],[],[]]
    top_bn_name = []
    top_bn_curr = []
    _, data = read_csv(data_paths[len(data_paths)-1] + 'botnetDailyMax.csv', [0,1])
    for i in range(5):
        top_bn_name.append(data[0][i])
        top_bn_curr.append(data[1][i])
    for j in range(4):
        _, data = read_csv(data_paths[j] + 'botnetDailyMax.csv', [0,1]) 
        for i in range(len(data[0])):
            index = -1
            try: 
                index = top_bn_name.index(data[0][i])
                if index >= 0:
                    top_bn_data[index].append(data[1][i])
            except:
                index = -1
        for i in range(5):
            if len(top_bn_data[i]) <= j:
                top_bn_data[i].append('0')
    for i in range(5):
        top_bn_data[i].append(top_bn_curr[i])
    plot_url = plot_line_chart(qrtr_label,
                   zip(top_bn_data, top_bn_name),
                   'Trend of 5 Botnet Families in Hong Kong Network')      
    plotly_download_png(plot_url, output_dir + 'BotnetFamTopLine.png')   

    # Server-related Events
    plot_url = plot_bar_chart(qrtr_label,
                   zip(url_data, ['Defacement','Phishing','Malware hosting']),
                   'Trend and Distribution of server related security events',
                   'stack')
    plotly_download_png(plot_url, output_dir + 'ServerDisBar.png')   
    
    # Total Events
    url_data.append(bn_data)
    url_data.append(cc_data[2])
    serv_events = reduce(sum_array, url_data)
    plot_url = plot_bar_chart(qrtr_label,
                   [(serv_events, 'Unique security events')],
                   'Trend of Security events')      
    plotly_download_png(plot_url, output_dir + 'TotalEventBar.png')   


def test():
    data_dir = 'QOutput/'
    output_dir = os.path.join(os.getcwd(), 'latex/')
    yymm = int(sys.argv[1])
    print('start drive')
    gchart.set_input_dir('QOutput/' + str(yymm) + '/report/')
    display = Display(visible=0, size=(1024, 768))
    display.start()
    driver = webdriver.Firefox()
    driver.get('http://localhost:5000/graph/botnetDailyMax')
    print('Getting website...')
    print(driver.page_source)
    base = driver.find_element_by_id('png').text
    with open(output_dir + 'BotnetFamPie.png', 'w+b') as f:
        f.write(base[22:].decode('base64'))
  
    
if __name__ == '__main__':    
    #create_qrtr_graphs()
    test()
