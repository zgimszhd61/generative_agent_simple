import math
import sys
import datetime
import random
sys.path.append('../')

from global_methods import *

from persona.memory_structures.spatial_memory import *
from persona.memory_structures.associative_memory import *
from persona.memory_structures.scratch import *

from persona.cognitive_modules.perceive import *
from persona.cognitive_modules.retrieve import *
from persona.cognitive_modules.plan import *
from persona.cognitive_modules.reflect import *
from persona.cognitive_modules.execute import *
from persona.cognitive_modules.converse import *

class Persona:
    def __init__(self, name, folder_mem_saved=False):
        """
        初始化Persona对象。

        参数：
            name：Persona的全名，是在Reverie中唯一标识该Persona的标识符。
            folder_mem_saved：如果文件夹folder_mem_saved中已经存在内存，则加载该内存；否则，创建新的内存实例。
        """
        self.name = name
        f_s_mem_saved = f"{folder_mem_saved}/bootstrap_memory/spatial_memory.json"
        self.s_mem = MemoryTree(f_s_mem_saved)
        f_a_mem_saved = f"{folder_mem_saved}/bootstrap_memory/associative_memory"
        self.a_mem = AssociativeMemory(f_a_mem_saved)
        scratch_saved = f"{folder_mem_saved}/bootstrap_memory/scratch.json"
        self.scratch = Scratch(scratch_saved)

    def save(self, save_folder):
        """
        保存Persona的当前状态（即内存）。

        参数：
            save_folder：我们将保存Persona状态的文件夹。
        返回值：
            无
        """
        f_s_mem = f"{save_folder}/spatial_memory.json"
        self.s_mem.save(f_s_mem)
        f_a_mem = f"{save_folder}/associative_memory"
        self.a_mem.save(f_a_mem)
        f_scratch = f"{save_folder}/scratch.json"
        self.scratch.save(f_scratch)

    def perceive(self, maze):
        """
        获取当前迷宫中发生的事件。

        参数：
            maze：当前世界的迷宫实例。
        返回值：
            一个包含感知到的新概念节点的列表。
        """
        return perceive(self, maze)

    def retrieve(self, perceived):
        """
        获取与感知到的事件相关的事件和思考的集合。

        参数：
            perceived：一个包含感知到的新概念节点的列表。
        返回值：
            一个字典，其中第一层指定一个事件，而后一层指定与之相关的当前事件、事件和思考。
        """
        return retrieve(self, perceived)

    def plan(self, maze, personas, new_day, retrieved):
        """
        对Persona进行长期和短期规划。

        参数：
            maze：当前世界的迷宫实例。
            personas：一个字典，其中包含所有Persona名称作为键，Persona实例作为值。
            new_day：这可以取三个值之一。
                     1）<布尔值>False——不是“新的一天”周期（如果是，我们需要为Persona调用长期规划序列）。
                     2）<字符串>“第一天”——这实际上是模拟开始，因此不仅是新的一天，而且是第一天。
                     3）<字符串>“新的一天”——这是一个新的一天。
            retrieved：一个字典，其中第一层指定一个事件，而后一层指定与之相关的当前事件、事件和思考。
        返回值：
            Persona的目标动作地址（persona.scratch.act_address）。
        """
        return plan(self, maze, personas, new_day, retrieved)

    def execute(self, maze, personas, plan):
        """
        执行Persona的当前计划。

        参数：
            maze：当前世界的迷宫实例。
            personas：一个字典，其中包含所有Persona名称作为键，Persona实例作为值。
            plan：Persona的目标动作地址（persona.scratch.act_address）。
        返回值：
            执行的具体动作，包含下一个方块、发音和描述。
        """
        return execute(self, maze, personas, plan)

    def reflect(self):
        """
        回顾Persona的内存并基于此产生新的思考。
        """
        reflect(self)

    def move(self, maze, personas, curr_tile, curr_time):
        """
        执行Persona的主要认知功能。

        参数：
            maze：当前世界的迷宫实例。
            personas：一个字典，其中包含所有Persona名称作为键，Persona实例作为值。
            curr_tile：当前Persona的当前方块位置。
            curr_time：指示游戏当前时间的datetime实例。
        返回值：
            执行的具体动作，包含下一个方块、发音和描述。
        """
        self.scratch.curr_tile = curr_tile
        new_day = False
        if not self.scratch.curr_time:
            new_day = "First day"
        elif (self.scratch.curr_time.strftime('%A %B %d')
                != curr_time.strftime('%A %B %d')):
            new_day = "New day"
        self.scratch.curr_time = curr_time
        perceived = self.perceive(maze)
        retrieved = self.retrieve(perceived)
        plan = self.plan(maze, personas, new_day, retrieved)
        self.reflect()
        return self.execute(maze, personas, plan)

    def open_convo_session(self, convo_mode):
        """
        开启对话模式。

        参数：
            convo_mode：对话模式。
        """
        open_convo_session(self, convo_mode)
