# test folder iteration functionality
cd ..
rootdir=$(cd $(dirname $0); pwd)
source /opt/intel/oneapi/setvars.sh
mkdir oneAPI-DirectProgramming-training
cd oneAPI-DirectProgramming
x=$(find . -name "*-cuda")
for folder in $x;do
    folder_name=${folder#*/}
    new_folder_name=${folder_name%'-cuda'}
    echo $new_folder_name
    cd $rootdir/training_data_overview
    ./auto_dpct_script.sh $new_folder_name
done