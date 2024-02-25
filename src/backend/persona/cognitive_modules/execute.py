"""
作者：Joon Sung Park（joonspk@stanford.edu）

文件：execute.py
描述：为生成型代理定义了“Act”模块。
"""
import sys
import random
sys.path.append('../../')

from opensource.generative_agent_simple.backend.global_methods import *
from opensource.generative_agent_simple.backend.path_finder import *
from utils import *

def execute(persona, maze, personas, plan): 
    """
    给定一个计划（动作的字符串地址），我们执行该计划（实际输出路径的瓦片坐标和人物的下一个坐标）。

    输入：
        persona：当前的 <Persona> 实例。
        maze：当前 <Maze> 的实例。
        personas：世界中所有人物的字典。
        plan：需要执行的动作的字符串地址。
            它的格式为"{world}:{sector}:{arena}:{game_objects}"。
            非常重要的是不要使用负索引（例如，[-1]），因为在某些情况下可能不存在后面的地址元素。
            例如，"dolores double studio:double studio:bedroom 1:bed"
        
    输出：
        execution
    """
    if "<random>" in plan and persona.scratch.planned_path == []: 
        persona.scratch.act_path_set = False

    # 如果未设置路径，则将 <act_path_set> 设置为 True，表示需要构建新路径。
    if not persona.scratch.act_path_set: 
        # <target_tiles> 是一个瓦片坐标列表，表示人物可能去执行当前动作的位置。目标是选择其中一个。
        target_tiles = None

        if "<persona>" in plan: 
            # 执行人物-人物交互。
            target_p_tile = (personas[plan.split("<persona>")[-1].strip()]
                            .scratch.curr_tile)
            potential_path = path_finder(maze.collision_maze, 
                                        persona.scratch.curr_tile, 
                                        target_p_tile, 
                                        collision_block_id)
            if len(potential_path) <= 2: 
                target_tiles = [potential_path[0]]
            else: 
                potential_1 = path_finder(maze.collision_maze, 
                                        persona.scratch.curr_tile, 
                                        potential_path[int(len(potential_path)/2)], 
                                        collision_block_id)
                potential_2 = path_finder(maze.collision_maze, 
                                        persona.scratch.curr_tile, 
                                        potential_path[int(len(potential_path)/2)+1], 
                                        collision_block_id)
                if len(potential_1) <= len(potential_2): 
                    target_tiles = [potential_path[int(len(potential_path)/2)]]
                else: 
                    target_tiles = [potential_path[int(len(potential_path)/2+1)]]
        
        elif "<waiting>" in plan: 
            # 执行人物在执行动作之前决定等待的交互。
            x = int(plan.split()[1])
            y = int(plan.split()[2])
            target_tiles = [[x, y]]

        elif "<random>" in plan: 
            # 执行随机位置动作。
            plan = ":".join(plan.split(":")[:-1])
            target_tiles = maze.address_tiles[plan]
            target_tiles = random.sample(list(target_tiles), 1)

        else: 
            # 默认执行。将人物带到当前动作发生的位置。
            # 检索目标地址。再次说明，plan 是动作地址的字符串形式。 <maze.address_tiles> 获取这个并返回候选坐标。
            if plan not in maze.address_tiles: 
                maze.address_tiles["Johnson Park:park:park garden"] # 错误
            else: 
                target_tiles = maze.address_tiles[plan]

        # 有时会返回多个瓦片（例如，一个桌子可能延伸到许多坐标）。因此，我们在这里进行随机抽样。
        if len(target_tiles) < 4: 
            target_tiles = random.sample(list(target_tiles), len(target_tiles))
        else:
            target_tiles = random.sample(list(target_tiles), 4)
        
        # 如果可能，我们希望人物在前往迷宫相同位置时占据不同的瓦片。
        # 如果他们最终在同一个瓦片上，也可以，但我们试图降低这种可能性。
        # 我们在这里处理重叠。
        persona_name_set = set(personas.keys())
        new_target_tiles = []
        for i in target_tiles: 
            curr_event_set = maze.access_tile(i)["events"]
            pass_curr_tile = False
            for j in curr_event_set: 
                if j[0] in persona_name_set: 
                    pass_curr_tile = True
            if not pass_curr_tile: 
                new_target_tiles += [i]
        if len(new_target_tiles) == 0: 
            new_target_tiles = target_tiles
        target_tiles = new_target_tiles

        # 现在我们已经确定了目标瓦片，我们找到了到其中一个目标瓦片的最短路径。
        curr_tile = persona.scratch.curr_tile
        collision_maze = maze.collision_maze
        closest_target_tile = None
        path = None
        for i in target_tiles: 
            curr_path = path_finder(maze.collision_maze, 
                                    curr_tile, 
                                    i, 
                                    collision_block_id)
            if not closest_target_tile: 
                closest_target_tile = i
                path = curr_path
            elif len(curr_path) < len(path): 
                closest_target_tile = i
                path = curr_path

        # 实际设置 <planned_path> 和 <act_path_set>。我们在计划路径中去掉了第一个元素，因为它包括当前瓦片。
        persona.scratch.planned_path = path[1:]
        persona.scratch.act_path_set = True
    
    # 设置下一步。如果没有剩余的 <planned_path>，则留在当前瓦片，否则，去到路径中的下一个瓦片。
    ret = persona.scratch.curr_tile
    if persona.scratch.planned_path: 
        ret = persona.scratch.planned_path[0]
        persona.scratch.planned_path = persona.scratch.planned_path[1:]

    description = f"{persona.scratch.act_description}"
    description += f" @ {persona.scratch.act_address}"

    execution = ret, persona.scratch.act_pronunciation, description
    return execution
