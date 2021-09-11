cd ..
parent_dir=$(cd $(dirname $0); pwd)
cd oneAPI-DirectProgramming-training
mkdir $1
cd ../oneAPI-DirectProgramming
source /opt/intel/oneapi/setvars.sh

# cd oneAPI-DirectProgramming

function read_dir(){
current_dir=$(cd $(dirname $0); pwd) 
for file in `ls $1` 
do
if [ -d $1"/"$file ]
    then
        # read_dir $1"/"$file
        new_path=$3/$file
        read_dir $1/$file $2 ${new_path##/}/ $4
    else
        if [ "${file##*.}"x = "cu"x ];then
            # dpct --in-root=. $file --out-root=${current_dir}/dpcpp
            # echo ${3##/}/
            a=$3/$file
            echo ${a##/} 
            # echo ${2}/oneAPI-DirectProgramming-training/${4}/dpcpp/${3}
            # echo ===
            # cd ${2}/oneAPI-DirectProgramming-training/${4}
            # pwd
            # dpct --in-root=. $3/$file --out-root=${2}/oneAPI-DirectProgramming-training/${4}/dpcpp/
            dpct --in-root=. ${a##/} --out-root=${2}/oneAPI-DirectProgramming-training/${4}/dpcpp/
            # echo /${2}/scripts_output/${3}/dpcpp
        fi
fi
done
} 

root_dir=$(cd $(dirname $0); pwd)
cd ${1}-cuda
echo $parent_dir
x=$(find . -name "*.cu")
workdir=$(cd $(dirname $0); pwd)
if [ -d "dpcpp" ];then
    echo "this project has been translated"
else
    echo working: $workdir
    echo parent: $parent_dir
    echo 1:$1    
    # read_dir $workdir $parent_dir $1 $1
    read_dir $workdir $parent_dir "" $1
fi


echo -------------------------------
cd $parent_dir/oneAPI-DirectProgramming-training/${1}
cd dpcpp
path_prefix=$(cd $(dirname $0); pwd)
echo $path_prefix
dpcpp_collection=$(find . -name "*.dp.cpp")
for file in $dpcpp_collection;do
    file=${file#*/}
    python3 $parent_dir/training_data_overview/warnings_count.py $path_prefix/$file
    echo $path_prefix/$file
    
done
cp -rvf ../../../oneAPI-DirectProgramming/${1}-dpct ../dpct-version



cd $root_dir
pwd
