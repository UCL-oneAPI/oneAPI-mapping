from pathlib import Path

def load_file(file_path):
    f = open(file_path,"r+",encoding='UTF-8')
    return f

def dpct_file_processing():
    # f = load_file("main.dp.cpp")
    # for f in f.readlines():
    # file_path = "main.dp.cpp"
    # contents = Path(file_path).read_text()
    # s = contents.split('\n')

    f = load_file("main.dp.cpp")
    s2 = f.readlines()

    bracket_stack = []
    code_snippets = []
    warning_description_start_flag = False
    warning_description_end_flag = False
    warning_content_start_flag = False
    warning_content_end_flag = False

    bracket_number = 0
    single_snippets = ""
    result = []

    # define the preceding_line & subsequent_line
    preceding_line = ""
    subsequent_line = ""

    for line in s2:
        if "DPCT" in line:
            warning_description_start_flag = True

        if warning_description_end_flag == False:
            preceding_line = str(line)

        if "*/" in line and warning_description_start_flag == True:
            warning_description_end_flag = True
            continue
        if warning_description_end_flag == True and warning_description_start_flag == True:
            single_snippets += str(line)
            front_bracket_number = line.count("{")
            back_bracket_number = line.count("}")
            bracket_number += (front_bracket_number - back_bracket_number)
            if bracket_number == 0:
                result.append(single_snippets)
                single_snippets = ""
                warning_description_start_flag = False
                warning_description_end_flag = False
                print(preceding_line)
                print(manual_version_processing(preceding_line=preceding_line, subsequent_line=str(line)))
    print(result)


def manual_version_processing(preceding_line, subsequent_line):
    # flags define
    begain_flag = False
    Ending_flag = False

    f = load_file('main.cpp')
    output_result = ""
    for line in f.readlines():
        # stored the content
        if begain_flag == True:
            output_result += str(line)

        if line == preceding_line:
            begain_flag = True

        if line == subsequent_line:
            begain_flag = False

    return output_result









dpct_file_processing()