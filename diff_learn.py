import difflib

diff_module = difflib.Differ()

file1 = open('main.cpp','r',encoding='UTF-8')
file2 = open('main.dp.cpp','r',encoding='UTF-8')

for line in diff_module.compare(file1.readlines(),file2.readlines()):
    print(line)