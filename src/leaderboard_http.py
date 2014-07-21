#!/usr/bin/pytnon
#coding: utf-8

import sys
import os
import redis
import random
reload(sys)
sys.setdefaultencoding('utf-8')

import time
import json
import redis
import pymongo
from exceptions import Exception

from tornado import httpserver
from tornado import ioloop

import logging
import logging.config

from evaluating_map import *

cur_path = os.path.dirname(__file__)
log_conf_file = os.path.join(cur_path, '../conf/log.conf')
logging.config.fileConfig(log_conf_file)
ilog = logging.getLogger('root')


truth_path = '/home/liuzuotao/kddcup2012/data/dog_mid/dog_positive.txt'
rdb = redis.StrictRedis(host = "192.168.91.162", port = 6399, db = 13)
#rdb = redis.StrictRedis(host = "192.168.91.162", port = 6399, db = 14)

def handle_commit(request):
  args = request.arguments

  f = lambda x: " ".join(x)

  test_path = f(args.get('path', []))
  desc = f(args.get('desc', []))

  print 'commit file:', test_path
  print 'commit desc:', desc

  err_msg = []
  score = 0
  try:
    score = evaluation(test_path, truth_path, False, err_msg)
  except Exception as e:
    message += 'evaluation error! <br>'

  message = str(score) + '<br>'
  for msg_line in err_msg:
    message += msg_line + '<br>' 

  print message

  zkey = str(time.time())
  rdb.zadd('leaderboard', score, zkey)
  rdb.set(zkey, desc)
  

  request.write("HTTP/1.1 200 OK\r\nContent-Length: %d\r\nContent-Type: text/HTML\r\n\r\n%s" % (len(message), message))
  request.finish()
  

def handle_rank(request):
  img_idx = random.randint(1,5)
  message = '<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"></head><body style=\"background-color:PowderBlue;\" background=\"res/smth' + str(img_idx) + '.jpg\">'
  #message = '<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"></head><body style=\"background-color:PowderBlue;\" >'
  message += '<table border=\"2\" cellspacing=\"5\"><caption>Leaderboard (<a href=\"/page\">submit</a>)</caption>'
  message += '<tr><th>Rank</th><th>Score</th><th>Time</th><th>Description</th><th>Delete?</th></tr>'

  i_rank = 0
  
  score_list = rdb.zrange('leaderboard', 0, 50, desc=True, withscores=True)

  for (zkey, score) in score_list:
    timestamp = int(float(zkey))
    asctime = time.asctime(time.localtime(timestamp))
    desc = rdb.get(zkey)
    i_rank += 1
    #message += '<p style=\"font-family:verdana;color:red;font-size:20px\">Rank ' + str(i_rank) + ': <b>' + str(score) + '</b></p>'
    #message += '<p style=\"color:blue;\"><em>' + asctime + '</em>.   Desc: <b><big>' + desc + '.</big></b></p><hr/> '
    message += '<tr><td bgcolor=\"red\">' + str(i_rank) + '</td><td>' + str(score) + '</td><td>' + asctime + '</td><td>' + desc + '</td><td><a href=\"/del?time=' + zkey + '\">delete</a></td></tr>'

  message += '</table>'
  message += '</body></html>'
  print message 

  request.write("HTTP/1.1 200 OK\r\nContent-Length: %d\r\nContent-Type: text/HTML\r\n\r\n%s" % (len(message), message))
  request.finish()


def handle_error(request):
  res = {'error':'wrong path, should be /page'}
  message = json.dumps(res)
  print message

  request.write("HTTP/1.1 200 OK\r\nContent-Length: %d\r\nContent-Type: application/json\r\n\r\n%s" % (len(message), message))
  request.finish()


def handle_page(request):
  html_file = open('res/page.html')
  message = ""
  for line in html_file:
    message += line
  html_file.close()
  print message

  request.write("HTTP/1.1 200 OK\r\nContent-Length: %d\r\nContent-Type: text/HTML\r\n\r\n%s" % (len(message), message))
  request.finish()


def handle_del(request):
  print 'handle del'

  args = request.arguments

  f = lambda x: " ".join(x)

  zkey = f(args.get('time', []))
  message = ""
  if rdb.zrem('leaderboard', zkey):
    message += 'succeed!'
  else:
    message += 'no record!'
  rdb.delete(zkey)
  print message

  message += '<br><a href=\"/rank\">rank page</a><br><a href=\"/page\">submit page</a>'
  request.write("HTTP/1.1 200 OK\r\nContent-Length: %d\r\nContent-Type: text/HTML\r\n\r\n%s" % (len(message), message))
  request.finish()


def handle_res(request):
  print 'handle res'
  jpg_file = open(request.path[1:])
  message = ""
  for line in jpg_file:
    message += line
  jpg_file.close()
  print message

  request.write("HTTP/1.1 200 OK\r\nContent-Length: %d\r\nContent-Type: image/jpeg\r\n\r\n%s" % (len(message), message))
  request.finish()


def handle_request(request):
  print request
  print request.path

  if request.path == '/page':
    print 'page'
    handle_page(request)
  elif request.path == '/commit':
    print 'commit'
    handle_commit(request)
  elif request.path == '/rank':
    print 'rank'
    handle_rank(request)
  elif request.path == '/del':
    print 'del'
    handle_del(request)
  elif request.path.startswith('/res'):
    print 'res'
    handle_res(request)
  else:
    print 'wrong'
    handle_error(request)


http_server = httpserver.HTTPServer(handle_request)
http_server.listen(8866)
ioloop.IOLoop.instance().start()

