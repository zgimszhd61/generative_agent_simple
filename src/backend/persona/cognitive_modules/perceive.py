"""
作者: Joon Sung Park (joonspk@stanford.edu)

文件: perceive.py
描述: 这定义了生成型代理的“Perceive”模块。
"""
import sys
sys.path.append('../../')

import math
from operator import itemgetter
from opensource.generative_agent_simple.backend.global_methods import *
from persona.prompt_template.gpt_structure import *
from persona.prompt_template.run_gpt_prompt import *

def generate_poig_score(persona, event_type, description): 
  # 如果描述中包含"idle"，则返回1
  if "is idle" in description: 
    return 1

  # 根据事件类型调用不同的函数计算“poignancy”（一种情感度量）
  if event_type == "event": 
    return run_gpt_prompt_event_poignancy(persona, description)[0]
  elif event_type == "chat": 
    return run_gpt_prompt_chat_poignancy(persona, 
                           persona.scratch.act_description)[0]

def perceive(persona, maze): 
  """
  感知围绕人物发生的事件，并将其保存到记忆中，包括事件和空间。

  我们首先感知人物附近的事件，由其<vision_r>决定。如果在该半径内发生了很多事件，
  我们获取最近事件的<att_bandwidth>。最后，我们检查是否有新事件，根据<retention>来确定。
  如果是新事件，则保存它们并返回那些事件的<ConceptNode>实例。

  输入:
    persona: 表示当前人物的<Persona>实例。
    maze: 表示人物所在迷宫的<Maze>实例。
  输出:
    ret_events: 一组<ConceptNode>，表示被感知并且是新的事件。
  """
  # 感知空间
  # 根据当前瓦片和人物的视野半径，获取附近的瓦片。
  nearby_tiles = maze.get_nearby_tiles(persona.scratch.curr_tile, 
                                       persona.scratch.vision_r)

  # 存储感知到的空间。注意，persona的s_mem以字典构建的树的形式存在。
  for i in nearby_tiles: 
    i = maze.access_tile(i)
    if i["world"]: 
      if (i["world"] not in persona.s_mem.tree): 
        persona.s_mem.tree[i["world"]] = {}
    if i["sector"]: 
      if (i["sector"] not in persona.s_mem.tree[i["world"]]): 
        persona.s_mem.tree[i["world"]][i["sector"]] = {}
    if i["arena"]: 
      if (i["arena"] not in persona.s_mem.tree[i["world"]]
                                              [i["sector"]]): 
        persona.s_mem.tree[i["world"]][i["sector"]][i["arena"]] = []
    if i["game_object"]: 
      if (i["game_object"] not in persona.s_mem.tree[i["world"]]
                                                    [i["sector"]]
                                                    [i["arena"]]): 
        persona.s_mem.tree[i["world"]][i["sector"]][i["arena"]] += [
                                                             i["game_object"]]

  # 感知事件
  # 我们将感知发生在与人物当前所在竞技场相同的竞技场中的事件。
  curr_arena_path = maze.get_tile_path(persona.scratch.curr_tile, "arena")
  # 我们不会感知相同的事件两次（如果一个对象横跨多个瓦片，则可能发生这种情况）。
  percept_events_set = set()
  # 我们将根据距离对感知进行排序，距离越近，优先级越高。
  percept_events_list = []
  # 首先，我们将所有发生在附近瓦片上的事件放入percept_events_list中。
  for tile in nearby_tiles: 
    tile_details = maze.access_tile(tile)
    if tile_details["events"]: 
      if maze.get_tile_path(tile, "arena") == curr_arena_path:  
        # 计算人物当前瓦片与目标瓦片之间的距离。
        dist = math.dist([tile[0], tile[1]], 
                         [persona.scratch.curr_tile[0], 
                          persona.scratch.curr_tile[1]])
        # 将任何相关事件按距离添加到我们的临时集合/列表中。
        for event in tile_details["events"]: 
          if event not in percept_events_set: 
            percept_events_list += [[dist, event]]
            percept_events_set.add(event)

  # 我们对距离进行排序，并仅感知最接近的persona.scratch.att_bandwidth数量的事件。
  percept_events_list = sorted(percept_events_list, key=itemgetter(0))
  perceived_events = []
  for dist, event in percept_events_list[:persona.scratch.att_bandwidth]: 
    perceived_events += [event]

  # 存储事件。
  # <ret_events>是persona关联内存中的一组<ConceptNode>实例。
  ret_events = []
  for p_event in perceived_events: 
    s, p, o, desc = p_event
    if not p: 
      # 如果对象不存在，则将事件默认为"idle"。
      p = "is"
      o = "idle"
      desc = "idle"
    desc = f"{s.split(':')[-1]} is {desc}"
    p_event = (s, p, o)

    # 我们检索最新的persona.scratch.retention个事件。如果有新事件发生（即p_event不在latest_events中），
    # 那么我们将该事件添加到a_mem中并返回它。
    latest_events = persona.a_mem.get_summarized_latest_events(
                                    persona.scratch.retention)
    if p_event not in latest_events:
      # 首先处理关键词。
      keywords = set()
      sub = p_event[0]
      obj = p_event[2]
      if ":" in p_event[0]: 
        sub = p_event[0].split(":")[-1]
      if ":" in p_event[2]: 
        obj = p_event[2].split(":")[-1]
      keywords.update([sub, obj])

      # 获取事件嵌入。
      desc_embedding_in = desc
      if "(" in desc: 
        desc_embedding_in = (desc_embedding_in.split("(")[1]
                                              .split(")")[0]
                                              .strip())
      if desc_embedding_in in persona.a_mem.embeddings: 
        event_embedding = persona.a_mem.embeddings[desc_embedding_in]
      else: 
        event_embedding = get_embedding(desc_embedding_in)
      event_embedding_pair = (desc_embedding_in, event_embedding)
      
      # 获取事件“poignancy”。
      event_poignancy = generate_poig_score(persona, 
                                            "event", 
                                            desc_embedding_in)

      # 如果观察到了persona的自我聊天，我们将在此处将其包含在persona的记忆中。
      chat_node_ids = []
      if p_event[0] == f"{persona.name}" and p_event[1] == "chat with": 
        curr_event = persona.scratch.act_event
        if persona.scratch.act_description in persona.a_mem.embeddings: 
          chat_embedding = persona.a_mem.embeddings[
                             persona.scratch.act_description]
        else: 
          chat_embedding = get_embedding(persona.scratch
                                                .act_description)
        chat_embedding_pair = (persona.scratch.act_description, 
                               chat_embedding)
        chat_poignancy = generate_poig_score(persona, "chat", 
                                             persona.scratch.act_description)
        chat_node = persona.a_mem.add_chat(persona.scratch.curr_time, None,
                      curr_event[0], curr_event[1], curr_event[2], 
                      persona.scratch.act_description, keywords, 
                      chat_poignancy, chat_embedding_pair, 
                      persona.scratch.chat)
        chat_node_ids = [chat_node.node_id]

      # 最后，将当前事件添加到代理的记忆中。
      ret_events += [persona.a_mem.add_event(persona.scratch.curr_time, None,
                           s, p, o, desc, keywords, event_poignancy, 
                           event_embedding_pair, chat_node_ids)]
      persona.scratch.importance_trigger_curr -= event_poignancy
      persona.scratch.importance_ele_n += 1

  return ret_events