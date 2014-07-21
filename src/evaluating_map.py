import sys
import time


def evaluation(path_test, path_truth, debug_info=False, err_msg = []):
  '''
  main(path_test, path_truth)
  @param path_test: file to test, format(Itemid1[ Itemid2...]), or(Userid,Itemid1[ Itemid2...]);
  @param path_truth: file of groundtruth, format(Userid,Itemid1[ Itemid2...])
  the details will be printed to standard output
  '''
  file_truth = open(path_truth)
  file_test = open(path_test)

  #check file format, if is csv, the first line should be 'id, clicks'
  flag_csv = False
  first_line = file_test.readline()
  if first_line.find('id') >= 0:
    flag_csv = True
    if debug_info:
      print 'file format is csv!'
  else:
    file_test.close()
    file_test = open(path_test)  
    if debug_info:
      print 'file format is not csv!'

  if debug_info:
    print 'userid', '\twrong_list', '\tap', '\tlen(positive_item_list)'

  line_total = 0
  ap_list = []


  #travelse both files 
  for truth_line in file_truth:
    test_line = file_test.readline()
    if not test_line: 
      err_msg.append('format error, comes to the end, line:' + str(line_total))
      return 0
    
    line_total += 1

    #parse groundtruth
    [userid, positive_items] = truth_line.strip().split(',')
    if len(positive_items) == 0: 
      ap_list.append(0)
      continue
    positive_item_list = positive_items.split(' ')

    #parse test line according to the format
    if flag_csv:
      userid_2, item_list_str = test_line.strip().split(',')
      if userid != userid_2:
        err_msg.append('format error, userid not match, line:' + str(line_total))
        return 0
      test_item_list = item_list_str.strip().split(' ')
    else:
      test_item_list = test_line.strip().split(' ')

    #check validation and remove duplication
    if len(test_item_list) > 3:
      err_msg.append('format error, too many items, line:' + str(line_total))
      return 0
    else:
      test_item_old = test_item_list
      test_item_list = []
      test_item_list = [item for item in test_item_old if item not in test_item_list]
   
    #number of groundtruth, if is 0, ignore 
    n_positive = len(positive_item_list)
    if n_positive == 0: 
      ap_list.append(0)
      continue
    #if n_positive > 3: n_positive = 3

    #calculate average precision: AP = sigma(p@i) / m 
    n_right = 0
    ap = 0
    wrong_list = []
    for i in range(0, len(test_item_list)):
      item = test_item_list[i]
      if item in positive_item_list:
        n_right += 1
        ap += n_right / float(i + 1)
        if n_right == n_positive: break
      else:
        wrong_list.append(item)
    ap /= n_positive

    ap_list.append(ap)   
    if debug_info:
      print userid, wrong_list, ap, len(positive_item_list)

  file_truth.close()
  file_test.close()

  if debug_info:
    print 'process lines', line_total 
    print 'lines with positive', len(ap_list)

  #calculate mean average precision: MAP = mean(AP)
  mean_ap = 0
  for ap in ap_list:
    mean_ap += ap
  mean_ap /= len(ap_list)

  if debug_info:
    print 'map', mean_ap
  return mean_ap


if __name__ == '__main__':
  if len(sys.argv) == 3:
    start_time = time.time()

    err_msg = []
    evaluation(sys.argv[1], sys.argv[2], True, err_msg)
    print err_msg

    end_time = time.time()
    print 'use time:', (end_time-start_time), 'seconds'
  else:
    print 'usage: file_to_test, file_for_groundtruth'

 
