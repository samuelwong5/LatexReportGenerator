import plotly.plotly as py
from plotly.graph_objs import *
from selenium import webdriver
from pyvirtualdisplay import Display
import csv, requests, shutil, os, sys, stat, Image

# returns filename from complete path
# strips path and extension
def get_file_name(file_path):
    strSplit = file_path.split('/')
    return (strSplit[len(strSplit) - 1]).split('.')[0]
    
def read_monthly_csv(file_paths):
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
    draw_monthly_chart(server_dis, server_dis_headers, 'ServerRelated', 'Server Related security events distribution','stack')
    
    gen_headers = ['Month','URL','Domain','IP']                
    gen_data = [['Mar15','Apr15','May15'],[],[],[]]
    for i in range(3):
        gen_data[i+1] = []
        for j in range(3):
            gen_data[i+1].append(data[j][1][i+1])
            
    draw_monthly_chart(gen_data, gen_headers, 'DefacementGen', 'Defacement General Statistics')
               
    gen_data = [['Mar15','Apr15','May15'],[],[],[]]
    for i in range(3):
        gen_data[i+1] = []
        for j in range(3):
            gen_data[i+1].append(data[j][2][i+1])  
    draw_monthly_chart(gen_data, gen_headers, 'PhishingGen', 'Phishing General Statistics')
           
    gen_data = [['Mar15','Apr15','May15'],[],[],[]]
    for i in range(3):
        gen_data[i+1] = []
        for j in range(3):
            gen_data[i+1].append(data[j][3][i+1])  
    draw_monthly_chart(gen_data, gen_headers, 'MalwareGen', 'Malware General Statistics')
    
    url_ip_headers = ['Month', 'URL/IP Ratio']
    gen_data = [['Mar15','Apr15','May15'],[]]
    gen_data[1] = []
    for j in range(3):
        gen_data[1].append(round(float(data[j][1][1]) / float(data[j][1][3]),2))  
    draw_monthly_chart(gen_data, gen_headers, 'DefacementURLIP', 'Defacement URL/IP Ratio')
    
    gen_data = [['Mar15','Apr15','May15'],[]]
    gen_data[1] = []
    for j in range(3):
        gen_data[1].append(round(float(data[j][2][1]) / float(data[j][2][3]),2))  
    draw_monthly_chart(gen_data, gen_headers, 'PhishingURLIP', 'Phishing URL/IP Ratio')  
    
    gen_data = [['Mar15','Apr15','May15'],[]]
    gen_data[1] = []
    for j in range(3):
        gen_data[1].append(round(float(data[j][3][1]) / float(data[j][3][3]),2))  
    draw_monthly_chart(gen_data, gen_headers, 'MalwareURLIP', 'Malware URL/IP Ratio')  
 
    

def draw_monthly_chart(data, headers, png_name, name, bar_mode='group'):
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
    download_png(plot_url, 'graphs/' + png_name + '.png')        
    
    
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
    download_png(plot_url, 'graphs/' + chart_title + '.png')      

    
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
         
# main function        
def main():
    # pie charts     
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
    print_no_newline('Downloading Google Charts...')
    while ("Done" not in driver.title):
        time.sleep(1);
    print_done()              
    print('  Trimming images...')
    for png_file in os.listdir(os.getcwd() + '/graphs'):
        print_no_newline("  " + png_file)
        png_trim(os.getcwd() + '/graphs/' + png_file)
        print_done()       
    driver.quit()
    display.stop()
    # bar charts
    print('Creating bar charts...')
    print('  Downloading bar charts...')
    bar_chart_max_bars = 10           # Number of bars in bar chart  
    bar_chart_dir = os.getcwd() + '/data/bar'
    for file in os.listdir(bar_chart_dir):
        draw_bar_chart(bar_chart_dir + '/' + file, bar_chart_max_bars)
    file_paths = ['HKSWROutput03/report/serverSummary.csv', 
                  'HKSWROutput04/report/serverSummary.csv',
                  'HKSWROutput/report/serverSummary.csv']
    read_monthly_csv(file_paths)
        
    
        
    
if __name__ == "__main__":    
    main()    