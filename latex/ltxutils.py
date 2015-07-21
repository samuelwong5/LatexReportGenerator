import csv, os

def ltx_sanitize(str):
    return str.replace('&', '\\&').replace('#','')

def get_file_name(file_path):
    strSplit = file_path.split(os.sep)
    return (strSplit[len(strSplit) - 1]).split('.')[0]

def ltx_section(title, fltbarrier=True):
    if fltbarrier:
        return '\\FloatBarrier\n\\section{' + title + '}\n'
    return '\\section{' + title + '}'

def ltx_subsection(title):
    return '\\subsection{' + title + '}\n'
    
def ltx_subsubsection(title):
    return '\\subsubsection(' + title + ')\n'
    
def ltx_figure(img, caption='Default Caption', param='width=\\textwidth'):
    str = '\\begin{figure}[h]\n\\includegraphics['
    str += param + ']{' 
    str += img + '}\n'
    str += '\\caption{' + caption + '}\n\\end{figure}\n'
    return str
    
def ltx_table(file_path, max_row=10):
    data, headers = read_csv(file_path)
    file_name = get_file_name(file_path)
    ltx = '\\begin{table}[!htbp]\n\\centering\n\\caption{' + file_name + '}'
    ltx += '\n\\begin{tabular}{' + (len(data) * 'l') + '} \\hline\n'
    for i in range(len(headers) - 1):
        ltx += '\\bf ' + headers[i].replace('&', '\\&') + ' & '
    ltx += '\\bf ' + headers[len(headers) - 1].replace('&', '\\&') + '\\\\\\hline\n'
    for i in range(max_row):
        for j in range(len(data)-1):
            ltx += ltx_sanitize((data[j][i])[:(57-7*len(headers))]) + '&'
        ltx += ltx_sanitize((data[len(data)-1][i])[:15]) + '\\\\\n'
    ltx += '\\hline\n\\end{tabular}\n\\end{table}\n'
    return ltx
    #with open(os.getcwd() + os.sep + 'output' + os.sep + file_name + '.txt', 'w+') as f:
    #   f.write(ltx)

def ltx_newpage():
    return '\\newpage\n'

def read_csv(file_path):        
    # method scoped variables assigned in 'with' scope
    data = []
    headers = ['Rank']
    
    # reading from csv file
    with open(file_path) as csv_file:
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
    summ_param = 'height=6cm'
    pie_chart_trim_param = 'trim={4cm 8cm 4cm 5.5cm},clip,height=9cm'
    ltx = ''
    ltx += ltx_section(title)
    ltx += ltx_subsection('Summary')
    ltx += ltx_figure('placeholder', title + ' - General Statistics', summ_param)
    ltx += ltx_figure('placeholder', title + ' - URL/IP ratio', summ_param)
    ltx += ltx_newpage()
    ltx += ltx_subsection("TLD Distribution")
    ltx += ltx_figure(file_name, file_name + " - TLD Distribution", pie_chart_trim_param)
    ltx += ltx_table(input_dir + file_name + '.csv')
    return ltx

input_dir = ''
def main():
    global input_dir
    input_dir = 'input' + os.sep
    ltx = summary('Defacement', 'DefacementTld')
    ltx += summary('Phishing', 'PhishingTld')
    ltx += summary('Malware', 'MalwareTld')
    ltx += ltx_section('Botnet')
    ltx += ltx_subsection('Botnet- Bots')
    ltx += ltx_figure('listOfBotnets', 'Botnet Unique IP (Monthly Max Count)', 'trim={4cm 8cm 4cm 5.5cm},clip,height=9cm')
    ltx += ltx_table(input_dir + 'listOfBotnets.csv')
    with open(os.getcwd() + os.sep + 'output' + os.sep + 'latex.tex', 'w+') as f:
       f.write(ltx)    
    
if __name__ == "__main__":    
    main()    