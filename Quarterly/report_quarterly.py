# -*- coding: utf-8 -*- 
import codecs
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
    print(chart_title)
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
            y_height += reduce(lambda x,y:sum_array(x,y), map(lambda z:z[0], data[:i]), [0] * len(data[0][0]))
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
    plot_url = py.plot(fig, chart_title, auto_open=False)
    return plot_url

    
def create_qrtr_graphs():
    data_dir = 'QOutput/'
    output_dir = os.path.join(os.getcwd(), 'latex/')
    if len(sys.argv) < 2:
        print('Missing parameter: YYQQ (Y=Year / Q=Quarter)')
        return -1
    yymm = int(sys.argv[1])
    if yymm < 1000:
        print('Invalid input. Expected format: YYQQ')
        return -1
    qrtr = yymm % 10
    if qrtr <= 0 or qrtr > 4:
        print('Invalid quarter. Accepted range: 0 < QQ <= 4')
        return -1
    year = (yymm - qrtr) / 100
    qrtr_label = map(lambda x: prev_qrtr(year, qrtr, x),
                     range(4,-1,-1))
    data_paths = map(lambda x: data_dir + x + '/report/', qrtr_label)
    qrtr_label = map(lambda x: '20' + str(int(x)/100) + ' Q' + str(int(x)%100),
                     qrtr_label)
    
    print('Generating Security Watch Report for ' + qrtr_label[4])
    
    print('Creating charts:')
    
    qrtr_bar = lambda x,y: plot_bar_chart(qrtr_label,x,y)
    
    # Defacement, Phishing and Malware
    # Trend, URL/IP
    url_data = [[],[],[]]
    url_ip_col = [('Defacement', 1, u'網頁塗改'), 
                  ('Phishing', 2, u'釣魚網站'), 
                  ('Malware',3,u'惡意程式寄存')]
    for type, index, type_c in url_ip_col:
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
        plot_url = qrtr_bar(zip(url_ip_unique_data, ['Unique URL', 'Unique IP']), 
                       'Trend of ' + type + ' security events')  
        plotly_download_png(plot_url, output_dir + type + 'UniqueBar.png')        
        plot_url = qrtr_bar([(url_ip_ratio_data[0],'URL/IP ratio')], 
                       'URL/IP ratio of ' + type + ' security events')        
        plotly_download_png(plot_url, output_dir + type + 'RatioBar.png')  
        plot_url = qrtr_bar(zip(url_ip_unique_data, ['唯一網址', '唯一IP']), 
                       type_c + u'安全事件趨勢')  
        plotly_download_png(plot_url, output_dir + type + 'UniqueBarChi.png')        
        plot_url = qrtr_bar([(url_ip_ratio_data[0],'唯一網址/IP比')], 
                       type_c + u'安全事件唯一網址/IP比')        
        plotly_download_png(plot_url, output_dir + type + 'RatioBarChi.png')         
    
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
                    zip(cc_data[0:2], ['IRC','HTTP']),
                   u'殭屍網絡控制中心安全事件的趨勢和分佈',
                   'stack')
    plotly_download_png(plot_url, output_dir + 'BotnetCCDisBarChi.png')  
    plot_url = qrtr_bar([(cc_data[2], 'Botnet C&Cs')],
                   'Trend of Botnet (C&C) security events')  
    plotly_download_png(plot_url, output_dir + 'BotnetCCBar.png')   
    plot_url = qrtr_bar([(cc_data[2], u'殭屍網絡控制中心(C&C)')],
                   u'殭屍網絡控制中心(C&C)安全事件趨勢')  
    plotly_download_png(plot_url, output_dir + 'BotnetCCBarChi.png')
    
    # Unique Botnet (Bots) Trend
    bn_data = []
    for d in data_paths:
        _, data = read_csv(d + 'botnetDailyMax.csv', columns=[1]) 
        total_count = 0
        for i in range(len(data[0])):
            if data[0][i] is not '':
                total_count += int(data[0][i])
        bn_data.append(total_count)
    plot_url = qrtr_bar([(bn_data,'Botnet (Bots)')],
                   'Trend of Botnet (Bots) security events')
    plotly_download_png(plot_url, output_dir + 'BotnetBotsBar.png')   
    plot_url = qrtr_bar([(bn_data,u'殭屍電腦')],
                   u'殭屍網絡(殭屍電腦)安全事件趨勢')
    plotly_download_png(plot_url, output_dir + 'BotnetBotsBarChi.png')          
           
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
    plot_url = plot_line_chart(qrtr_label,
                   zip(top_bn_data, top_bn_name),
                   u'五大主要殭屍網絡趨勢')      
    plotly_download_png(plot_url, output_dir + 'BotnetFamTopLineChi.png')   
    table_hdr = ['Name'] + qrtr_label
    table_top_bot = ''
    table_top_bot += '\\begin{table}[!htbp]\n\\centering\n'
    table_top_bot += '\n\\begin{tabular}{llllll} \\hline\n'
    table_top_bot += '&'.join(map(lambda x: '\\bf ' + x, table_hdr)) + '\\\\\\hline\n'
    rows = map(lambda x,y:x+'&'+'&'.join(y)+'\\\\\n', top_bn_name, top_bn_data)
    for row in rows:  
        table_top_bot += row     
    table_top_bot += '\\hline\n\\end{tabular}\n\\end{table}\n'            
    
    
    # Server-related Events
    plot_url = plot_bar_chart(qrtr_label,
                   zip(url_data, ['Defacement','Phishing','Malware hosting']),
                   'Trend and Distribution of server related security events',
                   'stack')
    plotly_download_png(plot_url, output_dir + 'ServerDisBar.png')   
    plot_url = plot_bar_chart(qrtr_label,
                   zip(url_data, [u'網頁塗改',u'釣魚網站',u'惡意程式寄存']),
                   u'與伺服器有關的安全事件的趨勢和分佈',
                   'stack')
    plotly_download_png(plot_url, output_dir + 'ServerDisBarChi.png')   

    # Total Events
    url_data.append(bn_data)
    url_data.append(cc_data[2])
    serv_events = reduce(sum_array, url_data)
    plot_url = qrtr_bar([(serv_events, 'Unique security events')],
                   'Trend of Security events')      
    plotly_download_png(plot_url, output_dir + 'TotalEventBar.png')   
    plot_url = qrtr_bar([(serv_events, u'唯一安全事件')],
                   u'安全事件趨勢')      
    plotly_download_png(plot_url, output_dir + 'TotalEventBarChi.png')   
    
    
    # Botnet Family Pie Chart (Google Charts)
    gchart.set_input_dir('QOutput/' + str(yymm) + '/report/')
    gchart.start_flask_process()
    display = Display(visible=0, size=(1024, 768))
    display.start()
    driver = webdriver.Firefox()
    driver.get('http://localhost:5000/graph/botnetDailyMax')
    with open('selenium_debug.html','w+') as f:
        f.write(driver.page_source.encode('utf-8'))
    base = driver.find_element_by_id('png').text
    with open(output_dir + 'BotnetFamPie.png', 'w+b') as f:
        f.write(base[22:].decode('base64'))
    gchart.stop_flask_process()
    
    headers, data = read_csv(data_paths[4] + 'botnetDailyMax.csv', [0,1])
    _, prev_data = read_csv(data_paths[3] + 'botnetDailyMax.csv', [0,1])
    rank_change = []
    pct_change = ['NA'] * 10
    for i in range(10):
        if data[0][i] == prev_data[0][i]:
            rank_change.append('$\\rightarrow$')        
        elif data[0][i] in prev_data[0][:i]:
            rank_change.append('$\\Downarrow$')
        elif data[0][i] in prev_data[0][i+1:]:
            rank_change.append('$\\Uparrow$')
        else:
            rank_change.append('NEW')
    for i in range(len(prev_data[0])):
        for j in range(10):
            if prev_data[0][i] == data[0][j]:
                new = float(data[1][j])
                old = float(prev_data[1][i])
                pct_change[j] = str(round((new - old) * 100 / old, 1)) + '\%'           
    headers = ['Rank', '$\\Uparrow\\Downarrow$', 'Concerned Bots', 'Number of Unique', 'Changes with']
    table_ltx = ''
    table_ltx += '\\begin{table}[!htbp]\n\\centering\n'
    table_ltx += '\\caption{Major Botnet Families in Hong Kong Networks}'
    table_ltx += '\n\\begin{tabular}{lllll} \\hline\n__HEADERS__\\\\\\hline\n'

    
    for i in range(len(data[0]) if len(data[0]) < 10 else 10):
        table_ltx += '&'.join([str(i), rank_change[i], data[0][i], data[1][i], pct_change[i]]) + '\\\\\n'      
    table_ltx += '\\hline\n\\end{tabular}\n\\end{table}\n'            
    ltx_temp = ''
    
    table_ltx_hdr_eng = '&'.join(map(lambda x:'\\bf ' + x,headers)) + '\\\\\n&&& \\bf IP addresses & \\bf previous period\\\\\hline\n'
    table_ltx_hdr_chi = u'\\bf 排名 & \\bf $\\Uparrow\\Downarrow$ & \\bf 殭屍網絡名稱 & \\bf 唯一IP地址 & \\bf 變化 \\\\\\hline\n'
    table_eng = table_ltx.replace('__HEADERS__', table_ltx_hdr_eng)
    table_chi = table_ltx.replace('__HEADERS__', table_ltx_hdr_chi)
    print(table_chi)
    
    # Output Latex
    with open(output_dir + 'report_quarterly_temp.tex') as f:
        ltx_temp = f.read()
    ltx_temp = ltx_temp.replace('botnet\\_table', table_eng)
    ltx_temp = ltx_temp.replace('QUARTER', qrtr_label[4])
    ltx_temp = ltx_temp.replace('UNIQUEEVENTS', serv_events[4])
    ltx_temp = ltx_temp.replace('table\\_top\\_bot', table_top_bot)
    with open(output_dir + 'SecurityWatchReport.tex', 'w+') as f:
        f.write(ltx_temp)
        
    with open(output_dir + 'report_qrtr_temp_chi.tex') as f:
        ltx_temp = f.read()
    ltx_temp = ltx_temp.replace('UNIQUEEVENTS', serv_events[4])
    ltx_temp = ltx_temp.replace('table\\_top\\_bot', table_top_bot)
    with open(output_dir + 'SecurityWatchReportChi.tex', 'w+') as f:
        f.write(ltx_temp)
    with codecs.open(output_dir + 'chiqrtr.tex', mode='w+', encoding='utf-8-sig') as f:
        f.write(u'20' + unicode(year) + u'第' + [u'一',u'二',u'三',u'四'][qrtr-1] + u'季度')
    with codecs.open(output_dir + 'botnetchitable.tex', mode='w+', encoding='utf-8-sig') as f:
        f.write(table_chi)
        
    print('Rendering PDF')
    os.chdir(output_dir)
    os.system('pdflatex SecurityWatchReport.tex')    
    os.rename('SecurityWatchReport.pdf', 
              'SecurityWatchReport' + qrtr_label[4] + '.pdf')  

    print('Report successfully compiled. Exiting now...')   
    os.system('xelatex SecurityWatchReportChi.tex')    
    os.rename('SecurityWatchReportChi.pdf', 
              'SecurityWatchReportChi' + qrtr_label[4] + '.pdf')  
    print('Report successfully compiled. Exiting now...')   
    
        
if __name__ == '__main__':    
    create_qrtr_graphs()
