import ConfigParser
import csv
import os 
import shutil
import sys

import ltxutils
import report_utils as rutil


# Global config dictionary
config = {}


def print_done():
    print('[DONE]')    
    
 
# Formats month string 
# Takes integer year, month into readable string (Apr15)
def fms(year, month):
    while month <= 0:
        month += 12
        year -= 1
    y_str = str(year) if year >= 10 else '0' + str(year)   # year 9 -> 09, 8 -> 08 ...
    return ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][month-1] + y_str  
    
    
def create_monthly_bar():
    file_paths = config['file_paths']
    year = config['year']
    month = config['month']
    months = [fms(year, month-2), fms(year, month-1), fms(year, month)]
    output_dir = config['output_dir']
    
    ssfiles = map(lambda x: x + 'serverSummary.csv', file_paths)
    create_server_summary(ssfiles, months, output_dir)
    
    bot_data = []   
    ccfiles = map(lambda x: x + 'C&CServers.csv', file_paths)
    for ccf in ccfiles:
        with open(ccf) as csv_file:
            dreader = csv.DictReader(csv_file)
            hold = []
            for row in dreader:
                if row['ip'] not in hold:
                   hold.append(row['ip'])        
            bot_data.append(len(hold))
    plot_url = rutil.plotly_bar_chart(months, [(bot_data, 'Botnet (C&C)s')], 'Botnet (C&Cs) security event distribution')
    rutil.plotly_download_png(plot_url, output_dir + 'BotCCDis.png')
    
    cc_data = [0,0,0]
    with open(ccfiles[2]) as csv_file:
        dreader = csv.DictReader(csv_file)
        hold = []
        for row in dreader:
            if row['ip'] not in hold:
                if row['channel'] == '-': #HTTP
                    cc_data[1] += 1 
                else:                     #IRC
                    cc_data[0] += 1  
                hold.append(row['ip'])   
    plot_url = rutil.plotly_bar_chart(['IRC', 'HTTP', 'P2P'], [(cc_data, 'Count')], 'Botnet (C&Cs) by communication type')
    rutil.plotly_download_png(plot_url, output_dir + 'BotCCType.png')

    bot_data = []
    bnfiles = map(lambda x: x + 'botnetDailyMax.csv', file_paths)
    for bnf in bnfiles:
        with open(bnf) as csv_file:
            dreader = csv.DictReader(csv_file)
            total_count = 0
            for row in dreader:
                if row['Count'] != '':
                    total_count += int(row['Count'])
            bot_data.append(total_count)
    plot_url = rutil.plotly_bar_chart(months,
                                      [(bot_data, 'Botnet (Bots)')],
                                      'Botnet (Bots) security event distribution')
    rutil.plotly_download_png(plot_url, output_dir + 'BotBotsDis.png')
      
      
def create_server_summary(file_paths, months, output_dir='latex/'):
    data = []
    for file in file_paths:
        _, csv_data = rutil.read_csv(file, [1,2,3])
        data.append(csv_data)
    server_dis_headers = ['Defacement','Phishing','Malware']                
    server_dis = [[],[],[]]
    for i in range(3):
        for j in range(3):
            server_dis[i].append(data[j][i][1])
    plot_url = rutil.plotly_bar_chart(months, 
                           zip(server_dis, server_dis_headers), 
                           'Server Related security events distribution', 
                           bar_mode='stack')
    rutil.plotly_download_png(plot_url, output_dir + 'ServerRelated.png')

    gen = [(1,'Defacement',config['defce_clr']),(2,'Phishing',config['phish_clr']),(3,'Malware',config['malwr_clr'])]
    gen_headers = ['URL','Domain','IP']                
    gen_data = [[],[],[]]
    for index, type, colors in gen:
        for i in range(3):
            gen_data[i] = []
            for j in range(3):
                gen_data[i].append(data[j][index-1][i+1])    
        plot_url = rutil.plotly_bar_chart(months,
                                          zip(gen_data, gen_headers),
                                          type + ' General Statistics', color=colors)
        rutil.plotly_download_png(plot_url, output_dir + type + 'Gen.png')
    
    url_ip_headers = ['URL/IP Ratio']

    for index, type, colors in gen:
        url_data = []
        for j in range(3):
            url_data.append(round(float(data[j][index-1][1]) / float(data[j][index-1][3]),2))  
        plot_url = rutil.plotly_bar_chart(months, [(url_data, 'URL/IP Ratio')], type + ' URL/IP Ratio', color=colors)
        rutil.plotly_download_png(plot_url, output_dir + type + 'URLIP.png')
  
  
def format_month_str(y, x):
    if x <= 0:
        x += 12
        y -= 1
    y_str = str(y) if y >= 10 else '0' + str(y)
    if x < 10:
        return y_str + '0' + str(x)    
    return y_str + str(x)

    
def parse_config():
    # File dependencies 
    required_files = ['footer.tex',
                      'header.tex',
                      'HKCERT.png']         
    
    cfg = ConfigParser.ConfigParser(allow_no_value=True)
    cfg.read('config.cfg')
    ltx_output = cfg.get('monthly','output')
    data_folder = cfg.get('monthly','input')
    if len(sys.argv) < 2:
        print ('[FATAL] Error: Missing YYMM argument.')
        sys.exit(1)
    if sys.argv[1] == '--clean':
        for file in os.listdir(ltx_output):
            if (not file in required_files) and os.path.isfile(ltx_output + file):
                os.remove(ltx_output + file)
        sys.exit(0)
    if len(sys.argv[1]) != 4:
        print('[FATAL] Error: Argument should be in format YYMM (e.g. 1403 for 2014 March)')
        sys.exit(1)
    yymm = 0
    year = 0
    month = 0
    try:
        yymm = int(sys.argv[1])
        month = yymm % 100
        year = (yymm-month) / 100
    except:
        print('Invalid argument. Expected format: YYMM (e.g. 1403 for 2014 March')
        sys.exit(1)
    file_paths = [data_folder + format_month_str(year, month - 2) + '/report/',  
        data_folder + format_month_str(year, month - 1) + '/report/',  # 1 month ago
        data_folder + format_month_str(year, month) + '/report/'       # current month
        ]
    plotly_cred = (cfg.get('plotly','username'), cfg.get('plotly','api_key'))
    rutil.plotly_init(plotly_cred)
    
    # Check file dependencies
    file_missing = False                      
    for req in map(lambda x: ltx_output + x, required_files):
        if not os.path.isfile(req):
            print('[FATAL] Missing file: ' + req)
            file_missing = True
    if file_missing:
        sys.exit('[FATAL] Please check the data path is correct in config.cfg')
        
    defce_clr = map(lambda x: x.replace('-',','), cfg.get('monthly','defce_colors').split(','))
    phish_clr = map(lambda x: x.replace('-',','), cfg.get('monthly','phish_colors').split(','))
    malwr_clr = map(lambda x: x.replace('-',','), cfg.get('monthly','malwr_colors').split(','))
    other_clr = map(lambda x: x.replace('-',','), cfg.get('monthly','other_colors').split(','))
    rutil.set_bar_deflt_colors(other_clr)
    global config
    config = {'yymm': yymm, 'year': year, 'month': month, 'file_paths':file_paths, 'output_dir': ltx_output, 'plotly_cred': plotly_cred,
              'defce_clr': defce_clr, 'phish_clr': phish_clr, 'malwr_clr': malwr_clr, 'other_clr': other_clr}   

    
def create_bar_charts():
    # Create bar charts that use data from current month
    print('Creating bar charts...')
    print('  Downloading bar charts...')
    bar_chart_dir = os.path.join(os.getcwd(), config["file_paths"][2])
    bar_charts = [('ISPServerAll', 'Top 10 ISPs by server related event types'),
                  ('ISPBotnets', 'Top 10 ISPs by non-server event type'),
                  ('ISPAll', 'Top 10 ISPs for all events')]
    for file, title in bar_charts:
        shutil.copyfile(bar_chart_dir + file + '.csv', bar_chart_dir + file + 'Pie.csv')
        header, data = rutil.read_csv(bar_chart_dir + file + '.csv', max_row=10)
        plot_url = rutil.plotly_bar_chart(data[0][:10], zip(data[1:], header[1:]), title, 'stack')
        rutil.plotly_download_png(plot_url, config['output_dir'] + file + '.png')

    # Create bar charts that use data from multiple months
    create_monthly_bar()
 
 
def create_pie_charts():
    pie_chart_csv = ['DefacementTld',
                     'ISPDefacement',
                     'ISPMalware',
                     'ISPPhishing',
                     'MalwareTld',
                     'PhishingTld',
                     'botnetDailyMax',
                     'ISPBotnetsPie',
                     'ISPServerAllPie',
                     'ISPAllPie']
    rutil.google_pie_chart(zip(pie_chart_csv, pie_chart_csv), config['file_paths'][2], config['output_dir'])
    
    
def main():    
    parse_config()
    create_bar_charts()
    create_pie_charts()
    ltxutils.create_report(config["file_paths"][2], config["file_paths"][1], config['output_dir'], config["yymm"])
           
    
if __name__ == "__main__":    
    main()    