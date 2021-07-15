import difflib
from pathlib import Path


def generate_html(file1, file2, name):
    read1 = read_file(file1)
    read2 = read_file(file2)
    html_diff = difflib.HtmlDiff()
    with open(name+'.html', 'a+') as output:
        output.write(html_diff.make_file(read1, read2))
        output.close()
    Path('html_files').mkdir(parents=True, exist_ok=True)
    Path(name+'.html').rename('html_files/'+name+'.html')


def read_file(file):
    f = open(file,"r+",encoding='UTF-8')
    read = f.readlines()
    return read


generate_html('main.cpp', 'main.dp.cpp','main')
