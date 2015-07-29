import csv
import math
import os
import sys

class LatexDocument():
    def __init__(self):
         self.ltx = ''

    def section(self, title, fltbarrier=True):
        if fltbarrier:
            self.ltx += '\\FloatBarrier\n\\section{' + sanitize(title) + '}\n'
        else:
            self.ltx += '\\section{' + sanitize(title) + '}'

    def subsection(self, title):
        self.ltx += '\\subsection{' + sanitize(title) + '}\n'
    
    def subsubsection(self, title):
        self.ltx += '\\subsubsection{' + sanitize(title) + '}\n'
    
    def figure(self, img, caption='Default Caption', param='width=\\textwidth'):
        self.ltx += '\\begin{figure}[h]\n\\centerline{\\includegraphics['
        self.ltx += param + ']{' 
        self.ltx += img + '}}\n'
        self.ltx += '\\caption{' + sanitize(caption) + '}\n\\end{figure}\n'
    
    def rc_table(self, file_path, max_row=10):
        data, headers = read_csv(input_dir + file_path)
        data_prev, headers_prev = read_csv(prev_dir + file_path)
        for i in range(10):
            if data[2][i] in data_prev[2][:i]:
                data[1][i] = '$\\Downarrow$'
            elif data[2][i] == data_prev[2][i]:
                data[1][i] = '$\\rightarrow$'
            elif data[2][i] in data_prev[2][i+1:]:
                data[1][i] = '$\\Uparrow$'
        file_name = get_file_name(file_path)
        self.table(data, headers, file_name)

    def table(self, data, headers, caption='', max_row=10):
        table_ltx = ''
        table_ltx += '\\begin{table}[!htbp]\n\\centering\n'
        if caption is not '':
            table_ltx += '\\caption{' + sanitize(caption) + '}'
        table_ltx += '\n\\begin{tabular}{' + (len(data) * 'l') + '} \\hline\n'
        for i in range(len(headers) - 1):
            table_ltx += '\\bf ' + sanitize(headers[i]) + ' & '
        table_ltx += '\\bf ' + sanitize(headers[len(headers) - 1]) + '\\\\\\hline\n'
        max_len = 80 # max width of table
        max_lengths = []
        for i in range(len(headers)):
            max_lengths.append(80-reduce(lambda x,y:x+y,map(lambda z:len(z), headers[:i] + headers[i+1:])))
        #print(data[0])
        #print(max_lengths)
        for i in range(max_row if max_row < len(data[0]) else len(data[0])):
            buffer = []
            for j in range(len(headers)):
                #print(str(len(data[j])) + '   i:' + str(i) +    '    j:' + str(j))
                hold = string_length_split(data[j][i], max_lengths[j])
                if j == len(data) - 1:
                    table_ltx += sanitize(hold[0]) + '\\\\\n'
                else:
                    table_ltx += sanitize(hold[0]) + '&'
                for k in range(1,len(hold)):
                    if k-1 <= len(buffer):
                        buffer.append([''] * len(data))
                    buffer[k-1][j] = sanitize(hold[k])
            for b in buffer:
                table_ltx += reduce(lambda x,y: x+'&'+y, b) + '\\\\\n'
        table_ltx += '\\hline\n\\end{tabular}\n\\end{table}\n'
        self.ltx += table_ltx
        
    def text(self, txt):
        self.ltx += txt
        
    def newpage(self):
        self.ltx += '\\FloatBarrier\n\\newpage\n'
      
    def replace(self, rep):
        for r in rep:
            self.ltx = self.ltx.replace(r[0], r[1])        
     
    def write_to_file(self, fpath):
        with open(fpath, 'w+') as f:
            f.write(self.ltx)
            
            
### Utility Methods ###            
def string_length_split(str, max):
    '''Splits a string into an array where each
       string is no longer than a given max length
    '''
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

def sanitize(str):
    '''Escapes special characters in LaTeX'''
    return str.replace('&', '\\&').replace('#','')

def get_file_name(file_path):
    '''Gets the file name from absolute/relative file path'''
    strSplit = file_path.split(os.sep)
    return (strSplit[len(strSplit) - 1]).split('.')[0]
            
def read_csv(file_path):        
    '''Reads a csv file and returns a tuple (headers, data)'''
    data = []
    headers = ['Rank','+-']
    
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
                elif (i==1):
                    data[1].append('NEW')
                elif (i==len(headers)-1):
                    if row[headers[i]] == '':
                        data[i].append(0)
                    else:
                        data[i].append(row[headers[i]])
                        total_count += int(row[headers[i]])                    
                else:
                    data[i].append(row[headers[i]])
    percent_change = ['N/A'] * 10
    percentages = []
    total_column_offset = 1
    with open(file_path.replace(input_dir, prev_dir)) as csv_file:
        dreader = csv.DictReader(csv_file)
        hdr = dreader.fieldnames
        if 'ISP' in hdr:
            total_column_offset += 1
            for row in dreader:
                for i in range(10):
                    if data[2][i] == row['ISP']:
                        old = int(row[hdr[len(hdr)-1]])
                        new = int(data[len(data)-1][i])
                        percent_change[i] = str((new - old) * 100 / old)
            #data.append(percent_change)
            headers.append('+-\\%')
    for i in range(len(data[0])):
        percentages.append(str(int(data[len(data)-1][i]) * 100 / total_count))
    if total_column_offset > 1:
        data.append(percent_change)
    data.append(percentages)
    headers.append('Total\\%')
    return (data, headers)

    
def summary(doc, title, file_name):
    title = sanitize(title)
    doc.section(sanitize(title))
    doc.subsection('Summary')
    if title == 'Defacement':
        doc.figure(title + 'Gen', title + 
                   ' - General Statistics{\\protect\\footnote{The data was adjusted to exlude non-confirmed defacement.}}', summ_param)
    else:
        doc.figure(title + 'Gen', title + ' - General Statistics', summ_param)
    doc.figure(title + 'URLIP', title + ' - URL/IP ratio', summ_param)
    doc.newpage()
    doc.subsection("TLD Distribution{\\protect\\footnote{TLD Distribution - Top Level Domain Distribution of compromised machines which serve systems registered with a .hk top level domain, or whose network geolocation is Hong Kong.}}")
    doc.figure(file_name, file_name + " - TLD Distribution", pie_chart_trim_param)
    doc.rc_table(file_name + '.csv')

    
# util function for printing to terminal without newline char 
# util function for printing to terminal without newline char 
def print_no_newline(text):
    sys.stdout.write('  ' + text + (' ' * (71 - len(text))))
    sys.stdout.flush()     
    
    
# input directory for .csv files
input_dir = '' 
prev_dir = ''
# standard latex options for figures
pie_chart_trim_param = 'trim={4cm 8cm 4cm 5.5cm},clip,height=12cm'
summ_param = 'height=8.5cm'
isp_param = 'height=13cm' 
    
       
def create_report(dir, prev_month_dir, output, yymm):
    global input_dir
    input_dir = dir
    global prev_dir
    prev_dir = prev_month_dir
    report = LatexDocument()    
    
    #header
    header = ''
    with open(output + 'header.tex') as f:
        header = f.read()
        report.text(header)

    #sections 1-3
    print_no_newline('Section 1')
    summary(report, 'Defacement', 'DefacementTld')
    report.newpage()
    print('[DONE]')
    print_no_newline('Section 2')
    summary(report, 'Phishing', 'PhishingTld')
    report.newpage()
    print('[DONE]')
    print_no_newline('Section 3')
    summary(report, 'Malware', 'MalwareTld')
    report.newpage()
    print('[DONE]')
    
    #section 4
    print_no_newline('Section 4')
    report.newpage()
    report.section('Botnet')
    report.subsection('Botnet - Bots')
    report.subsubsection('Major Botnet Families{\\protect\\footnote{Major Botnet Families are botnet families with security events report more than total of 20 counts monthly.}} found on Hong Kong Network')
    report.figure('listOfBotnets', 'Botnet Unique IP (Monthly Max Count)', 'trim={4cm 8cm 4cm 5.5cm},clip,height=8cm')
    report.rc_table('listOfBotnets.csv')
    report.newpage()
    report.subsection('Botnet - Command and Control Servers (C&Cs)')
    report.subsubsection('Botnet - C&C Servers by communication type')
    report.figure('BotCCType', 'Botnet - C&C Servers by communication type')
    print('[DONE]')
    
    #section 5
    print_no_newline('Section 5')
    report.newpage()
    report.section('Internet Service Providers (ISP)')
    report.subsection('Top 10 ISPs hosting Defacement')
    report.figure('ISPDefacement', 'Defacement - Top ISPs', pie_chart_trim_param)
    report.rc_table('ISPDefacement.csv')
    report.newpage()
    report.subsection('Top 10 ISPs hosting Phishing')
    report.figure('ISPPhishing', 'Phishing - Top ISPs', pie_chart_trim_param)
    report.rc_table('ISPPhishing.csv')
    report.newpage()
    report.subsection('Top 10 ISPs hosting Malware')
    report.figure('ISPMalware', 'Malware Hosting - Top ISPs', pie_chart_trim_param)
    report.rc_table('ISPMalware.csv')
    report.newpage()
    report.subsection('Top 10 ISPs of unique botnets (Bots)')
    report.figure('ISPBotnetsPie', 'Botnet (Bots) - Top ISPs', pie_chart_trim_param)
    report.rc_table('ISPBotnets.csv')
    report.newpage()
    report.subsection('Top 10 ISPs of Botnet C&Cs')
    with open(input_dir + 'C&CServers.csv') as f:
        headers = ['ISP','Channel','Port']
        data = [[],[],[]]
        dreader = csv.DictReader(f)
        fields = ['as_name','channel','port']
        for row in dreader:
            for i in range(3):
                data[i].append(row[fields[i]])
        report.table(data, headers, 'Botnet C&Cs')
        report.newpage()
    report.subsection('Top 10 ISPs for all security events')
    report.figure('ISPAllPie', 'All Events - Top ISPs', pie_chart_trim_param)
    isp_all_data, isp_all_hdr = read_csv(input_dir + 'ISPAll.csv')
    data_prev, headers_prev = read_csv(prev_dir + 'ISPAll.csv')
    for i in range(10):
        if isp_all_data[2][i] in data_prev[2][:i]:
            isp_all_data[1][i] = '$\\Downarrow$'
        elif isp_all_data[2][i] == data_prev[2][i]:
            isp_all_data[1][i] = '$\\rightarrow$'
        elif isp_all_data[2][i] in data_prev[2][i+1:]:
            isp_all_data[1][i] = '$\\Uparrow$'
    report.table(isp_all_data[:3] + isp_all_data[len(isp_all_data)-3:len(isp_all_data)-1],
                  isp_all_hdr[:3] + isp_all_hdr[len(isp_all_data)-3:len(isp_all_data)-1], 'Top 10 ISPs for all security events')
    report.newpage()
    report.subsection('Top 10 ISPs for server related security events')
    report.figure('ISPServerAllPie', 'Server Related Events - Top ISPs', pie_chart_trim_param)
    isp_all_data, isp_all_hdr = read_csv(input_dir + 'ISPServerAll.csv')
    data_prev, headers_prev = read_csv(prev_dir + 'ISPServerAll.csv')
    for i in range(10):
        if isp_all_data[2][i] in data_prev[2][:i]:
            isp_all_data[1][i] = '$\\Downarrow$'
        elif isp_all_data[2][i] == data_prev[2][i]:
            isp_all_data[1][i] = '$\\rightarrow$'
        elif isp_all_data[2][i] in data_prev[2][i+1:]:
            isp_all_data[1][i] = '$\\Uparrow$'
    report.table(isp_all_data[:3] + isp_all_data[len(isp_all_data)-3:len(isp_all_data)-1],
                 isp_all_hdr[:3] + isp_all_hdr[len(isp_all_data)-3:len(isp_all_data)-1], 'Top 10 ISPs for Server related security events')
    report.newpage()
    report.subsection('Top 10 ISPs by event types')
    report.subsubsection('Non-server related event types')
    report.figure('ISPBotnets', 'Top 10 ISPs by non-server event type', isp_param)
    bot_data, bot_hdr = read_csv(input_dir + 'ISPBotnets.csv')
    report.table(bot_data[2:4], bot_hdr[2:4])
    report.newpage()
    report.subsubsection('Server related event types')
    report.figure('ISPServerAll', 'Top 10 ISPs by server related event types', isp_param)
    report.table(isp_all_data[2:7], isp_all_hdr[2:7])
    report.newpage()
    print('[DONE]')
    
    #appendix
    with open(output + 'footer.tex') as f:
        header = f.read()
        report.text(header)
   
    # replacing text (e.g. month) in latex file
    month_str = (['January','February','March',
                 'April','May','June',
                 'July','August','September',
                 'October','November','December'])[(yymm % 100) - 1] + ' 20' + str(int(yymm/100))
    count = 0
    with open(input_dir + 'serverSummary.csv') as f:
        dreader = csv.DictReader(f)
        for row in dreader:
            if (count == 1):
                count = int(row['Defacement Count']) + int(row['Phishing Count']) + int(row['Malware Count']) 
                break
            count += 1            
    with open(input_dir + 'botnetDailyMax.csv') as f:
        dreader = csv.DictReader(f)
        for row in dreader:
            count += (0 if row['Count'] == '' else int(row['Count']))         
    with open(input_dir + 'C&CServers.csv') as f:
        dreader = csv.DictReader(f)
        unique = []
        for row in dreader:
            if row['ip'] not in unique:
                unique.append(row['ip'])
        count += len(unique)
    report.replace([('+-', '$\\Uparrow\\Downarrow$'),
                    ('__MONTH__', month_str),
                    ('__UNIQUEEVENT__',str(count))])
    
    
    #write to SecurityWatchReport.ltx
    fpath = output + 'SecurityWatchReport.tex'
    print_no_newline('Writing file: ' + fpath)
    report.write_to_file(fpath)   
    print('[DONE]')
    
    
if __name__ == "__main__":    
    create_report(os.sep + 'HKSWROutput' + os.sep + 'report' + os.sep, 'latex/')    