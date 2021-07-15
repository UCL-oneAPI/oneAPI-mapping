import difflib
from pathlib import Path


# load the file using Path, return the list of string
def load_file(file_path):
    file_context = Path(file_path)
    string_list = file_context.read_text()
    return string_list


# define the differ used
diff_module = difflib.Differ()
# use html differ to generate html diagram
html_diff = difflib.HtmlDiff()

# get the context of two files
dpct_version_string_list = load_file('main.dp.cpp')
manual_modified_string_list = load_file('main.cpp')
dpct_version_string_list = dpct_version_string_list.splitlines()
manual_modified_string_list = manual_modified_string_list.splitlines()

# using the differ to generate the "differ" collection
diff = difflib.context_diff(dpct_version_string_list, manual_modified_string_list)

# define the differ_collection
preprocessing_diff_collection = []
for line in diff:
    diff_item = str(line)
    preprocessing_diff_collection.append(diff_item)

# result_collection = ""
# for line in diff:
#     result_collection += str(line)
# print(result_collection.split('\n'))

#
# with open('htmlout.html','a+') as fo:
#     fo.write(html_diff.make_file(loads,mems))
#     fo.close()
