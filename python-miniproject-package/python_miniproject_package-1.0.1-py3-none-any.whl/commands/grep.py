#grep 
def run(n, pattern, file_name):
    file_handle = open(file_name, 'r')
    all_lines = file_handle.readlines()
    file_handle.close()
    count = 0
    for line in all_lines:
        count = count+1
        if line.find(pattern) > -1:
            print(file_name+":"+str(count)+":"+" "+line)