import difflib
from pathlib import Path


# load the file using Path, return the list of string
def load_file(file_path):
    file_context = Path(file_path)
    string_list = file_context.read_text()
    return string_list


def count_bracket(string_statement):
    front_bracket_number = string_statement.count("{")
    back_bracket_number = string_statement.count("}")
    bracket_count = front_bracket_number - back_bracket_number
    return bracket_count

def mapping_extraction(dpcpp_file_path, manual_file_path):
    # define the differ used
    diff_module = difflib.Differ()
    # use html differ to generate html diagram

    # get the context of two files
    # dpct_version_string_list = load_file('main.dp.cpp')
    # manual_modified_string_list = load_file('main.cpp')

    dpct_version_string_list = load_file(dpcpp_file_path)
    manual_modified_string_list = load_file(manual_file_path)
    dpct_version_string_list = dpct_version_string_list.splitlines()
    manual_modified_string_list = manual_modified_string_list.splitlines()

    # using the differ to generate the "differ" collection
    # diff = difflib.context_diff(dpct_version_string_list, manual_modified_string_list)
    diff = diff_module.compare(dpct_version_string_list, manual_modified_string_list)

    # define the differ_collection
    preprocessing_diff_collection = []
    for line in diff:
        diff_item = str(line)
        preprocessing_diff_collection.append(diff_item)

    # print the context of the differ
    for item in preprocessing_diff_collection:
        print(item)

    # define the flag will be used later
    warning_desc_start = False
    warning_desc_end = False

    dpct_version_snippets = []
    manual_modified_version_snippets = []
    warning_message_version_snippets = []
    dpct_brackets_num = 0
    manual_modified_brackets_num = 0

    dpct_code_snippet_string = ""
    manual_modified_code_snippet_string = ""

    # warning message
    warning_message = ""
    # use of detect warning message only record in one time
    w_massage_time = 0
    # warning detection: ensure there is no warning message followed
    # 0 = not have one  , >1 the number of warning message
    w_detect = 0

    # loop through all lines
    #for line in preprocessing_diff_collection:
    i = 0
    while i < len(preprocessing_diff_collection):
        line = preprocessing_diff_collection[i]
        i += 1
        # detect the warning description start


        if "/*" in line and "DPCT" in preprocessing_diff_collection[i]:
            warning_desc_start = True


        # detect the warning description end
        if "*/" in line and warning_desc_start == True:
            #w_detect += 1
            if "/*" not in preprocessing_diff_collection[i]:
                print("&&&&&&&&&&&")
                print(preprocessing_diff_collection[i])
                warning_desc_end = True
                continue  # jump into another loop

        # if "/*" in line and warning_desc_end == True:
        #     warning_desc_end = False
        #     print("In this if condition")
        #     continue

        # detect the warning context start
        if  warning_desc_start ==  True:
            prefix = line[0]
            if prefix == "-" and warning_desc_end == False:
                warning_message += (line[1:] + "\n")


            # if the prefix is " "  == this line shown in dpct version
            if prefix == "-" and warning_desc_end == True :
                # warning message
                if w_massage_time == 0:
                    warning_message_version_snippets.append(warning_message)
                    warning_message = ""
                    w_massage_time = 1


                dpct_brackets_num += count_bracket(line)
                dpct_code_snippet_string += (line[1:] + "\n")
                if dpct_brackets_num == 0 and line[-1] != "\\":
                    dpct_version_snippets.append(dpct_code_snippet_string)
                    dpct_code_snippet_string = ""
                    dpct_brackets_num = 0
                    # warning_desc_start = False
                    # warning_desc_end = False

            if prefix == "+":
                # print(count_bracket(line))
                manual_modified_brackets_num += count_bracket(line)
                manual_modified_code_snippet_string += (line[1:] + "\n")
                if manual_modified_brackets_num == 0 and line[-1] != "\\":
                    manual_modified_version_snippets.append(manual_modified_code_snippet_string)
                    manual_modified_code_snippet_string = ""
                    manual_modified_brackets_num = 0
                    # warning_desc_start = False
                    warning_desc_end = False

            # if the prefix is " "  == this line shown in both version
            if prefix == " " :
                dpct_brackets_num += count_bracket(line)
                manual_modified_brackets_num += count_bracket(line)
                dpct_code_snippet_string += (line[1:] + "\n")
                manual_modified_code_snippet_string += (line[1:] + "\n")
                if dpct_brackets_num == 0 and line[-2] != "\\":
                    dpct_version_snippets.append(dpct_code_snippet_string)
                    dpct_code_snippet_string = ""
                    dpct_brackets_num = 0
                    warning_desc_start = False
                    warning_desc_end = False

                if manual_modified_brackets_num == 0:
                    manual_modified_version_snippets.append(manual_modified_code_snippet_string)
                    manual_modified_code_snippet_string = ""
                    manual_modified_brackets_num = 0
                    warning_desc_start = False
                    warning_desc_end = False



    return dpct_version_snippets,manual_modified_version_snippets,warning_message_version_snippets

# change here!!!!! for testing !!!!!!
dpct_snippets_result, manual_snippets_result,warning_message_version_snippets = mapping_extraction('clenergy.dp.cpp', 'clenergy.cpp')
print(dpct_snippets_result,manual_snippets_result,warning_message_version_snippets)


'''
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
# diff = difflib.context_diff(dpct_version_string_list, manual_modified_string_list)
diff = diff_module.compare(dpct_version_string_list, manual_modified_string_list)

# define the differ_collection
preprocessing_diff_collection = []
for line in diff:
    diff_item = str(line)
    preprocessing_diff_collection.append(diff_item)

for item in preprocessing_diff_collection:
    print(item)

# define the flag will be used later
warning_desc_start = False
warning_desc_end = False

dpct_version_snippets = []
manual_modified_version_snippets = []
dpct_brackets_num = 0
manual_modified_brackets_num = 0

dpct_code_snippet_string = ""
manual_modified_code_snippet_string = ""

# loop through all lines
for line in preprocessing_diff_collection:
    # detect the warning description start
    if "DPCT" in line:
        warning_desc_start = True

    # detect the warning description end
    if "*/" in line and warning_desc_start == True:
        warning_desc_end = True
        continue  # jump into another loop

    # detect the warning context start
    if warning_desc_start == warning_desc_end == True:
        prefix = line[0]

        # if the prefix is " "  == this line shown in dpct version
        if prefix == "-":
            dpct_brackets_num += count_bracket(line)
            dpct_code_snippet_string += (line[1:]+"\n")
            if dpct_brackets_num == 0:
                dpct_version_snippets.append(dpct_code_snippet_string)
                dpct_code_snippet_string = ""
                dpct_brackets_num = 0
                # warning_desc_start = False
                # warning_desc_end = False

        if prefix == "+":
            print(count_bracket(line))
            manual_modified_brackets_num += count_bracket(line)
            manual_modified_code_snippet_string += (line[1:] + "\n")
            if manual_modified_brackets_num == 0:
                print("in it ")
                manual_modified_version_snippets.append(manual_modified_code_snippet_string)
                manual_modified_code_snippet_string = ""
                manual_modified_brackets_num = 0
                warning_desc_start = False
                warning_desc_end = False


        # if the prefix is " "  == this line shown in both version
        if prefix == " ":
            dpct_brackets_num += count_bracket(line)
            manual_modified_brackets_num += count_bracket(line)
            dpct_code_snippet_string += (line[1:]+"\n")
            manual_modified_code_snippet_string += (line[1:]+"\n")
            if dpct_brackets_num == 0:
                dpct_version_snippets.append(dpct_code_snippet_string)
                dpct_code_snippet_string = ""
                dpct_brackets_num = 0
                warning_desc_start = False
                warning_desc_end = False

            if manual_modified_brackets_num == 0:
                manual_modified_version_snippets.append(manual_modified_code_snippet_string)
                manual_modified_code_snippet_string = ""
                manual_modified_brackets_num = 0
                warning_desc_start = False
                warning_desc_end = False
'''

