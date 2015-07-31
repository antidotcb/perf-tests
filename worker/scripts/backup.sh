#!/bin/bash

dts() { date +%Y-%m-%d-%H-%M-%S; }

dmkdir() { newdir="$@$(dts)"; mkdir ${newdir} & echo ${newdir}; }

log_dir="/media/mt4_logs/"
log_mask="T*"
backup_dir="/media/mt4_logs/_backup/"

dmkdir $backup_dir

for server_dir in $( ls -d $log_dir$log_mask );
do
    echo rsync -av $server_dir $newdir
done

#rmdir $newdir
