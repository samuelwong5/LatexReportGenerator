import argparse
import ConfigParser
import csv
import os 
import shutil
import sys

import ltxutils
import report_utils as rutil


def print_done():
    """
    Utility function that prints '[DONE]'
    """
    print('[DONE]')    
      
      
def month_format(year, month):
    """
    Formats year and month to YYMM.
    Example: 9, 4 -> 0904
    """
    if month <= 0:
        month += 12
        year -= 1
    y_str = str(year) if year >= 10 else '0' + str(year)
    if month < 10:
        return y_str + '0' + str(month)    
    return y_str + str(month)

 
def month_string_format(year, month):
    """
    Formats the input to a string suitable for
    human input. Example: 1504 -> Apr15
    """
    while month <= 0:
        month += 12
        year -= 1
    y_str = str(year) if year >= 10 else '0' + str(year)   # year 9 -> 09, 8 -> 08 ...
    return ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][month-1] + y_str  
 
 
def monthly_create_multi_bar(config):
    """
    Creates the bar charts that uses data from
    multiple months.
    
    Arguments:
    config     -- configuration dictionary
    """
    file_paths = config['file_paths']
    year = config['year']
    month = config['month']
    months = [month_string_format(year, month-2), month_string_format(year, month-1), month_string_format(year, month)]
    output_dir = config['output_dir']
    
    ssfiles = map(lambda x: x + 'serverSummary.csv', file_paths)
    create_server_summary(ssfiles, config)
    
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
      
      
def create_server_summary(file_paths, config):
    """
    Creates the summary bar charts:
    Defacement/Phishing/Malware Summary/(URL/IP)
    
    Arguments:
    file_paths -- folder paths for the three months of csv files
    config     -- configuration dictionary
    """
    month = config['month']
    year = config['year']
    months = [month_string_format(year, month-2), month_string_format(year, month-1), month_string_format(year, month)]
    output_dir = config['output_dir']
    
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

    gen = [(1,'Defacement',config['defce_color']),(2,'Phishing',config['phish_color']),(3,'Malware',config['malwr_color'])]
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
  
def clean(ltx_output):
    """
    Cleans the output latex directory of all files except
    the required dependencies.
    """
    # File dependencies 
    required_files = ['footer.tex',
                      'header.tex',
                      'HKCERT.png']     
    for file in os.listdir(ltx_output):
        if (not file in required_files) and os.path.isfile(ltx_output + file):
            os.remove(ltx_output + file)
    sys.exit(0)
   
def parse_config():
    """
    Parses the config.cfg file and outputs it to the global
    python dictionary variable config.
    """
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument('-c', '--clean', action='store_true', help='Clean output folder of all files that are not dependencies.')
    g.add_argument('YYMM', nargs='?', type=int, action='store', help='Report month in YYMM format')
    h = parser.add_mutually_exclusive_group()
    h.add_argument('-l', '--latex-only', action='store_true', help='Only compiles the latex report without replotting charts. Note: Requires the charts to be generated previously.')
    h.add_argument('-g', '--graph-only', action='store_true', help='Only generates the charts for the report without compiling the LaTeX and PDF.')
    args = parser.parse_args(sys.argv[1:])
  
    # File dependencies 
    required_files = ['footer.tex',
                      'header.tex',
                      'HKCERT.png']         
    
    cfg = ConfigParser.ConfigParser(allow_no_value=True)
    cfg.read('config.cfg')
    ltx_output = cfg.get('monthly','output')
    data_folder = cfg.get('monthly','input')

    # Clean output folder if --clean flag
    if args.clean:
        clean(ltx_output)
        
    # Check arguments
    if args.YYMM < 1000 or args.YYMM > 10000 or args.YYMM % 100 > 12:
        print('[FATAL] Error: Argument should be in format YYMM (e.g. 1403 for 2014 March)')
        sys.exit(-1)
    try:
        yymm = args.YYMM
        month = yymm % 100
        year = (yymm-month) / 100
    except:
        print('[FATAL] Error: Invalid argument. Expected format: YYMM (e.g. 1403 for 2014 March')
        sys.exit(1)
    file_paths = [data_folder + month_format(year, month - 2) + '/report/',  
        data_folder + month_format(year, month - 1) + '/report/',  
        data_folder + month_format(year, month) + '/report/'       
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
    
    # Set global config   
    config = {'yymm': yymm, 'year': year, 'month': month, 'file_paths':file_paths, 'output_dir': ltx_output, 'plotly_cred': plotly_cred}
    config.update({k:map(lambda x:x.replace('-',','),
                         cfg.get('monthly',k).split(',')) 
                         for k in ['defce_color','phish_color','malwr_color','other_color']})
    rutil.set_bar_deflt_colors(config['other_color'])
    config['trim_config'] = (cfg.get('monthly', 'bar_chart').replace('-','='), cfg.get('monthly', 'pie_chart').replace('-','='))
    if args.latex_only:
        config['only'] = 'latex'
    elif args.graph_only:
        config['only'] = 'graph'
    else:
        config['only'] = 'all'
    return config
    
    
def monthly_create_bar_charts(config):
    """
    Create bar charts that use data from current month
    [N.B. Bar charts that use data from multiple months are generated
    in monthly_create_multi_bar]
    
    Arguments:
    config     -- configuration dictionary
    """
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
    monthly_create_multi_bar(config)
 
 
def monthly_create_pie_charts(config):
    """
    Creates the bar charts for the security watch report.
    Uses the Google Charts API.
    
    Arguments:
    config     -- configuration dictionary
    """
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
    rutil.google_pie_chart(zip(pie_chart_csv, pie_chart_csv), 
                           config['file_paths'][2], 
                           config['output_dir'])
    
    
def create_monthly_report():    
    """
    Main function to create the quarterly security watch report.
    
    Flags:
    --clean
        Clears the latex output directory of all files except
        the file dependencies for report generation
    --help
        Shows the usage and commands
    --latex-only
        Only compiles the latex report without replotting the 
        charts. REQUIRES THE GRAPHS TO BE PLOTTED PREVIOUSLY
    --graph-only
        Only generates the charts for the report without compiling
        the LaTeX pdf        
    """
    config = parse_config()       
    if config['only'] != 'latex': 
        monthly_create_bar_charts(config)    
        monthly_create_pie_charts(config)
    if config['only'] != 'graph': 
        ltxutils.create_report(config['file_paths'][2], 
                               config['file_paths'][1], 
                               config['output_dir'], 
                               config['yymm'],
                               config['trim_config'])
           
    
if __name__ == "__main__":    
    create_monthly_report()  