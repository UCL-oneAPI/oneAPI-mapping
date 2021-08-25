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
    打印一个目录下的所有文件夹和文件 
    '''
    # 所有文件夹，第一个字段是次目录的级别
    # get the root path for this function call
    global file_counter, mapping_result, non_matched_collection, mapping_list
    dirList = []
    # 所有文件  
    fileList = []
    # 返回一个列表，其中包含在目录条目的名称
    files = os.listdir(path)
    # 先添加目录级别  
    dirList.append(str(level))
    for f in files:
        if (os.path.isdir(path + '/' + f)):
            if (f[0] == '.'):  # 忽略隐藏文件夹
                pass
            else:  # 非隐藏文件夹
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
                            mapping_list.append({'file name':a,"dpct snippet": dpct_snippets[i], "manual snippets": manual_snippets[i]})


                        # if a not in mapping_result.keys():
                        #     mapping_result[a] = [
                        #         {"dpct snippet": dpct_snippets[i], "manual snippets": manual_snippets[i]}]
                        #     # mapping_result[a] = [{"warning message":warning_messages[i],"dpct snippet":dpct_snippets[i],"manual snippets":manual_snippets[i]}]
                        # else:
                        #     mapping_result[a].append(
                        #         {"dpct snippet": dpct_snippets[i], "manual snippets": manual_snippets[i]})
                            # mapping_result[a].append({"warning message":warning_messages[i],"dpct snippet":dpct_snippets[i],"manual snippets":manual_snippets[i]})
                        # mapping_result[a] = ({"dpct snippet":dpct_snippets[i],"manual snippets":manual_snippets[i]})
                    else:
                        non_matched_collection[a] = {"dpct snippet": dpct_snippets, "manual snippets": manual_snippets}
                        # if a not in non_matched_collection.keys():
                        #     non_matched_collection[a] = [{"dpct snippet":dpct_snippets,"manual snippets":manual_snippets}]
                        # else:
                        #     non_matched_collection[a].append({"dpct snippet":dpct_snippets,"manual snippets":manual_snippets})

                        # print(warning_messages[i])
    # print(mapping_result)

    ####可以利用os.path.splitext() 方法: 该方法返回两个元素, 第一个是路径去掉后缀的部分, 第二个是文件后缀:

    # -------------------------------print-----------------------------------
    # 当一个标志使用，文件夹列表第一个级别不打印  
    i_dl = 0
    for dl in dirList:
        if (i_dl == 0):
            i_dl = i_dl + 1
        else:
            # 打印至控制台，不是第一个的目录  
            # print ('-' * (int(dirList[0])), dl  )
            # 打印目录下的所有文件夹和文件，目录级别+1  
            printPath((int(dirList[0]) + 1), path + '/' + dl, root_dir)
    for fl in fileList:
        # 打印文件  
        # print ('-' * (int(dirList[0])), fl  )
        # 随便计算一下有多少个文件  
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
    with open('mapping-result.json','w') as f:
        json.dump(mapping_result, f, indent=4)
        print("mapping result output finish...")

    store_in_csv(mapping_list)

