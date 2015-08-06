import ConfigParser
import os 
import shutil
import sys

from pyvirtualdisplay import Display
from selenium import webdriver

import ltxutils
import report_csv_monthly
import report_utils as rutil
import gchart


# Global config dictionary
config = {}


def print_done():
    print('[DONE]')    
    
    
def format_month_str(y, x):
    if x <= 0:
        x += 12
        y -= 1
    y_str = str(y) if y >= 10 else '0' + str(y)
    if x < 10:
        return y_str + '0' + str(x)    
    return y_str + str(x)

    
def parse_config():
    cfg = ConfigParser.ConfigParser(allow_no_value=True)
    cfg.read('config.cfg')
    data_folder = cfg.get('monthly','input')
    if len(sys.argv) < 2:
        print ('[FATAL] Error: Missing YYMM argument.')
        sys.exit(1)
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
    ltx_output = cfg.get('monthly','output')
    plotly_cred = (cfg.get('plotly','username'), cfg.get('plotly','api_key'))
    rutil.plotly_init(plotly_cred)
    global config
    config = {'yymm': yymm, 'year': year, 'month': month, 'file_paths':file_paths, 'output_dir': ltx_output, 'plotly_cred': plotly_cred}   

    
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
    report_csv_monthly.create_monthly_bar(config)
 
 
def create_pie_charts():
    print('Creating pie charts...')
    rutil.print_no_newline('Starting virtual display...')
    display = Display(visible=0, size=(1024, 768))
    display.start()
    print_done()
    rutil.print_no_newline('Starting Flask webserver...')
    gchart.set_input_dir(config['file_paths'][2])
    gchart.start_flask_process()
    print_done()
    rutil.print_no_newline('Initializing Selenium webdriver...')        
    driver = webdriver.Firefox()
    print_done()
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
    for file in pie_chart_csv:
        rutil.print_no_newline(file + '.png')
        driver.get('http://localhost:5000/graph/' + file)
        base = driver.find_element_by_id('png').text
        # Decode Base64 string and save
        with open(config['output_dir'] + file + '.png', 'w+b') as f:
            f.write(base[22:].decode('base64'))
        print_done()           
    gchart.stop_flask_process()
    driver.quit()
    display.stop() 

    
def main():    
    parse_config()
    create_bar_charts()
    create_pie_charts()
    ltxutils.create_report(config["file_paths"][2], config["file_paths"][1], config['output_dir'], config["yymm"])
           
    
if __name__ == "__main__":    
    main()    