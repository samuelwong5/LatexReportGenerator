import csv, os, sys, math

def string_length_split(str, max):
    str_split = str.split(' ')
    count = 0
    curr = max
    result = ['']
    for word in str_split:
        if (len(word) < curr):
            result[count] += word + ' '
            curr -= (len(word) + 1)
        else:
            result.append('')
            count += 1
            curr = max
            result[count] += word + ' '
            curr -= (len(word) + 1)
    return(result)

def ltx_sanitize(str):
    return str.replace('&', '\\&').replace('#','')

def get_file_name(file_path):
    strSplit = file_path.split(os.sep)
    return (strSplit[len(strSplit) - 1]).split('.')[0]

def ltx_section(title, fltbarrier=True):
    if fltbarrier:
        return '\\FloatBarrier\n\\section{' + ltx_sanitize(title) + '}\n'
    return '\\section{' + ltx_sanitize(title) + '}'

def ltx_subsection(title):
    return '\\subsection{' + ltx_sanitize(title) + '}\n'
    
def ltx_subsubsection(title):
    return '\\subsubsection{' + ltx_sanitize(title) + '}\n'
    
def ltx_figure(img, caption='Default Caption', param='width=\\textwidth'):
    str = '\\begin{figure}[h]\n\\centerline{\\includegraphics['
    str += param + ']{' 
    str += img + '}}\n'
    str += '\\caption{' + ltx_sanitize(caption) + '}\n\\end{figure}\n'
    return str
    
def ltx_table(file_path, max_row=10):
    data, headers = read_csv(file_path)
    file_name = get_file_name(file_path)
    ltx = '\\begin{table}[!htbp]\n\\centering\n\\caption{' + file_name + '}'
    ltx += '\n\\begin{tabular}{' + (len(data) * 'l') + '} \\hline\n'
    for i in range(len(headers) - 1):
        ltx += '\\bf ' + headers[i].replace('&', '\\&') + ' & '
    ltx += '\\bf ' + headers[len(headers) - 1].replace('&', '\\&') + '\\\\\\hline\n'
    buffer = ''
    max_len = 80
    for i in range(len(headers)):
        max_len -= len(headers[i])
    
    for i in range(max_row):
        for j in range(len(data)-1):
            hold = string_length_split(data[j][i], max_len)
            ltx += ltx_sanitize(hold[0]) + '&'
            for k in range(1,len(hold)):
                buffer += '&' + ltx_sanitize(hold[k]) + ('&'*(len(data)-2)) + '\\\\\n'
        ltx += ltx_sanitize((data[len(data)-1][i])[:15]) + '\\\\\n'
        ltx += buffer
        buffer = '' 
    ltx += '\\hline\n\\end{tabular}\n\\end{table}\n'
    return ltx
    #with open(os.getcwd() + os.sep + 'output' + os.sep + file_name + '.txt', 'w+') as f:
    #   f.write(ltx)

def ltx_newpage():
    return '\\FloatBarrier\n\\newpage\n'

def read_csv(file_path):        
    # method scoped variables assigned in 'with' scope
    data = []
    headers = ['Rank']
    
    # reading from csv file
    with open(os.getcwd() + os.sep + file_path) as csv_file:
        dreader = csv.DictReader(csv_file)
        headers += dreader.fieldnames
        total_count = 0
        row_count = 1
        for row in dreader:
            for i in range(len(headers)):
                if (len(data) < len(headers)):
                    data.append([])
                if (i == 0):
                    data[0].append(str(row_count))
                    row_count += 1
                elif (i==len(headers)-1):
                    if row[headers[i]] == '':
                        data[i].append(0)
                    else:
                        data[i].append(row[headers[i]])
                        total_count += int(row[headers[i]])                    
                else:
                    data[i].append(row[headers[i]])
    percentages = []
    for i in range(len(data[0])):
        percentages.append(str(int(data[len(data)-1][i]) * 100 / total_count))
    data.append(percentages)
    headers.append('\\%')
    return (data, headers)

def summary(title, file_name):
    title = ltx_sanitize(title)
    ltx = ''
    ltx += ltx_section(ltx_sanitize(title))
    ltx += ltx_subsection('Summary')
    ltx += ltx_figure(title + 'Gen', title + ' - General Statistics', summ_param)
    ltx += ltx_figure(title + 'URLIP', title + ' - URL/IP ratio', summ_param)
    ltx += ltx_newpage()
    ltx += ltx_subsection("TLD Distribution")
    ltx += ltx_figure(file_name, file_name + " - TLD Distribution", pie_chart_trim_param)
    ltx += ltx_table(input_dir + file_name + '.csv')
    return ltx

# util function for printing to terminal without newline char 
# util function for printing to terminal without newline char 
def print_no_newline(text):
    sys.stdout.write('  ' + text + (' ' * (71 - len(text))))
    sys.stdout.flush()     
    
# input directory for .csv files
input_dir = '' 

# standard latex options for figures
pie_chart_trim_param = 'trim={4cm 8cm 4cm 5.5cm},clip,height=12cm'
summ_param = 'height=8.5cm'
isp_param = 'height=13cm' 
       
def create_report(dir, output):
    global input_dir
    input_dir = dir
    
    #preamble
    #ltx = '\\documentclass[a4wide, 11pt]{article}\n\\usepackage{placeins}\n'
    #ltx += '\\usepackage[titletoc,toc,page]{appendix}\n\\usepackage{graphicx,hhline}\n'
    #ltx += '\\graphicspath{ {graphs/} }\n\\begin{document}\n'
    
    #sections 1-3
    print_no_newline('Section 1')
    ltx = summary('Defacement', 'DefacementTld')
    ltx += ltx_newpage()
    print('[DONE]')
    print_no_newline('Section 2')
    ltx += summary('Phishing', 'PhishingTld')
    ltx += ltx_newpage()
    print('[DONE]')
    print_no_newline('Section 3')
    ltx += summary('Malware', 'MalwareTld')
    ltx += ltx_newpage()
    print('[DONE]')
    
    
    #section 4
    print_no_newline('Section 4')
    ltx += ltx_newpage()
    ltx += ltx_section('Botnet')
    ltx += ltx_subsection('Botnet - Bots')
    ltx += ltx_subsubsection('Major Botnet Families found on Hong Kong Network')
    ltx += ltx_figure('listOfBotnets', 'Botnet Unique IP (Monthly Max Count)', 'trim={4cm 8cm 4cm 5.5cm},clip,height=8cm')
    ltx += ltx_table(input_dir + 'listOfBotnets.csv')
    ltx += ltx_newpage()
    ltx += ltx_subsection('Botnet - Command and Control Servers (C&Cs)')
    ltx += ltx_subsubsection('Botnet - C&C Servers by communication type')
    ltx += ltx_figure('placeholder', 'Botnet - C&C Servers by communication type')
    print('[DONE]')
    
    #section 5
    print_no_newline('Section 5')
    ltx += ltx_newpage()
    ltx += ltx_section('Internet Service Providers (ISP)')
    ltx += ltx_subsection('Top 10 ISPs hosting Defacement')
    ltx += ltx_figure('ISPDefacement', 'Defacement - Top ISPs', pie_chart_trim_param)
    ltx += ltx_table(input_dir + 'ISPDefacement.csv')
    ltx += ltx_newpage()
    ltx += ltx_subsection('Top 10 ISPs hosting Phishing')
    ltx += ltx_figure('ISPPhishing', 'Phishing - Top ISPs', pie_chart_trim_param)
    ltx += ltx_table(input_dir + 'ISPPhishing.csv')
    ltx += ltx_newpage()
    ltx += ltx_subsection('Top 10 ISPs hosting Malware')
    ltx += ltx_figure('ISPMalware', 'Malware Hosting - Top ISPs', pie_chart_trim_param)
    ltx += ltx_table(input_dir + 'ISPMalware.csv')
    ltx += ltx_newpage()
    ltx += ltx_subsection('Top 10 ISPs of unique botnets (Bots)')
    ltx += ltx_figure('ISPBotnets', 'Botnet (Bots) - Top ISPs', isp_param)
    ltx += ltx_table(input_dir + 'ISPBotnets.csv')
    ltx += ltx_newpage()
    ltx += ltx_subsection('Top 10 ISPs for all security events')
    ltx += ltx_figure('ISPAll', 'All Events - Top ISPs', isp_param)
    ltx += ltx_table(input_dir + 'ISPAll.csv')
    ltx += ltx_newpage()
    ltx += ltx_subsection('Top 10 ISPs for server related security events')
    ltx += ltx_figure('ISPServerAll', 'Server Related Events - Top ISPs', isp_param)
    ltx += ltx_table(input_dir + 'ISPServerAll.csv')  
    print('[DONE]')
    
    #end document
    #ltx += '\end{document}'
    
    #write to latex.ltx
    fpath = output + 'latex.tex'
    print_no_newline('Writing file: ' + fpath)
    with open(fpath, 'w+') as f:
       f.write(ltx)    
    print('[DONE]')
    
if __name__ == "__main__":    
    create_report(os.sep + 'HKSWROutput' + os.sep + 'report' + os.sep, 'latex/')    