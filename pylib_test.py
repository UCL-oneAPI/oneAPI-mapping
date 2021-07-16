import difflib
import sys
import argparse


def read_file(file_name):
    try:
        file_desc = open(file_name, 'r')
        text = file_desc.read().splitlines()
        file_desc.close()
        return text
    except IOError as error:
        print 'Read input file Error: {0}'.format(error)
        sys.exit()



def compare_file(file1, file2):
    if file1 == "" or file2 == "":
        print "should not be empty"
        sys.exit()
    else:
        print "comparision..."
    text1_lines = read_file(file1)
    text2_lines = read_file(file2)
    diff = difflib.HtmlDiff()    
    result = diff.make_file(text1_lines, text2_lines)  

    d = difflib.Differ()
    #print(list(d.compare(text1_lines, text2_lines)))
    print("********************")
    print("".join(list(d.compare(text1_lines, text2_lines))))
    try:
        with open('result_comparation.html', 'w') as result_file:
            result_file.write(result)
            print "0==}==========> Successfully Finished\n"
    except IOError as error:
        print "wrong thml"


if __name__ == "__main__":
    my_parser = argparse.ArgumentParser(description="two parameter")
    my_parser.add_argument('-f1', action='store', dest='fname1', required=True)
    my_parser.add_argument('-f2', action='store', dest='fname2', required=True)

    given_args = my_parser.parse_args()
    file1 = given_args.fname1
    file2 = given_args.fname2
    compare_file(file1, file2)
