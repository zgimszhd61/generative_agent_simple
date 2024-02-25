import random
import string
import csv
import time
import datetime as dt
import pathlib
import os
import sys
import numpy
import math
import shutil
import errno
from os import listdir

def create_folder_if_not_there(curr_path): 
  """
  检查当前路径中的文件夹是否存在。如果不存在，则创建该文件夹。
  注意，如果curr_path指定了文件位置，则将操作包含该文件的文件夹。
  但是该函数即使路径指定为一个文件夹也同样适用。
  参数：
    curr_list：待写入的列表。该列表以以下形式出现：
               [['key1', 'val1-1', 'val1-2'...],
                ['key2', 'val2-1', 'val2-2'...],]
    outfile：要写入的csv文件的名称    
  返回值： 
    True：如果创建了新文件夹
    False：如果未创建新文件夹
  """
  outfolder_name = curr_path.split("/")
  if len(outfolder_name) != 1: 
    # 检查当前路径是文件还是文件夹。
    if "." in outfolder_name[-1]: 
      outfolder_name = outfolder_name[:-1]

    outfolder_name = "/".join(outfolder_name)
    if not os.path.exists(outfolder_name):
      os.makedirs(outfolder_name)
      return True

  return False 


def write_list_of_list_to_csv(curr_list_of_list, outfile):
  """
  将列表的列表写入csv文件。
  与write_list_to_csv_line不同，它一次性写入整个csv。
  参数：
    curr_list_of_list：待写入的列表。该列表以以下形式出现：
               [['key1', 'val1-1', 'val1-2'...],
                ['key2', 'val2-1', 'val2-2'...],]
    outfile：要写入的csv文件的名称    
  返回值： 
    None
  """
  create_folder_if_not_there(outfile)
  with open(outfile, "w") as f:
    writer = csv.writer(f)
    writer.writerows(curr_list_of_list)


def write_list_to_csv_line(line_list, outfile): 
  """
  将一行写入csv文件。
  与write_list_of_list_to_csv不同，此函数打开一个现有的outfile，然后将一行追加到该文件。
  即使文件不存在，这也有效。
  参数：
    curr_list：待写入的列表。该列表以以下形式出现：
               ['key1', 'val1-1', 'val1-2'...]
               重要的是，这不是列表的列表。
    outfile：要写入的csv文件的名称   
  返回值： 
    None
  """
  create_folder_if_not_there(outfile)

  # 首先打开文件，以便随着进度的推进逐步写入
  curr_file = open(outfile, 'a',)
  csvfile_1 = csv.writer(curr_file)
  csvfile_1.writerow(line_list)
  curr_file.close()


def read_file_to_list(curr_file, header=False, strip_trail=True): 
  """
  将csv文件读入列表的列表中。如果header为True，则返回一个元组（标题行，所有行）。
  参数：
    curr_file：当前csv文件的路径。 
  返回值： 
    列表的列表，其中组件列表是文件的行。 
  """
  if not header: 
    analysis_list = []
    with open(curr_file) as f_analysis_file: 
      data_reader = csv.reader(f_analysis_file, delimiter=",")
      for count, row in enumerate(data_reader): 
        if strip_trail: 
          row = [i.strip() for i in row]
        analysis_list += [row]
    return analysis_list
  else: 
    analysis_list = []
    with open(curr_file) as f_analysis_file: 
      data_reader = csv.reader(f_analysis_file, delimiter=",")
      for count, row in enumerate(data_reader): 
        if strip_trail: 
          row = [i.strip() for i in row]
        analysis_list += [row]
    return analysis_list[0], analysis_list[1:]


def read_file_to_set(curr_file, col=0): 
  """
  将csv文件的“单个列”读入集合中。 
  参数：
    curr_file：当前csv文件的路径。 
  返回值： 
    包含csv文件单个列中所有项目的集合。 
  """
  analysis_set = set()
  with open(curr_file) as f_analysis_file: 
    data_reader = csv.reader(f_analysis_file, delimiter=",")
    for count, row in enumerate(data_reader): 
      analysis_set.add(row[col])
  return analysis_set


def get_row_len(curr_file): 
  """
  获取csv文件中的行数 
  参数：
    curr_file：当前csv文件的路径。 
  返回值： 
    行数
    如果文件不存在则返回False
  """
  try: 
    analysis_set = set()
    with open(curr_file) as f_analysis_file: 
      data_reader = csv.reader(f_analysis_file, delimiter=",")
      for count, row in enumerate(data_reader): 
        analysis_set.add(row[0])
    return len(analysis_set)
  except: 
    return False


def check_if_file_exists(curr_file): 
  """
  检查文件是否存在
  参数：
    curr_file：当前csv文件的路径。 
  返回值： 
    如果文件存在则返回True
    如果文件不存在则返回False
  """
  try: 
    with open(curr_file) as f_analysis_file: pass
    return True
  except: 
    return False


def find_filenames(path_to_dir, suffix=".csv"):
  """
  给定一个目录，找到所有以提供的后缀结尾的文件并返回它们的路径。 
  参数：
    path_to_dir：当前目录的路径 
    suffix：目标后缀。
  返回值： 
    目录中所有文件的路径列表。 
  """
  filenames = listdir(path_to_dir)
  return [ path_to_dir+"/"+filename 
           for filename in filenames if filename.endswith( suffix ) ]


def average(list_of_val): 
  """
  计算列表中数字的平均值。
  参数：
    list_of_val：数字值列表  
  返回值： 
    值的平均值
  """
  return sum(list_of_val)/float(len(list_of_val))


def std(list_of_val): 
  """
  计算列表中数字的标准差。
  参数：
    list_of_val：数字值列表  
  返回值： 
    值的标准差
  """
  std = numpy.std(list_of_val)
  return std


def copyanything(src, dst):
  """
  将源文件夹中的所有内容复制到目标文件夹中。 
  参数：
    src：源文件夹的地址  
    dst：目标文件夹的地址  
  返回值： 
    None
  """
  try:
    shutil.copytree(src, dst)
  except OSError as exc: # python >2.5
    if exc.errno in (errno.ENOTDIR, errno.EINVAL):
      shutil.copy(src, dst)
    else: raise


if __name__ == '__main__':
  pass
