import difflib
from pathlib import Path


def find_dpcpp():
    root = Path.cwd()
    dpcpp_dir = root/Path('dpcpp')
    dpct_dir = root/Path('dpct-version')
    for i in dpcpp_dir.rglob('*.dp.cpp'):
        dpcpp_path = str(i.parent)
        temp = i.stem
        fname = temp.split('.')[0]
        for j in dpct_dir.rglob('*.cpp'):
            if fname == j.stem:
                dpct_path = str(j.parent)
                generate_html(dpcpp_path+'/'+fname+'.dp.cpp', dpct_path+'/'+fname+'.cpp', fname)


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
    f = open(file, "r+", encoding='UTF-8')
    read = f.readlines()
    return read

find_dpcpp()
