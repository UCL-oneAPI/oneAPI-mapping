from pathlib import Path


def load_file(file_path):
    f = open(file_path, "r+", encoding='UTF-8')
    return f


def mapping_extraction():
    # f = load_file("main.dp.cpp")
    # for f in f.readlines():
    # file_path = "main.dp.cpp"
    # contents = Path(file_path).read_text()
    # s = contents.split('\n')

    f = load_file("main.dp.cpp")
    lines_in_file = f.readlines()

    bracket_stack = []
    code_snippets = []
    warning_description_start_flag = False
    warning_description_end_flag = False
    warning_content_start_flag = False
    warning_content_end_flag = False

    bracket_number = 0
    single_snippets = ""
    up_snippets = ""
    below_snippets = ""

    result = []
    up = []
    below = []

    line_number = 0
    while line_number < len(lines_in_file):
        # count the numbers of the line in the file
        if "DPCT" in lines_in_file[line_number]:
            warning_description_start_flag = True

            # get the line before the code snippets
            up_snippets = lines_in_file[line_number - 2]
            print(up_snippets)
            up.append(up_snippets)

        # detect the the end of the warning description
        if "*/" in lines_in_file[
            line_number] and warning_description_start_flag == True:
            warning_description_end_flag = True
            line_number += 1
            # jump into the next loop
            continue

        # detect the beginning of the warning context
        if warning_description_end_flag == True and warning_description_start_flag == True:
            single_snippets += str(lines_in_file[line_number])
            front_bracket_number = lines_in_file[line_number].count("{")
            back_bracket_number = lines_in_file[line_number].count("}")
            bracket_number += (front_bracket_number - back_bracket_number)

            # detect the end of the warning context
            if bracket_number == 0:
                result.append(single_snippets)
                single_snippets = ""
                warning_description_start_flag = False
                warning_description_end_flag = False
            below_snippets = lines_in_file[line_number + 1]
            print(below_snippets)
            below.append(below_snippets)
            
        # loop through next line
        line_number += 1

    print(result)
    return up, below


def mapping_extraction_manual_modifications():
    f = load_file("main.cpp")
    lines_in_file = f.readlines()

    bracket_stack = []
    code_snippets = []
    warning_description_start_flag = False
    warning_description_end_flag = False
    warning_content_start_flag = False
    warning_content_end_flag = False

    bracket_number = 0
    single_snippets = ""
    up, below = mapping_extraction()
    print("--------------------------------------------")
    print(up)
    print(below)


mapping_extraction_manual_modifications()
