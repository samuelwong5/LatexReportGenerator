import plotly.plotly as py
from plotly.graph_objs import *
from selenium import webdriver
from pyvirtualdisplay import Display
import csv, requests, shutil, os, sys, stat, Image
import ltxutils
import report_csv_monthly
import ConfigParser, io

# returns filename from complete path
# strips path and extension
def get_file_name(file_path):
    strSplit = file_path.split('/')
    return (strSplit[len(strSplit) - 1]).split('.')[0]
    
# file_path: relative file path to .csv file
# max: optional maximum number of bars
# bar_mode: 'overlay', 'stack', 'group'
def draw_bar_chart(file_path, max, bar_mode='stack'):
    # method scoped variables assigned in 'with' scope
    data = []
    headers = []
    
    # reading from csv file
    with open(file_path) as csv_file:
        dreader = csv.DictReader(csv_file)
        headers = dreader.fieldnames
        for row in dreader:
            for i in range(len(headers)):
                if (len(data) < len(headers)):
                    data.append([])
                if (i == 0):
                    data[0].append(row[headers[0]])
                else:
                    data[i].append(float(row[headers[i]]))
                    
    # converting raw data to plotly 'Bar' class
    bars = []
    for i in range(len(data[0])):
        if (len(data[0][i]) > 15):
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
                        
    # misc. chart setup
    chart_data = Data(bars)
    chart_title = get_file_name(file_path)
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
    print_no_newline('  ' + chart_title + '.png')
    download_png(plot_url, output_dir + chart_title + '.png')      

    
# url: html url to .png file
# output: output relative file location        
def download_png(url, output):
    r = requests.get(url + '.png', stream=True)
    if r.status_code == 200:
        dir = os.path.dirname(output)
        if not os.path.exists(dir): # Check that parent dir exists
            os.makedirs(dir)
        with open(output, 'w+b') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        print_done()   

        
# trim excess white borders from png files
def png_trim(file_name):
    os.chmod(file_name, 0o777)
    im = Image.open(file_name)
    im2 = im.crop((150,90,660,580))
    im2.save(file_name)
        
        
# util function for printing to terminal without newline char 
def print_no_newline(text):
    sys.stdout.write('  ' + text + (' ' * (71 - len(text))))
    sys.stdout.flush()     
    
    
# util function for printing "[DONE]" 
def print_done():
    print('[DONE]')    
         
output_dir = 'latex/'         
# main function        
def main():
    config = ConfigParser.ConfigParser(allow_no_value=True)
    config.read('config.cfg')
    file_paths = [config.get('input','fst-month'),  # 2 months ago
                  config.get('input','snd-month'),  # 1 month ago
                  config.get('input','thd-month')]  # current month
    ltx_output = config.get('output','latex')
    webserver = config.get('input','webserver')
    global output_dir
    output_dir = ltx_output
    # bar charts
    print('Creating bar charts...')
    print('  Downloading bar charts...')
    bar_chart_max_bars = 10           # Number of bars in bar chart  
    bar_chart_dir = os.getcwd() + os.sep + file_paths[2]
    for file in ['ISPServerAll.csv', 'ISPBotnets.csv', 'ISPAll.csv']:
        draw_bar_chart(bar_chart_dir + file, bar_chart_max_bars)
    report_csv_monthly.main(file_paths)
    
    # pie charts     
    google_chart_files = ['DefacementTld.csv',
                          'ISPDefacement.csv',
                          'ISPMalware.csv',
                          'ISPPhishing.csv',
                          'MalwareTld.csv',
                          'PhishingTld.csv',
                          'listOfBotnets.csv']
    for gc_file in google_chart_files:
        shutil.copyfile(file_paths[2] + gc_file, webserver + gc_file)
    print('Creating pie charts...')
    print_no_newline('Starting virtual display...')
    display = Display(visible=0, size=(1024, 768))
    display.start()
    print_done()
    print_no_newline('Initializing Selenium webdriver...')        
    driver = webdriver.Firefox()
    print_done()
    print_no_newline('Rendering Google Charts...')
    driver.get("http://localhost/graph.html")
    print_done() 
    print('Downloading Google Charts...')
    while ("Done" not in driver.title):
        time.sleep(1);
    for file in os.listdir(webserver + 'graphs/'):
        print_no_newline('  ' + file)
        shutil.copyfile(webserver + 'graphs/' + file, ltx_output + file)
        print_done()           
    driver.quit()
    display.stop()
    print('Compiling LaTeX...')
    ltxutils.create_report(file_paths[2], ltx_output)
    print('Rendering .pdf')
    os.chdir(os.getcwd() + os.sep + output_dir)
    os.system('pdflatex SecurityWatchReport.tex')
    print('Report successfully compiled. Exiting now...')
        
    
if __name__ == "__main__":    
    main()    