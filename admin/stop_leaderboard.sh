#!/bin/bash - 

ps aux | grep "leaderboard_http.py" | grep -v grep | awk '{print $2}' | xargs kill
