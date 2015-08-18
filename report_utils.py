import csv
import os
import sys

import requests
import plotly
from plotly.graph_objs import Annotation, Bar, Data, Figure, Font, Marker, Layout, Scatter
import plotly.plotly as py
from pyvirtualdisplay import Display
from selenium import webdriver

import report_gchart as gchart

bar_deflt_colors = []

def set_bar_deflt_colors(colors):
    """
    Sets the default color scheme for the Plotly
    bar charts. This color scheme will be used
    if the optional parameter is not used in
    plotly_bar_chart
    """
    global bar_deflt_colors
    bar_deflt_colors = colors

    
def read_csv(file, columns=[], max_row=-1):
    """
    Reads a csv file and returns a list of
    strings containing the data of each column.
    
    Arguments:
    file    -- path to the .csv file
    columns -- the columns to be read (default: all)
    max_row -- maximum rows to be read (default: all)
    """
    header = []
    data = []
    row_count = max_row
    with open(file) as csv_file:
        reader = csv.DictReader(csv_file)
        header = reader.fieldnames
        if columns == []:
            columns = range(len(header))
        for i in columns:
            data.append([])
        for row in reader:
            for i in range(len(columns)):
                data[i].append(row[header[columns[i]]])
            row_count -= 1
            if row_count == 0:
                break
    return header, data
        
  
def plotly_init(cred):
    """
    Initializes plotly API credentials. See config file.
    
    Arguments:
    cred -- tuple containing API username and key
    """
    usr, pwd = cred
    plotly.tools.set_credentials_file(username=usr, api_key=pwd)
        
        
def plotly_download_png(url, output):
    """
    Downloads a static .png representation
    of a Plotly chart.
    
    Arguments:
    url    -- return value of py.plot
    output -- output path for the image file
    """
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
        print('[DONE]')
    else:
        print('[FAIL]' )
    
    
def plotly_line_chart(x_label, data, chart_title=''):
    """
    Plots a line chart using the Plotly API.
    
    Arguments:
    x_label     -- labels for the x-axis
    data        -- a list of (data set, data set title)
    chart_title -- the above chart title (default: empty string)    
    """
    print_no_newline(chart_title)
    data = Data([Scatter(x=x_label,y=data_array,mode='lines+markers',
                      name=data_name) for data_array, data_name in data])
    layout = Layout(title=chart_title)
    fig = Figure(data=data,layout=layout)
    return py.plot(fig, chart_title, auto_open=False)
    
 
def plotly_bar_chart(x_label, data, chart_title='', bar_mode='group', color=[], annotations=True):
    """
    Plots a bar chart using the Plotly API.
    
    Arguments:
    x_label     -- labels for the x-axis
    data        -- a list of (data set, data set title)
    chart_title -- the above chart title (default: empty string)
    bar_mode    -- 'overlay', 'stack' or 'group' (default: 'group')
    color       -- the color schemes for the bar chart
    annotations -- turns on labels for the bars (default: on)
    """
    if color == []:
        color = bar_deflt_colors
    print_no_newline(chart_title)
    anno_data = [] 
    
    # Calculate annotations positions 
    if (bar_mode=='group' or len(data) == 1) and annotations:
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
        
        # Map the color scheme into the Plotly Bar object
        if color == []:
            bars = [Bar(x=x_label,y=data_array,name=data_name) for (data_array, data_name) in data]
        elif len(data) > 1:
            bars = [Bar(x=x_label,y=data_array,name=data_name,marker=Marker(color=clr)) for ((data_array, data_name), clr) in zip(data, color[:len(data)])]
        else:
            bars = [Bar(x=x_label,y=data_array,name=data_name,marker=Marker(color=color[:len(x_label)])) for (data_array, data_name) in data]
    elif bar_mode=='stack' and annotations:
        y_height = []
        anno_text = []
        for i in range(len(data)):
            y_height += reduce(lambda x,y:sum_array(x,y), map(lambda z:z[0], data[:i]), [0] * len(data[0][0]))
            anno_text += data[i][0]
        max_height = max(map(int, y_height)) / 6
        anno_data = filter(lambda x: int(x[2]) >= max_height, zip(range(len(data[0][0])) * len(data), y_height, anno_text))        
        if color == []:
            bars = [Bar(x=x_label,y=data_array,name=data_name) for (data_array, data_name) in data]
        else:
            bars = [Bar(x=x_label,y=data_array,name=data_name,marker=Marker(color=clr)) for ((data_array, data_name), clr) in zip(data, color[:len(data)])]       
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
    return py.plot(fig, chart_title, auto_open=False)   

def google_pie_chart(files, input_dir, output_dir):
    """
    Creates a pie chart using Google Charts API
    Uses Flask as a webserver and selenium as a browser
    to run the Google Charts JS API, converts the chart
    to a Base64 encoded string and then saves it as a 
    PNG file.
    
    Arguments:
    files      -- CSV filenames to be parsed and plotted
    input_dir  -- Location of the input data files
    output_dir -- Location where the PNG files should be saved
    """
    print('Creating pie charts...')
    print_no_newline('Starting virtual display...')
    display = Display(visible=0, size=(1024, 768))
    display.start()
    print('[DONE]')
    print_no_newline('Starting Flask webserver...')
    gchart.set_input_dir(input_dir)
    gchart.start_flask_process()
    print('[DONE]')
    try:
        print_no_newline('Initializing Selenium webdriver...')        
        driver = webdriver.Firefox()
        print('[DONE]')
        for url, file in files:
            print_no_newline(file)
            driver.get('http://localhost:5000/graph/' + url)
            png_encoded = driver.find_element_by_id('png').text
            with open(output_dir + file + '.png', 'w+b') as f:
                f.write(png_encoded[22:].decode('base64'))  # Strip header
            print('[DONE]')
        display.stop()
        driver.quit()
    finally:
        gchart.stop_flask_process()
    
    
def sum_array(fst, snd):
    """
    Utility function to sum two arrays by pairing
    elements of the same indexes.  
    
    Arguments:
    fst -- the first array to be summed
    snd -- the second array to be summed 
    """
    return map(lambda x,y:str(int(x)+int(y)), fst, snd)   
    
    
def print_no_newline(text, width=71, prespace=2):
    """
    Utility function to print text without newline
    
    Arguments:
    text  -- the text to be printed
    width -- total padding for text (default: 71)
    """
    len = width - reduce(lambda x,y: x + (1 if ord(y) < 128 else 2), text, 0)
    while len < 0:
        len += width
    sys.stdout.write((' ' * prespace) + text + (' ' * len))
    sys.stdout.flush()  
    