import ConfigParser
import csv
import math
import os
import sys

import report_utils as rutil

class LatexDocument():
    def __init__(self):
        self.ltx = ''
        self.font = ''

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
        self.ltx += '\\caption{' + sanitize(caption) + '}\n\\label{fig:'+ img + '}\n\\end{figure}\n'
    
    # table with ranks and change
    def rc_table(self, file_path, dir, max_row=10):
        input_dir, prev_dir = dir
        csv_headers, csv_data = rutil.read_csv(input_dir + file_path)
        prev_headers, prev_data = rutil.read_csv(prev_dir + file_path)
    
        data, headers = calculate_rank_change([(csv_headers, csv_data),(prev_headers, prev_data)])
          
        file_name = get_file_name(file_path)
        self.table(data, headers, file_name)

    #default table
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
        for i in range(max_row if max_row < len(data[0]) else len(data[0])):
            buffer = []
            for j in range(len(headers)):
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
         
  
def calculate_rank_change(data):
    csv_headers, csv_data = data[0]
    prev_headers, prev_data = data[1]
    data = [[],[]]
    headers = ['Rank','+-']
      
    # add rank column (assumes csv is sorted)
    data[0] = map(str,range(1,len(csv_data[0])+1))

    # add change in rank wrt previous column
    total = 0
    data[1] = len(csv_data[0]) * ['NEW']
    min = lambda x,y: x if x < y else y
    for i in range(min(len(csv_data[0]), len(prev_data[0]))):
        count = csv_data[len(csv_data)-1][i]
        if count is not '':
            total += int(count)
        if csv_data[0][i] in prev_data[0][:i]:
            data[1][i] = '$\\Downarrow$'
        elif csv_data[0][i] == prev_data[0][i]:
            data[1][i] = '$\\rightarrow$'
        elif csv_data[0][i] in prev_data[0][i+1:]:
            data[1][i] = '$\\Uparrow$'
  
    data += csv_data
    headers += csv_headers
  
    # add change % wrt previous column
    percent_change = ['N/A'] * len(csv_data[0])
    if ('ISP' in csv_headers) or ('Botnet Family' in csv_headers):
        for i in range(len(prev_data[0])):
            for j in range(len(csv_data[0])):
                if prev_data[0][i] == csv_data[0][j]:
                    old = prev_data[1][i]
                    new = csv_data[1][j]
                    if (old != '') and (new != '') and (old != '0'):
                        percent_change[j] = str((int(new) - int(old)) * 100 / int(old))
                    break
        headers.append('+-\\%')
        data.append(percent_change)        
    
    # add percentages column
    percentages = []
    for i in range(len(data[0])):
        if csv_data[len(csv_data)-1][i] != '':
            percentages.append(str(int(csv_data[len(csv_data)-1][i]) * 100 / total))
    headers.append('Total\\%')
    data.append(percentages)
    
    return data, headers    

  
            
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
     
    
def summary(doc, title, file_name, dir_t):
    summ_param = 'height=8.5cm'
    pie_chart_trim_param = 'trim={4cm 8cm 4cm 5.5cm},clip,height=12cm'
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
    doc.text("\\subsection[TLD Distribution]{TLD Distribution{\\protect\\footnote{TLD Distribution - Top Level Domain Distribution of compromised machines which serve systems registered with a .hk top level domain, or whose network geolocation is Hong Kong.}}}\n")
    doc.figure(file_name, file_name + " - TLD Distribution", pie_chart_trim_param)
    doc.rc_table(file_name + '.csv', dir_t)

    
# util function for printing to terminal without newline char 
def print_no_newline(text):
    sys.stdout.write('  ' + text + (' ' * (71 - len(text))))
    sys.stdout.flush()     
    
 
def create_report(dir, prev_month_dir, output, yymm):
    isp_param = 'height=13cm' 
    pie_chart_trim_param = 'trim={4cm 8cm 4cm 5.5cm},clip,height=12cm'
    input_dir = dir
    prev_dir = prev_month_dir
    dir_t = (input_dir, prev_dir)
    report = LatexDocument()    
    print('Compiling LaTeX...')
    
    #header
    header = ''
    with open(output + 'header.tex') as f:
        header = f.read()
       
    fontcfg = ConfigParser.ConfigParser(allow_no_value=True)
    fontcfg.read('config.cfg')
    f = lambda x: fontcfg.get('font','font_' + x)
    header = header.replace('__FONT_SIZE__',f('size'))
    report.text(header.replace('__FONT__',f('family')))
    
    #sections 1-3
    print_no_newline('Section 1')
    summary(report, 'Defacement', 'DefacementTld', dir_t)
    report.newpage()
    print('[DONE]')
    print_no_newline('Section 2')
    summary(report, 'Phishing', 'PhishingTld', dir_t)
    report.newpage()
    print('[DONE]')
    print_no_newline('Section 3')
    summary(report, 'Malware', 'MalwareTld', dir_t)
    report.newpage()
    print('[DONE]')
    
    #section 4
    print_no_newline('Section 4')
    report.newpage()
    report.section('Botnet')
    report.subsection('Botnet - Bots')
    report.text('\\subsection[Major Botnet Families]{Major Botnet Families{\\protect\\footnote{Major Botnet Families are botnet families with security events report more than total of 20 counts monthly.}} found on Hong Kong Network}')
    report.figure('botnetDailyMax', 'Botnet Unique IP (Monthly Max Count)', 'trim={4cm 8cm 4cm 5.5cm},clip,height=8cm')
    report.rc_table('botnetDailyMax.csv', dir_t)
    report.newpage()
    report.subsection('Botnet - Command and Control Servers (C&Cs)')
    report.subsubsection('Botnet - C&C Servers by communication type')
    report.figure('BotCCType', 'Botnet - C&C Servers by communication type')
    print('[DONE]')
    
    #section 5
    print_no_newline('Section 5')
    report.newpage()
    report.section('Internet Service Providers (ISP)')  
    
    isp = ['Defacement', 'Phishing', 'Malware']
    for i in isp:
        report.subsection('Top 10 ISPs hosting ' + i)
        report.figure('ISP' + i, i + ' - Top ISPs', pie_chart_trim_param)
        report.rc_table('ISP' + i + '.csv', dir_t)
        report.newpage()
    
    report.subsection('Top 10 ISPs of unique botnets (Bots)')
    report.figure('ISPBotnetsPie', 'Botnet (Bots) - Top ISPs', pie_chart_trim_param)
    report.rc_table('ISPBotnets.csv', dir_t)
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
    
    isp_info = [('all security events', 'All Events', 'ISPAll')
               ,('server related security events', 'Server Related Events', 'ISPServerAll')]
    for i in isp_info:
        title = i[0]
        report.subsection('Top 10 ISPs for ' + i[0])
        report.figure(i[2] + 'Pie', i[1] + ' - Top ISPs', pie_chart_trim_param)
        isp_all_hdr, isp_all_data = rutil.read_csv(input_dir + i[2] + '.csv')
        headers_prev, data_prev = rutil.read_csv(prev_dir + i[2] + '.csv')
        data, headers = calculate_rank_change([(isp_all_hdr, isp_all_data), (headers_prev, data_prev)])
        
        report.table(data[:3] + data[len(data)-3:len(data)-1],
                     headers[:3] + headers[len(data)-3:len(data)-1], 'Top 10 ISPs for ' + title)
        report.newpage()
    
    report.subsection('Top 10 ISPs by event types')
    report.subsubsection('Non-server related event types')
    report.figure('ISPBotnets', 'Top 10 ISPs by non-server event type', isp_param)
    bot_hdr, bot_data = rutil.read_csv(input_dir + 'ISPBotnets.csv')
    report.table(bot_data[0:2], bot_hdr[0:2])
    report.newpage()
    report.subsubsection('Server related event types')
    report.figure('ISPServerAll', 'Top 10 ISPs by server related event types', isp_param)
    report.table(isp_all_data[0:5], isp_all_hdr[0:5])
    report.newpage()
    print('[DONE]')
    
    #appendix
    with open(output + 'footer.tex') as f:
        header = f.read()
        report.text(header)
   
    # replacing text (e.g. month) in latex file
    # parsing yymm into proper month year
    month_str = (['January','February','March',
                 'April','May','June',
                 'July','August','September',
                 'October','November','December'])[(yymm % 100) - 1] + ' 20' + str(int(yymm/100))
                 
    # calculating total unique event count
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
    
    
    # write to SecurityWatchReport.ltx
    fpath = output + 'SecurityWatchReport.tex'
    print_no_newline('Writing file: ' + fpath)
    report.write_to_file(fpath)   
    print('[DONE]')
    
    # Compile SecurityWatchReport.ltx to .pdf
    print('Rendering .pdf')
    os.chdir(os.path.join(os.getcwd(), output))
    os.system('pdflatex SecurityWatchReport.tex')    
    os.system('pdflatex SecurityWatchReport.tex')  # Second time to replace references and ToC
    os.rename('SecurityWatchReport.pdf', 
              'SecurityWatchReport' + str(yymm) + '.pdf')  
    print('Report successfully compiled. Exiting now...')
   
   
if __name__ == "__main__":    
    create_report(os.sep + 'HKSWROutput' + os.sep + 'report' + os.sep, 'latex/')    