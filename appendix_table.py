import csv
import os
import sys

def sanitize(str):
    '''Escapes special characters in LaTeX'''
    return str.replace('&', '\\&').replace('#','')

    
def table(data, headers, caption='', max_row=10):
    table_ltx = ''
    table_head = '\\begin{table}[!htbp]\n\\centering\n'
    if caption is not '':
        table_head += '\\caption{' + sanitize(caption) + '}'
    table_head += '\n\\begin{tabular}{' + (len(data) * 'l') + '} \\hline\n'
    for i in range(len(headers) - 1):
        table_head += '\\bf ' + sanitize(headers[i]) + ' & '
    table_head += '\\bf ' + sanitize(headers[len(headers) - 1]) + '\\\\\\hline\n'
    table_ltx += table_head
    table_head = table_head.replace(sanitize(caption), sanitize(caption + ' (cont.)'))
    max_lengths = [15,15,15,25,25]
    table_row = 0
    for i in range(max_row if max_row < len(data[0]) else len(data[0])):
        buffer = []
        if table_row >= 40 and data[0][i] is not '':
            table_ltx += '\\hline\n\\end{tabular}\n\\end{table}\n\\newpage' + table_head
            table_row = 0
        if not is_empty(reduce(lambda x,y:x+y, map(lambda z:z[i], data))):    
            for j in range(len(headers)):
                hold = string_length_split(data[j][i], max_lengths[j])
                if j == len(data) - 1:
                    table_ltx += sanitize(hold[0]) + '\\\\\n'
                    table_row += 1
                else:
                    table_ltx += sanitize(hold[0]) + '&'
                if hold != [' ']:
                    for k in range(1,len(hold)):
                        if k-1 >= len(buffer):
                            buffer.append([''] * len(data))
                        if (hold[k] != '' and hold[k] != ' '):
                            c = 0
                            while (buffer[c][j] is not ''):
                                c += 1
                            buffer[c][j] = sanitize(hold[k])
            for b in buffer:
                if not is_empty(b[0]+b[1]+b[2]+b[3]+b[4]):
                    table_ltx += reduce(lambda x,y: x+'&'+y, b) + '\\\\\n'
                    table_row += 1
    table_ltx += '\\hline\n\\end{tabular}\n\\end{table}\n'
    return table_ltx
           
           
def is_empty(str):
    if len(str) == 0:
        return True
    for i in range(len(str)):
        if str[i] is not ' ':
            return False
    return True
            
            
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
        if (word == 'l'):
            if (result[len(result)-1] is not ''):
                result.append('')
                count += 1
            result[count] += '\\tabitem '
            curr = max - 2
        elif (len(word) < curr):
            result[count] += word + ' '
            curr -= (len(word) + 1)
        else:
            result.append('')
            count += 1
            curr = max
            result[count] += word + ' '
            curr -= (len(word) + 1)
    return(filter(lambda x: x is not [],result))
    
    
def create_appendix_table():
    file_name = 'appendix.csv'
    if len(sys.argv) >= 2:
        file_name = argv[2]
        
    data = []
    headers = []
    
    # read csv file into list
    with open('appendix.csv') as csv_file:
        dreader = csv.DictReader(csv_file)
        headers = dreader.fieldnames
        for row in dreader:
            for i in range(len(headers)):
                if i >= len(data):
                    data.append([])
                data[i].append(row[headers[i]])
                
    # reduce data by whether first column is empty
    last = 0
    for i in range(len(data[0])):
        if data[0][i] == '':
            for j in range(1, len(data)):
                data[j][last] += ' ' + data[j][i]
                data[j][i] = ''
        else:
            last = i
            
    # generate the latex table 
    with open('appendix.ltx', 'w+') as f:
        f.write(table(data,headers,'Botnet Families',10000).replace(' & & & & \\\\', ''))
        
        
if __name__ == '__main__':
    create_appendix_table()
                
                