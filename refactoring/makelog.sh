#!/bin/bash

print_usage() {
  echo "Usage: "
  echo "$0 FILE"
  echo ""
  echo "example:"
  echo -e "$0 \033[96mFILENAME\033[0m"
  echo ""
}

path="."
if [ $# -eq 1 ];then
  path=$1
else
  print_usage
  exit 1
fi

cnt=0
total_cnt=2
start_index=10
end_index=$(( ${start_index}+${total_cnt}-1 ))
echo "copy ${path} ${total_cnt} times from index ${start_index} to ${end_index}"
while (( ${cnt} < ${total_cnt} ))
do
  #echo "cp" ${path} ${path}.${start_index}
  cp ${path} ${path}.${start_index}
  cnt=$(( ${cnt} + 1 ))
  start_index=$(( ${start_index} + 1 ))
  sleep 0.1
done
