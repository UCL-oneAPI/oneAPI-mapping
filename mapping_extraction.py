import difflib
from pathlib import Path


# load the file using Path, return the list of string
def load_file(file_path):
    file_context = Path(file_path)
    string_list = file_context.read_text()
    return string_list


def warning_status_cache(l, a):
    l.insert(0, a)
    if len(l) > 2:
        l.pop()
    return l


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
    # for item in preprocessing_diff_collection:
    #     print(item)

    # define the flag will be used later
    warning_desc_start = False
    warning_desc_end = False

    # define flag for extraction complete
    dpct_extraction_complete = False
    manual_extraction_complete = False

    dpct_version_snippets = []
    manual_modified_version_snippets = []
    warning_message_version_snippets = []
    dpct_brackets_num = 0
    manual_modified_brackets_num = 0

    dpct_code_snippet_string = ""
    manual_modified_code_snippet_string = ""

    # warning message
    warning_message = ""
    warning_status = []
    warning_desc_start_copy, warning_des_end_copy = False, False
    # used to record the last time flag
    warning_flag_cache = [0] * 2

    # use of detect warning message only record in one time
    w_massage_time = 0
    # warning detection: ensure there is no warning message followed
    # 0 = not have one  , >1 the number of warning message
    w_detect = 0

    before_mark = ""
    after_mark = ""

    # loop through all lines
    # for line in preprocessing_diff_collection:
    i = 0
    while i < len(preprocessing_diff_collection):
        line = preprocessing_diff_collection[i]
        i += 1
        # detect the warning description start

        if "/*" in line and "DPCT" in preprocessing_diff_collection[i]:
            warning_desc_start = True
            before_mark = preprocessing_diff_collection[i - 2]

            manual_extraction_complete, dpct_extraction_complete = False, False

        # detect the warning description end
        if "*/" in line and warning_desc_start == True:
            # w_detect += 1
            if "/*" not in preprocessing_diff_collection[i]:
                warning_desc_end = True
                continue  # jump into another loop

        # detect the warning context start
        if warning_desc_start == True:
            # print("line:",line," i:",i)
            prefix = line[0]
            if prefix == "-":
                # if warning_desc_end == False:
                #    warning_message += (line[1:] + "\n")
                #    w_massage_time = 0

                # if the prefix is " "  == this line shown in dpct version
                if warning_desc_end == True:
                    # warning message
                    # if w_massage_time == 0:
                    #    warning_message_version_snippets.append(warning_message)
                    #    warning_message = ""
                    #    w_massage_time = 1

                    dpct_brackets_num += count_bracket(line)
                    dpct_code_snippet_string += (line[1:] + "\n")

                    if dpct_extraction_complete == True and dpct_brackets_num == 0:
                        manual_modified_version_snippets.append("")
                        # warning_desc_end = False

                        manual_extraction_complete = True

                    if dpct_brackets_num == 0 and line[-1] != "\\":
                        dpct_version_snippets.append(dpct_code_snippet_string)
                        dpct_code_snippet_string = ""
                        dpct_brackets_num = 0

                        # new added
                        after_mark = preprocessing_diff_collection[i]
                        dpct_extraction_complete = True
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

                    # warning_desc_end = False

                    # set extraction complete flag
                    manual_extraction_complete = True

            # if the prefix is " "  == this line shown in both version
            if prefix == " ":
                dpct_brackets_num += count_bracket(line)
                manual_modified_brackets_num += count_bracket(line)
                dpct_code_snippet_string += (line[1:] + "\n")
                manual_modified_code_snippet_string += (line[1:] + "\n")
                if dpct_brackets_num == 0 and line[-2] != "\\" and line[1:] != ' ':
                    dpct_version_snippets.append(dpct_code_snippet_string)
                    dpct_code_snippet_string = ""
                    dpct_brackets_num = 0

                    # warning_desc_start = False
                    # warning_desc_end = False
                    dpct_extraction_complete = True

                if manual_modified_brackets_num == 0 and line[1:] != ' ':
                    manual_modified_version_snippets.append(manual_modified_code_snippet_string)
                    manual_modified_code_snippet_string = ""
                    manual_modified_brackets_num = 0

                    # warning_desc_start = False
                    # warning_desc_end = False

                    manual_extraction_complete = True

        # if manual_extraction_complete == dpct_extraction_complete == True:
        if dpct_extraction_complete == True and manual_extraction_complete == True:
            warning_desc_start = False
            warning_desc_end = False

            # warning_des_end_copy, warning_desc_start_copy = False,False
    # print(len(dpct_version_snippets),"----",len(manual_modified_version_snippets))
    return dpct_version_snippets, manual_modified_version_snippets, warning_message_version_snippets
