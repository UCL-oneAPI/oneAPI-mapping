import json
import os
import mapping_extraction
import pandas as pd

allFileNum = 0
mapping_result = {}
mapping_list = []
non_matched_collection = {}  # this is the collection of the non matched snippets
file_counter = 0
test_dict = set()
counter_1, counter_2 = 0, 0


def file_existing_check(file_path):
    return os.path.exists(file_path)


def printPath(level, path, root_dir):
    global allFileNum, mapping_result

    # define the map (collect the mapping)
    ''''' 
    print all files in the same directory
    '''
    # get the root path for this function call
    global file_counter, mapping_result, non_matched_collection, mapping_list
    dirList = []
    fileList = []
    files = os.listdir(path)
    dirList.append(str(level))
    for f in files:
        if (os.path.isdir(path + '/' + f)):
            if (f[0] == '.'):
                pass
            else:
                dirList.append(f)
        if (os.path.isfile(path + '/' + f)):
            fileList.append(f)

            # check the file surfix
            if (f.endswith(".dp.cpp")):

                # get the name of the dp.cpp file
                sub_dir = path.replace("dpcpp", "").replace(root_dir, '')
                a = "".join([path, "/", f])

                # get the name of the .cpp file
                b = ("".join([path, "/", str(f)])).replace("dpcpp", "dpct-version").replace('dp.cpp', 'cpp')

                # check file existing
                if (file_existing_check(a) and file_existing_check(b)):
                    test_dict.add(a)
                    file_name = a
                    print("filename: ", a)
                    dpct_snippets, manual_snippets, warning_messages = mapping_extraction.mapping_extraction(a, b)
                    file_counter += 1
                    # currently only output the snippets which numbers matched
                    if len(dpct_snippets) == len(manual_snippets):
                        mapping_result[a] = []
                        for i in range(len(dpct_snippets)):
                            mapping_result[a].append(
                                {"dpct snippet": dpct_snippets[i], "manual snippets": manual_snippets[i]})
                            mapping_list.append({'file name': a, "dpct snippet": dpct_snippets[i],
                                                 "manual snippets": manual_snippets[i]})


                    else:
                        non_matched_collection[a] = {"dpct snippet": dpct_snippets, "manual snippets": manual_snippets}

    i_dl = 0
    for dl in dirList:
        if (i_dl == 0):
            i_dl = i_dl + 1
        else:
            printPath((int(dirList[0]) + 1), path + '/' + dl, root_dir)
    for fl in fileList:
        allFileNum = allFileNum + 1


def iterate_all_projects():
    folders = [f for f in os.listdir("../oneAPI-DirectProgramming-training/") if not f.startswith('.')]
    for folder in folders:
        printPath(1, '../oneAPI-DirectProgramming-training/' + folder + '/dpcpp',
                  '../oneAPI-DirectProgramming-training/' + folder)
        # print('../oneAPI-DirectProgramming-training/'+folder+'/dpcpp')
        print("\n\n\n\n\n")


def store_in_csv(map_res: list):
    pd.DataFrame(map_res).to_csv('mapping-result.csv')


if __name__ == '__main__':
    # 修改‘’中的目录为需要索引的根目录
    # printPath(1, '../oneAPI-DirectProgramming-training/b+tree/dpcpp',"../oneAPI-DirectProgramming-training/b+tree/")
    # print('总文件数 =', allFileNum)

    # test iterate_all_projects()
    iterate_all_projects()
    with open('mapping-result.json', 'w') as f:
        json.dump(mapping_result, f, indent=4)
        print("mapping result output finish...")

    store_in_csv(mapping_list)
