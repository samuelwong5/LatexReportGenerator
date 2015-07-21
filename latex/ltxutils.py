import csv, os

def get_file_name(file_path):
    strSplit = file_path.split(os.sep)
    return (strSplit[len(strSplit) - 1]).split('.')[0]

def create_latex_table(data, headers, file_name):
    ltx = '\\begin{table}\n\\centering\n\\caption{' + file_name + '}'
    ltx += '\n\\begin{tabular}{' + (len(data) * 'l') + '} \\hline\n'
    for i in range(len(headers) - 1):
        ltx += '\\bf ' + headers[i].replace('&', '\\&') + ' & '
    ltx += '\\bf ' + headers[len(headers) - 1].replace('&', '\\&') + '\\\\\\hline\n'
    for i in range(15):
        for j in range(len(data)-1):
            ltx += (data[j][i])[:(57-7*len(headers))].replace('&', '\\&').replace('#','') + '&'
        ltx += (data[len(data)-1][i])[:15].replace('&', '\\&').replace('#','') + '\\\\\n'
    ltx += '\\hline\n\\end{tabular}\n\\end{table}'
    with open(os.getcwd() + os.sep + 'output' + os.sep + file_name + '.txt', 'w+') as f:
        f.write(ltx)


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
    
def main():
    for file in os.listdir(os.getcwd() + os.sep + 'input'):
        fpath = os.getcwd() + os.sep + 'input' + os.sep + file
        data, headers = read_csv(fpath)
        create_latex_table(data, headers, get_file_name(fpath))
    
if __name__ == "__main__":    
    main()    