from pathlib import Path

def load_file(file_path):
    f = open(file_path,"r+",encoding='UTF-8')
    return f

def file_preprocessing():
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
    for line in s2:
        if "DPCT" in line:
            warning_description_start_flag = True
            print("in it 3")
        if "*/" in line and warning_description_start_flag == True:
            print("in it 2")
            warning_description_end_flag = True
            continue
        if warning_description_end_flag == True and warning_description_start_flag == True:
            print("in it")
            single_snippets += str(line)
            front_bracket_number = line.count("{")
            back_bracket_number = line.count("}")
            bracket_number += (front_bracket_number - back_bracket_number)
            if bracket_number == 0:
                result.append(single_snippets)
                single_snippets = ""
                warning_description_start_flag = False
                warning_description_end_flag = False
    print(result)





file_preprocessing()