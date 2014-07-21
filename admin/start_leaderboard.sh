#!/bin/bash - 

set -o nounset  # Treat unset variables as an error

cd ${0%/*}
shdir=$PWD
rootdir=${shdir%/*}

cd $rootdir

mkdir -p $rootdir/logs

#kill running processes
pid=`ps aux | grep "leaderboard_http.py" | grep -v "grep" | grep -v "vi" | awk -F" " '{print $2}'`
pidnum=`echo $pid | wc | awk '{print $2}'`

if [ $pidnum -ne 0 ]; then
        echo "is running"
        echo $pid | xargs kill >> $rootdir/logs/log.leaderboard_http.sh 2>&1
		echo "kill and restart"
fi

#start process
nohup python $rootdir/src/leaderboard_http.py >> $rootdir/logs/log.leaderboard_http.sh 2>&1 &


