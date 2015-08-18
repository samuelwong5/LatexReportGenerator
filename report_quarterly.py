# -*- coding: utf-8 -*- 
import codecs
import ConfigParser
import csv
import os
import sys

import report_utils as rutil


# Global config dictionary
config = {}


def parse_config():
    """
    Parses the config.cfg file and outputs it to the global
    python dictionary variable config.
    """
    global config
    cfg = ConfigParser.ConfigParser(allow_no_value=True)
    cfg.read('config.cfg')
    config = {key : cfg.get('quarterly',key) for key in ['input','output']}
    config.update({k:map(lambda x:x.replace('-',','),
                         cfg.get('quarterly',k).split(',')) 
                         for k in ['defce_color','phish_color','malwr_color','other_color']})
    rutil.set_bar_deflt_colors(config['other_color'])
    
    
def prev_qrtr(year, qrtr, offset=0):
    """
    Formats a given year and quarter to a YYQQ format 
    corresponding to the file system structure. 
    
    Arguments:
    year   -- the year the report is being generated for
    qrtr   -- the quarter the report is being generated for
    offset -- the offset to calculate the file paths for previous quarters
    """
    new_qrtr = qrtr
    new_year = year
    for i in range(offset):
        if new_qrtr == 1:
            new_qrtr = 4
            new_year -= 1
        else:
            new_qrtr -= 1
    return str(new_year).zfill(2) + str(new_qrtr).zfill(2)

    
def check_file_dependencies():
    """
    Checks whether the required file dependencies exist. 
    Cleans the output directory if --clean flag is received.
    Process configuration files.
    """
    # File dependencies
    required_files = ['report_qrtr_temp_chi.tex',
                      'report_quarterly_temp.tex',
                      'lightbulb.jpg',
                      'warning.png',
                      'HKCERT.png']   
                      
    if len(sys.argv) < 2:
        print('Missing parameter: YYQQ (Y=Year / Q=Quarter)')
        sys.exit()
    parse_config()
    input = config['input']
    output = os.path.join(os.getcwd(), config['output'])    
    config['output'] = output
    
    # Clean output_dir if --clean flag
    if sys.argv[1] == '--clean':
        for file in os.listdir(output):
            if not file in required_files and os.path.isfile(output + file):
                os.remove(output + file)
        sys.exit(0)
    yyqq = int(sys.argv[1])
    if yyqq < 1000:
        print('Invalid input. Expected format: YYQQ')
        sys.exit()
    qrtr = yyqq % 10
    if qrtr <= 0 or qrtr > 4:
        print('Invalid quarter. Accepted range: 0 < QQ <= 4')
        sys.exit()
          
    # Check file dependencies    
    file_missing = False                      
    for req in map(lambda x: config['output'] + x, required_files):
        if not os.path.isfile(req):
            print('[FATAL] Missing file: ' + req)
            file_missing = True
    if file_missing:
        sys.exit('[FATAL] Please check the data path is correct in config.cfg')
    
    year = (yyqq - qrtr) / 100
    qrtr_label = map(lambda x: prev_qrtr(year, qrtr, x),
                     range(4,-1,-1))
    data_paths = map(lambda x: input + x + '/report/', qrtr_label)
    qrtr_label = map(lambda x: '20' + str(int(x)/100) + ' Q' + str(int(x)%100),
                     qrtr_label)
    config['params'] = (yyqq, year, qrtr, qrtr_label, data_paths)
   
def quarterly_compile_data():
    yyqq, year, qrtr, qrtr_label, data_paths = config['params']
    global config
    # URL/IP data
    url_data = [[],[],[]]
    url_ip_col = [('Defacement', 1), 
                  ('Phishing', 2), 
                  ('Malware', 3)]
    for type, index in url_ip_col:
        url_ip_unique_data = [[],[]]
        url_ip_ratio_data = [[]]
        for d in data_paths:
            _, data = rutil.read_csv(d + 'serverSummary.csv', columns=[index])
            url_count = data[0][1]
            ip_count = data[0][3]
            url_ip_ratio = round(float(url_count) / float(ip_count),2)
            url_ip_unique_data[0].append(url_count)
            url_ip_unique_data[1].append(ip_count)
            url_ip_ratio_data[0].append(str(url_ip_ratio))
        url_data[index-1] = url_ip_unique_data[0]
        config[type + '_url_data'] = (url_ip_unique_data, url_ip_ratio_data)    
    config['url_data'] = list(url_data)
    
    # Botnet (C&C) Distribution and Trend data
    cc_data = [[],[],[]]
    for d in data_paths:
        _, data = rutil.read_csv(d + 'C&CServers.csv', columns=[0,3]) 
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
    config['cc_data'] = cc_data
    
    # Unique Botnet (Bots) Trend
    bn_data = []
    for d in data_paths:
        _, data = rutil.read_csv(d + 'botnetDailyMax.csv', columns=[1]) 
        total_count = 0
        for i in range(len(data[0])):
            if data[0][i] is not '':
                total_count += int(data[0][i])
        bn_data.append(total_count)
    config['bn_data'] = bn_data
    
    # Top Botnet data
    top_bn_data = [[],[],[],[],[]]
    top_bn_name = []
    top_bn_curr = []
    _, data = rutil.read_csv(data_paths[len(data_paths)-1] + 'botnetDailyMax.csv', [0,1])
    for i in range(5):
        top_bn_name.append(data[0][i])
        top_bn_curr.append(data[1][i])
    for j in range(4):
        _, data = rutil.read_csv(data_paths[j] + 'botnetDailyMax.csv', [0,1]) 
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
    config['top_bn'] = (top_bn_data, top_bn_name, top_bn_curr)
    
    url_data.append(bn_data)
    url_data.append(cc_data[2])
    config['serv_events'] = reduce(rutil.sum_array, url_data)
   
   
def quarterly_create_charts(params):
    """
    Generates charts for the quarterly security watch report 
    using Plotly and Google Charts.
    
    Arguments:
    param -- contains the year, quarter and misc data for 
             chart graphing
    """
    yyqq, year, qrtr, qrtr_label, data_paths = config['params']
    output = config['output']
    
    print('Generating Security Watch Report for ' + qrtr_label[4])
    print('Creating charts:')
    
    # Lambda function to use qrtr_labels as the labels for the x-axis
    qrtr_bar = lambda x,y: rutil.plotly_bar_chart(qrtr_label,x,y)
     
    
    # Defacement, Phishing and Malware Trend and URL/IP
    url_ip_col = [('Defacement', 1, u'網頁塗改',config['defce_color']), 
                  ('Phishing', 2, u'釣魚網站',config['phish_color']), 
                  ('Malware',3,u'惡意程式寄存',config['malwr_color'])]
    for type, index, type_c, clr in url_ip_col:
        url_ip_unique_data, url_ip_ratio_data = config[type + '_url_data']
        plot_url = rutil.plotly_bar_chart(qrtr_label, zip(url_ip_unique_data, ['Unique URL', 'Unique IP']), 
                       'Trend of ' + type + ' security events',color=clr)  
        rutil.plotly_download_png(plot_url, output + type + 'UniqueBar.png')        
        plot_url = rutil.plotly_bar_chart(qrtr_label, [(url_ip_ratio_data[0],'URL/IP ratio')], 
                       'URL/IP ratio of ' + type + ' security events',color=clr)        
        rutil.plotly_download_png(plot_url, output + type + 'RatioBar.png')  
        plot_url = rutil.plotly_bar_chart(qrtr_label, zip(url_ip_unique_data, ['唯一網址', '唯一IP']), 
                       type_c + u'安全事件趨勢',color=clr)  
        rutil.plotly_download_png(plot_url, output + type + 'UniqueBarChi.png')        
        plot_url = rutil.plotly_bar_chart(qrtr_label, [(url_ip_ratio_data[0],'唯一網址/IP比')], 
                       type_c + u'安全事件唯一網址/IP比',color=clr)        
        rutil.plotly_download_png(plot_url, output + type + 'RatioBarChi.png')         
    
    # Botnet (C&C) Distribution and Trend
    cc_data = config['cc_data']
    plot_url = rutil.plotly_bar_chart(qrtr_label,
                    zip(cc_data[0:2], ['IRC','HTTP']),
                   'Trend and Distribution of Botnet (C&Cs) security events',
                   'stack')
    rutil.plotly_download_png(plot_url, output + 'BotnetCCDisBar.png')                   
    plot_url = rutil.plotly_bar_chart(qrtr_label,
                    zip(cc_data[0:2], ['IRC','HTTP']),
                   u'殭屍網絡控制中心安全事件的趨勢和分佈',
                   'stack')
    rutil.plotly_download_png(plot_url, output + 'BotnetCCDisBarChi.png')  
    plot_url = qrtr_bar([(cc_data[2], 'Botnet C&Cs')],
                   'Trend of Botnet (C&C) security events')  
    rutil.plotly_download_png(plot_url, output + 'BotnetCCBar.png')   
    plot_url = qrtr_bar([(cc_data[2], u'殭屍網絡控制中心(C&C)')],
                   u'殭屍網絡控制中心(C&C)安全事件趨勢')  
    rutil.plotly_download_png(plot_url, output + 'BotnetCCBarChi.png')
    
    # Unique Botnet (Bots) Trend
    bn_data = config['bn_data']
    plot_url = qrtr_bar([(bn_data,'Botnet (Bots)')],
                   'Trend of Botnet (Bots) security events')
    rutil.plotly_download_png(plot_url, output + 'BotnetBotsBar.png')   
    plot_url = qrtr_bar([(bn_data,u'殭屍電腦')],
                   u'殭屍網絡(殭屍電腦)安全事件趨勢')
    rutil.plotly_download_png(plot_url, output + 'BotnetBotsBarChi.png')          
           
    # Top 5 Botnets 
    top_bn_data, top_bn_name, top_bn_curr = config['top_bn']
    plot_url = rutil.plotly_line_chart(qrtr_label,
                   zip(top_bn_data, top_bn_name),
                   'Trend of 5 Botnet Families in Hong Kong Network')      
    rutil.plotly_download_png(plot_url, output + 'BotnetFamTopLine.png')   
    plot_url = rutil.plotly_line_chart(qrtr_label,
                   zip(top_bn_data, top_bn_name),
                   u'五大主要殭屍網絡趨勢')      
    rutil.plotly_download_png(plot_url, output + 'BotnetFamTopLineChi.png')   
    
    # Server-related Events
    url_data = config['url_data']
    plot_url = rutil.plotly_bar_chart(qrtr_label,
                   zip(url_data, ['Defacement','Phishing','Malware hosting']),
                   'Trend and Distribution of server related security events',
                   'stack')
    rutil.plotly_download_png(plot_url, output + 'ServerDisBar.png')   
    plot_url = rutil.plotly_bar_chart(qrtr_label,
                   zip(url_data, [u'網頁塗改',u'釣魚網站',u'惡意程式寄存']),
                   u'與伺服器有關的安全事件的趨勢和分佈',
                   'stack')
    rutil.plotly_download_png(plot_url, output + 'ServerDisBarChi.png')   

    # Total Events

    serv_events = config['serv_events']
    plot_url = qrtr_bar([(serv_events, 'Unique security events')],
                   'Trend of Security events')      
    rutil.plotly_download_png(plot_url, output + 'TotalEventBar.png')   
    plot_url = qrtr_bar([(serv_events, u'唯一安全事件')],
                   u'安全事件趨勢')      
    rutil.plotly_download_png(plot_url, output + 'TotalEventBarChi.png')   
    
    # Botnet Family Pie Chart (Google Charts)
    rutil.google_pie_chart([('botnetDailyMax','BotnetFamPie')], 
                            data_paths[len(data_paths) - 1], 
                            output)               
                   
                   
def quarterly_latex():
    """
    Compiles the LaTeX report for the Quarterly Security
    Watch Report. Generates the LaTeX tables from reading
    CSV files; Uses template LaTeX report_qrtr_temp_chi
    and report_quarterly_temp and inserts the data 
    appropriately.
    
    Arguments:
    param -- contains the year, quarter and misc data for 
             report generation
    """
    
    yyqq, year, qrtr, qrtr_label, data_paths = config['params']
    output = config['output']
    
    # Top 5 Botnets Table
    top_bn_data, top_bn_name, _ = config['top_bn']
    table_hdr = ['Name'] + qrtr_label
    table_top_bot = ''
    table_top_bot += '\\begin{table}[!htbp]\n\\centering\n'
    table_top_bot += '\n\\begin{tabular}{llllll} \\hline\n'
    table_top_bot += '&'.join(map(lambda x: '\\bf ' + x, table_hdr)) + '\\\\\\hline\n'
    rows = map(lambda x,y:x+'&'+'&'.join(y)+'\\\\\n', top_bn_name, top_bn_data)
    for row in rows:  
        table_top_bot += row     
    table_top_bot += '\\hline\n\\end{tabular}\n\\end{table}\n'                        
                   
    # Generate latex table for Major Botnet Families
    headers, data = rutil.read_csv(data_paths[4] + 'botnetDailyMax.csv', [0,1])
    _, prev_data = rutil.read_csv(data_paths[3] + 'botnetDailyMax.csv', [0,1])
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

    # Major Botnet Families table headers            
    headers = ['Rank', '$\\Uparrow\\Downarrow$', 
               'Concerned Bots', 'Number of Unique', 
               'Changes with']
    table_ltx = ''
    table_ltx += '\\begin{table}[!htbp]\n\\centering\n'
    table_ltx += '\\caption{__CAPTION__}'
    table_ltx += '\n\\begin{tabular}{lllll} \\hline\n__HEADERS__\\\\\\hline\n'

    # Major Botnet Families table data
    for i in range(len(data[0]) if len(data[0]) < 10 else 10):
        table_ltx += '&'.join([str(i), rank_change[i], data[0][i], data[1][i], pct_change[i]]) + '\\\\\n'      
    table_ltx += '\\hline\n\\end{tabular}\n\\end{table}\n'            
    ltx_temp = ''
    
    # Create Chinese and English version of Major Botnet Families
    table_ltx_cap_eng = 'Major Botnet Families in Hong Kong Networks'
    table_ltx_cap_chi = u'香港網絡內的主要殭屍網絡'
    table_ltx_hdr_eng = '&'.join(map(lambda x:'\\bf ' + x,headers)) + '\\\\\n&&& \\bf IP addresses & \\bf previous period\n'
    table_ltx_hdr_chi = u'\\bf 排名 & \\bf $\\Uparrow\\Downarrow$ & \\bf 殭屍網絡名稱 & \\bf 唯一IP地址 & \\bf 變化 \n'
    table_eng = table_ltx.replace('__HEADERS__', table_ltx_hdr_eng)
    table_eng = table_eng.replace('__CAPTION__', table_ltx_cap_eng)
    table_chi = table_ltx.replace('__HEADERS__', table_ltx_hdr_chi)
    table_chi = table_chi.replace('__CAPTION__', table_ltx_cap_chi)
    
    # Compile Latex report
    serv_events = config['serv_events']
    with open(output + 'report_quarterly_temp.tex') as f:
        ltx_temp = f.read()
    fontcfg = ConfigParser.ConfigParser(allow_no_value=True)
    fontcfg.read('config.cfg')
    f = lambda x: fontcfg.get('font','font_' + x)
    ltx_temp = ltx_temp.replace('__FONT_SIZE__',f('size'))
    ltx_temp = ltx_temp.replace('__FONT__',f('family'))
    ltx_temp = ltx_temp.replace('botnet\\_table', table_eng)
    ltx_temp = ltx_temp.replace('QUARTER', qrtr_label[4])
    ltx_temp = ltx_temp.replace('UNIQUEEVENTS', serv_events[4])
    ltx_temp = ltx_temp.replace('table\\_top\\_bot', table_top_bot)
    with open(output + 'SecurityWatchReport.tex', 'w+') as f:
        f.write(ltx_temp)
        
    with open(output + 'report_qrtr_temp_chi.tex') as f:
        ltx_temp = f.read()
    ltx_temp = ltx_temp.replace('UNIQUEEVENTS', serv_events[4])
    ltx_temp = ltx_temp.replace('table\\_top\\_bot', table_top_bot)
    with open(output + 'SecurityWatchReportChi.tex', 'w+') as f:
        f.write(ltx_temp)
    with codecs.open(output + 'chiqrtr.tex', mode='w+', encoding='utf-8-sig') as f:
        f.write(u'20' + unicode(year) + u'第' + [u'一',u'二',u'三',u'四'][qrtr-1] + u'季度')
    with codecs.open(output + 'botnetchitable.tex', mode='w+', encoding='utf-8-sig') as f:
        f.write(table_chi)
        
    print('Rendering PDF')
    os.chdir(output)
    os.system('pdflatex SecurityWatchReport.tex')    
    os.system('pdflatex SecurityWatchReport.tex')   # Second time to replace references and ToC  
    os.rename('SecurityWatchReport.pdf', 
              'SecurityWatchReport' + qrtr_label[4] + '.pdf')  

    print('Report successfully compiled. Exiting now...')   
    os.system('xelatex SecurityWatchReportChi.tex')    
    os.system('xelatex SecurityWatchReportChi.tex') # Second time to replace references and ToC
    os.rename('SecurityWatchReportChi.pdf', 
              'SecurityWatchReportChi' + qrtr_label[4] + '.pdf')  
    print('Report successfully compiled. Exiting now...')                           
                  
                  
def create_quarterly_report():
    """
    Main function to create the quarterly security watch report.
    
    Flags:
    --clean
        Clears the latex output directory of all files except
        the file dependencies for report generation
    --latex-only
        Only compiles the latex report without replotting the 
        charts. REQUIRES THE GRAPHS TO BE PLOTTED PREVIOUSLY
    --graph-only
        Only generates the charts for the report without compiling
        the LaTeX pdf        
    """
    check_file_dependencies()
    quarterly_compile_data()
    if not '--latex-only' in sys.argv: quarterly_create_charts()
    if not '--graph-only' in sys.argv: quarterly_latex()
    
            
        
if __name__ == '__main__':    
    create_quarterly_report()
