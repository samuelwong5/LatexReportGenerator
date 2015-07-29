import ConfigParser
import csv
import io
import os 
import requests
import shutil
import sys
import stat

from plotly.graph_objs import *
import plotly.plotly as py
from pyvirtualdisplay import Display
from selenium import webdriver

import ltxutils
import report_csv_monthly
import gchart

# Global variables
config = []

def get_file_name(file_path):
    strSplit = file_path.split('/')
    return (strSplit[len(strSplit)-1]).split('.')[0]
    
# file_path: relative file path to .csv file
# max: optional maximum number of bars
# bar_mode: 'overlay', 'stack', 'group'
def draw_bar_chart(file_path, max=10, bar_mode='stack'):
    # method scoped variables assigned in 'with' scope
    data = []
    headers = []
    
    # reading from csv file
    with open(file_path) as csv_file:
        dreader = csv.DictReader(csv_file)
        headers = dreader.fieldnames
        for row in dreader:
            for i in range(len(headers)):
                if (headers[i] == 'Total'):
                    break
                if (len(data) < i + 1):
                    data.append([])
                if (i == 0):
                    data[0].append(row[headers[0]])
                else:
                    data[i].append(float(row[headers[i]]))
                    
    # converting raw data to plotly 'Bar' class
    bars = []
    for i in range(len(data[0])):
        if (len(data[0][i]) > 15): # Cut label length to not exceed boundaries
            data[0][i] = data[0][i][:13] + '...' 
            
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
    total_len = 10 if len(data[0]) > 10 else len(data[0])
    total = data[1][:total_len]
    for i in range(2, len(data)):
        total = map(sum, zip(total, data[i][:total_len]))
    if len(data) > 2:
        all_columns =  sum([(data[x][:10]) for x in range(1,len(data))],[])
        all_columns_height = list(all_columns)
        for i in range(len(all_columns_height) - 1, 9, -1):
            j = 10
            all_columns_height[i] *= 0.4
            while (i - j >= 0):
                all_columns_height[i] += all_columns_height[i-j]
                j += 10
        for i in range(0, 10 if 10 <= len(all_columns_height) else len(all_columns_height)):
            all_columns_height[i] /= 2
    else:
        all_columns = total[:10]
        all_columns_height = total[:10] 
        
    # misc. chart setup
    chart_data = Data(bars)
    chart_title = get_file_name(file_path)
    layout = Layout(
        title=chart_title,
        font=Font(
            size=16
        ),
        barmode=bar_mode,
        annotations=[Annotation(
            x=xi,
            y=zi,
            text=str(int(yi)),
            xanchor='center',
            yanchor='bottom',
            showarrow=False,
        ) for xi, yi, zi in filter(lambda x: x[1] > (total[0] / 8), zip(data[0][:10] * (len(data)), all_columns, all_columns_height))]
    )
    fig = Figure(data=chart_data,layout=layout)
    
    # plot and download chart
    plot_url = py.plot(fig, chart_title)
    print_no_newline('  ' + chart_title + '.png')
    download_png(plot_url, config['output_dir'] + chart_title + '.png')      

         
def download_png(url, output):
    r = requests.get(url + '.png', stream=True)
    if r.status_code == 200:
        dir = os.path.dirname(output)
        if not os.path.exists(dir): 
            os.makedirs(dir)
        with open(output, 'w+b') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        print_done()   

        
def print_no_newline(text):
    sys.stdout.write('  ' + text + (' ' * (71 - len(text))))
    sys.stdout.flush()  # Flush text to stdout without newline
    
    
def print_done():
    print('[DONE]')    

def format_month_str(x):
    if x <= 0:
        x += 12
    if x < 10:
        return '0' + str(x)    
    return str(x)

    
def parse_config():
    cfg = ConfigParser.ConfigParser(allow_no_value=True)
    cfg.read('config.cfg')
    data_folder = cfg.get('input','data')
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
        print('Invalid argument. Expected format: YYMM.\nExample: March 2014 -> 1403')
        sys.exit(1)
    file_paths = [data_folder + str(year) + format_month_str(month - 2) + '/report/',  
        data_folder + str(year) + format_month_str(month - 1) + '/report/',  # 1 month ago
        data_folder + str(year) + format_month_str(month) + '/report/'       # current month
        ]
    ltx_output = cfg.get('output','latex')
    global config
    config = {'yymm': yymm, 'year': year, 'month': month, 'file_paths':file_paths, 'output_dir': ltx_output}   

    
def create_bar_charts():
    # Create bar charts that use data from current month
    print('Creating bar charts...')
    print('  Downloading bar charts...')
    bar_chart_dir = os.path.join(os.getcwd(), config["file_paths"][2])
    bar_chart_csv = ['ISPServerAll',
                     'ISPAll',
                     'ISPBotnets']
    for file in bar_chart_csv:
        shutil.copyfile(bar_chart_dir + file + '.csv', bar_chart_dir + file + 'Pie.csv')
        draw_bar_chart(bar_chart_dir + file + '.csv')
        
    # Create bar charts that use data from multiple months
    report_csv_monthly.create_monthly_bar(config['file_paths'])
 
 
def create_pie_chart():
    print('Creating pie charts...')
    print_no_newline('Starting virtual display...')
    display = Display(visible=0, size=(1024, 768))
    display.start()
    print_done()
    print_no_newline('Starting Flask webserver...')
    gchart.set_input_dir(data_folder + str(year) + format_month_str(month) + '/report/')
    gchart.start_flask_process()
    print_done()
    print_no_newline('Initializing Selenium webdriver...')        
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
        print_no_newline('  ' + file + '.png')
        driver.get('http://localhost:5000/graph/' + file)
        base = driver.find_element_by_id('png').text
        # Decode Base64 string and save
        with open(config['output_dir'] + file + '.png', 'w+b') as f:
            f.write(base[22:].decode('base64'))
        print_done()           
    driver.quit()
    display.stop() 

    
def main():
    parse_config()
    create_bar_charts()
    create_pie_charts()
    ltxutils.create_report(config["file_paths"][2], config["file_paths"][1], ltx_output, config["yymm"])
    os.system('killall -I python')
        
    
if __name__ == "__main__":    
    main()    