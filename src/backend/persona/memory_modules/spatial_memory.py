"""
作者: Joon Sung Park (joonspk@stanford.edu)

文件: spatial_memory.py
描述: 定义了MemoryTree类，用作代理程序的空间记忆，帮助它们在游戏世界中基于位置进行行为定位。
"""
import json
import sys
sys.path.append('../../')

from utils import *
from opensource.generative_agent_simple.backend.global_methods import *

class MemoryTree: 
  def __init__(self, f_saved): 
    self.tree = {}
    if check_if_file_exists(f_saved): 
      self.tree = json.load(open(f_saved))

  def print_tree(self): 
    """
    打印内存树的结构
    """
    def _print_tree(tree, depth):
      dash = " >" * depth
      if type(tree) == type(list()): 
        if tree:
          print (dash, tree)
        return 

      for key, val in tree.items(): 
        if key: 
          print (dash, key)
        _print_tree(val, depth+1)
    
    _print_tree(self.tree, 0)
    
  def save(self, out_json):
    """
    将内存树保存到JSON文件中
    """
    with open(out_json, "w") as outfile:
      json.dump(self.tree, outfile) 

  def get_str_accessible_sectors(self, curr_world): 
    """
    返回当前区域内代表人物可以访问的所有游戏场景的摘要字符串

    注意：某些情况下，人物无法进入。这些信息在人物表中提供。我们在这个函数中考虑到这一点。

    输入：
      None
    输出：
      代表人物可以访问的所有游戏场景的摘要字符串
    示例字符串输出：
      "卧室，厨房，餐厅，办公室，浴室"
    """
    x = ", ".join(list(self.tree[curr_world].keys()))
    return x

  def get_str_accessible_sector_arenas(self, sector): 
    """
    返回当前区域内代表人物可以访问的所有游戏场景的摘要字符串

    注意：某些情况下，人物无法进入。这些信息在人物表中提供。我们在这个函数中考虑到这一点。

    输入：
      None
    输出：
      代表人物可以访问的所有游戏场景的摘要字符串
    示例字符串输出：
      "卧室，厨房，餐厅，办公室，浴室"
    """
    curr_world, curr_sector = sector.split(":")
    if not curr_sector: 
      return ""
    x = ", ".join(list(self.tree[curr_world][curr_sector].keys()))
    return x

  def get_str_accessible_arena_game_objects(self, arena):
    """
    获取游戏场景中所有可访问的游戏对象的字符串列表。如果指定了temp_address，
    则返回该场景中可用的对象；如果未指定，则返回我们的角色当前所在场景中的对象。

    输入：
      temp_address：可选的场景地址
    输出：
      游戏场景中所有可访问的游戏对象的字符串列表
    示例字符串输出：
      "手机，充电器，床，床头柜"
    """
    curr_world, curr_sector, curr_arena = arena.split(":")
    if not curr_arena: 
      return ""

    try: 
      x = ", ".join(list(self.tree[curr_world][curr_sector][curr_arena]))
    except: 
      x = ", ".join(list(self.tree[curr_world][curr_sector][curr_arena.lower()]))
    return x

if __name__ == '__main__':
  x = f"../../../../environment/frontend_server/storage/the_ville_base_LinFamily/personas/Eddy Lin/bootstrap_memory/spatial_memory.json"
  x = MemoryTree(x)
  x.print_tree()

  print (x.get_str_accessible_sector_arenas("dolores double studio:double studio"))
