#! /bin/sh

# set Python environment
PYTHONIOENCODING="latin1"
export PYTHONIOENCODING

# Usage message
if [ $# -lt 2 ]
then
    echo "Usage: $(basename $0) [-w N] [-i file] [-f|-c|-t] directory directory"
    exit 1
fi

# save last two parameters as name of the directories
for i
do
    dir1=$dir2
    dir2=$i
done

# then rebuild command line without last two parameters
i=2
for arg
do
    if [ $i -eq $# ]
    then
        break
    else
        i=`expr $i + 1`
    fi

    args="$args $arg"
done

# verify these are actually directories or die with an error message
if [ ! -d "$dir1" ]; then
    echo "$dir1 is not a directory"
    exit 1
fi

if [ ! -d "$dir2" ]; then
    echo "$dir2 is not a directory"
    exit 1
fi

# create temporary files where we'll save output from Python script
out1=out1.txt
out2=out2.txt

# rest of parameters are passed to Python script
./wordcount.py $dir1/* $args > $out1
./wordcount.py $dir2/* $args > $out2

# horizontally catenate the results
paste $out1 $out2

# clean up temp files
rm -f $out1 $out2
