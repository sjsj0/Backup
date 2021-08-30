from datetime import datetime

filename = 'Test'
path = "test/path"
operation = 'Created'

def log_append(filename,operation,path):
    f = open("logFile.txt", "r")
    s1 = f.readlines()
    var ='\n'+ datetime.now().strftime("%Y-%m-%d %H:%M") + '\t|\t' + filename + '\t\t|\t' + operation + '\t|\t'+  path 
    s1.insert(1,var)
    f = open("logFile.txt", "w")
    f.writelines(s1)
    # f.seek(0)
    # f.write("\n{0}\t|\t{1}\t|\t{2}\t\t|\t{3}\t".format(datetime.now().strftime("%Y-%m-%d %H:%M"),filename,operation,path))
    f.close()

log_append(filename,operation,path)