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
    up_snippets = ""
    below_snippets = ""

    result = []
    up = []
    below = []


    line_number = 0
    while line_number < len(s2):
        
        if "DPCT" in s2[line_number]:
            warning_description_start_flag = True
            up_snippets = s2[line_number-2]
            print("in it 3")
            print(up_snippets)
            up.append(up_snippets)
        if "*/" in s2[line_number] and warning_description_start_flag == True:
            print("in it 2")
            warning_description_end_flag = True
            line_number += 1
            continue
        if warning_description_end_flag == True and warning_description_start_flag == True:
            print("in it")
            single_snippets += str(s2[line_number])
            front_bracket_number = s2[line_number].count("{")
            back_bracket_number = s2[line_number].count("}")
            bracket_number += (front_bracket_number - back_bracket_number)
            if bracket_number == 0:
                result.append(single_snippets)
                single_snippets = ""
                warning_description_start_flag = False
                warning_description_end_flag = False
            below_snippets = s2[line_number+1] 
            print(below_snippets)
            below.append(below_snippets)
        line_number += 1

    print(result)
    return up,below


def file_preprocessing_afterChanged():

    f = load_file("main.cpp")
    s2 = f.readlines()

    bracket_stack = []
    code_snippets = []
    warning_description_start_flag = False
    warning_description_end_flag = False
    warning_content_start_flag = False
    warning_content_end_flag = False

    bracket_number = 0
    single_snippets = ""
    up,below = file_preprocessing()
    print("--------------------------------------------")
    print(up)
    print(below)
    
    



file_preprocessing_afterChanged()