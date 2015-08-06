import csv

import report_utils as rutil
  
# Formats month string 
# Takes integer year, month into readable string (Apr15)
def fms(year, month):
    while month <= 0:
        month += 12
        year -= 1
    y_str = str(year) if year >= 10 else '0' + str(year)   # year 9 -> 09, 8 -> 08 ...
    return ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][month-1] + y_str  
    
def create_monthly_bar(config):
    # Parse configs
    file_paths = config['file_paths']
    year = config['year']
    month = config['month']
    months = [fms(year, month-2), fms(year, month-1), fms(year, month)]
    output_dir = config['output_dir']
    
    ssfiles = map(lambda x: x + 'serverSummary.csv', file_paths)
    create(ssfiles, months, output_dir)
    
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
      
      
def create(file_paths, months, output_dir='latex/'):
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

    gen = [(1,'Defacement'),(2,'Phishing'),(3,'Malware')]
    gen_headers = ['URL','Domain','IP']                
    gen_data = [[],[],[]]
    for index, type in gen:
        for i in range(3):
            gen_data[i] = []
            for j in range(3):
                gen_data[i].append(data[j][index-1][i+1])    
        plot_url = rutil.plotly_bar_chart(months,
                                          zip(gen_data, gen_headers),
                                          type + ' General Statistics')
        rutil.plotly_download_png(plot_url, output_dir + output_dir + type + 'Gen.png')
    
    url_ip_headers = ['URL/IP Ratio']

    for g in gen:
        index, type = g
        url_data = []
        for j in range(3):
            url_data.append(round(float(data[j][index-1][1]) / float(data[j][index-1][3]),2))  
        plot_url = rutil.plotly_bar_chart(months, [(url_data, 'URL/IP Ratio')], type + ' URL/IP Ratio')
        rutil.plotly_download_png(plot_url, output_dir + type + 'URLIP.png')
 
    
if __name__ == "__main__":    
    create_monthly_bar()
 