import difflib

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

diff = diff_module.compare(loads,mems)
print('\n'.join(diff))

with open('htmlout.html','a+') as fo:
    fo.write(html_diff.make_file(loads,mems))
    fo.close()