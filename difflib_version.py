import difflib
from pathlib import Path

diff_module = difflib.Differ()
html_diff = difflib.HtmlDiff()


loads = ''
with open('main.dp.cpp','r') as load:
    loads = load.readlines()
    load.close()

mems = ''
with open('main.cpp', 'r') as mem:
    mems = mem.readlines()
    mem.close()

f1 = open("main.cpp",'r',encoding="UTF-8")
f2 = open("main.dp.cpp",'r',encoding="UTF-8")
contents1 = Path('main.cpp').read_text()
contents2 = Path('main.dp.cpp').read_text()


diff = difflib.context_diff(contents1.splitlines(),contents2.splitlines())

result_collection = []
for line in diff:
    result_collection.append(line)
print(diff)
#
# with open('htmlout.html','a+') as fo:
#     fo.write(html_diff.make_file(loads,mems))
#     fo.close()