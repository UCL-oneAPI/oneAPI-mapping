# oneAPI-mapping
 This is a sub-tools for generating training data used in CTA(Code Translation Assistant). This tools will process the DPCT version of the projects(generated by using one-API) and Manual modified version(which is provided on Github repository wrote by intel employeer, website:https://github.com/zjin-lcf/oneAPI-DirectProgramming).   

 This tools can be later used by other developers which also want to make further development on CTA or oneAPI.

# main functions
 Mapping tools will:
 * Automatically process the two version of the project source code, and return a mapping dictionary which contains the code segement for different warnings. \
 (dictionary structure: {file name:  {dpct_snippets: " " ,manual_snippets:" "}} )
 * Based on the mapping extraction result, this tools will automatically generate a report which constains the comparision of code snippets(dpct version and manual modified version) 

 # User Guide
All the functions are contained in the main.py in this repository. To run all of the functions you need to use the following command.  
```
python main.py
```
The csv and report and corresponding json file will be generated in the root directory in this repository folder.

