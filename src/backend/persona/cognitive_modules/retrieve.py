"""
作者: Joon Sung Park (joonspk@stanford.edu)

文件: retrieve.py
描述: 这定义了生成型代理的“检索”模块。
"""
import sys
sys.path.append('../../')

from opensource.generative_agent_simple.backend.global_methods import *
from persona.prompt_template.gpt_structure import *

from numpy import dot
from numpy.linalg import norm

def retrieve(persona, perceived): 
  """
  此函数将个人所感知的事件作为输入，并返回一组相关事件和思考，个人在规划时需要将其考虑为上下文。

  输入: 
    perceived: 一个事件<ConceptNode>的列表，表示个人周围发生的事件之一。 这里包括由att_bandwidth和retention超参数控制的事件。
  输出: 
    retrieved: 一个字典的字典。第一层指定一个事件，而后一层指定相关的“curr_event”、“events”和“thoughts”。
  """
  # 我们分别检索事件和思考。
  retrieved = dict()
  for event in perceived: 
    retrieved[event.description] = dict()
    retrieved[event.description]["curr_event"] = event
    
    relevant_events = persona.a_mem.retrieve_relevant_events(
                        event.subject, event.predicate, event.object)
    retrieved[event.description]["events"] = list(relevant_events)

    relevant_thoughts = persona.a_mem.retrieve_relevant_thoughts(
                          event.subject, event.predicate, event.object)
    retrieved[event.description]["thoughts"] = list(relevant_thoughts)
    
  return retrieved


def cos_sim(a, b): 
  """
  此函数计算两个输入向量'a'和'b'之间的余弦相似度。余弦相似度是一个向量空间的两个非零向量之间的相似度度量，它衡量它们之间的夹角的余弦。

  输入: 
    a: 1-D数组对象 
    b: 1-D数组对象 
  输出: 
    表示输入向量'a'和'b'之间余弦相似度的标量值。
  
  示例输入: 
    a = [0.3, 0.2, 0.5]
    b = [0.2, 0.2, 0.5]
  """
  return dot(a, b)/(norm(a)*norm(b))


def normalize_dict_floats(d, target_min, target_max):
  """
  此函数将给定字典'd'的浮点值归一化到目标最小值和最大值之间。归一化通过将值缩放到目标范围来完成，同时保持原始值之间的相对比例。

  输入: 
    d: 字典。需要归一化浮点值的输入字典。
    target_min: 整数或浮点数。应将原始值缩放到的最小值。
    target_max: 整数或浮点数。应将原始值缩放到的最大值。
  输出: 
    d: 一个新字典，其键与输入相同，但浮点值在目标_min和目标_max之间归一化。

  示例输入: 
    d = {'a':1.2,'b':3.4,'c':5.6,'d':7.8}
    target_min = -5
    target_max = 5
  """
  min_val = min(val for val in d.values())
  max_val = max(val for val in d.values())
  range_val = max_val - min_val

  if range_val == 0: 
    for key, val in d.items(): 
      d[key] = (target_max - target_min)/2
  else: 
    for key, val in d.items():
      d[key] = ((val - min_val) * (target_max - target_min) 
                / range_val + target_min)
  return d


def top_highest_x_values(d, x):
  """
  此函数接受字典'd'和整数'x'作为输入，并从具有最高值的输入字典'd'中提取前'x'个键-值对，然后返回一个新字典。

  输入: 
    d: 字典。要从中提取具有最高值的'top x'键-值对的输入字典'd'。
    x: 整数。要从输入字典中提取具有最高值的'top x'键-值对的数量。
  输出: 
    一个新字典，其中包含输入字典'd'中具有最高值的'top x'键-值对。

  示例输入: 
    d = {'a':1.2,'b':3.4,'c':5.6,'d':7.8}
    x = 3
  """
  top_v = dict(sorted(d.items(), 
                      key=lambda item: item[1], 
                      reverse=True)[:x])
  return top_v


def extract_recency(persona, nodes):
  """
  获取当前Persona对象和按时间顺序排列的节点列表，并输出一个字典，其中计算了最近度量分数。

  输入: 
    persona: 我们正在检索其记忆的当前persona。 
    nodes: 按时间顺序排列的节点对象列表。 
  输出: 
    recency_out: 一个字典，其键是node.node_id，其值是表示最近度量分数的浮点数。 
  """
  recency_vals = [persona.scratch.recency_decay ** i 
                  for i in range(1, len(nodes) + 1)]
  
  recency_out = dict()
  for count, node in enumerate(nodes): 
    recency_out[node.node_id] = recency_vals[count]

  return recency_out


def extract_importance(persona, nodes):
  """
  获取当前Persona对象和按时间顺序排列的节点列表，并输出一个字典，其中计算了重要性度量分数。

  输入: 
    persona: 我们正在检索其记忆的当前persona。 
    nodes: 按时间顺序排列的节点对象列表。 
  输出: 
    importance_out: 一个字典，其键是node.node_id，其值是表示重要性度量分数的浮点数。
  """
  importance_out = dict()
  for count, node in enumerate(nodes): 
    importance_out[node.node_id] = node.poignancy

  return importance_out


def extract_relevance(persona, nodes, focal_pt): 
  """
  获取当前Persona对象、按时间顺序排列的节点列表和焦点字符串，并输出一个字典，其中计算了相关度分数。

  输入: 
    persona: 我们正在检索其记忆的当前persona。 
    nodes: 按时间顺序排列的节点对象列表。 
    focal_pt: 描述当前思考或关注事件的字符串。 
  输出: 
    relevance_out: 一个字典，其键是node.node_id，其值是表示相关度分数的浮点数。 
  """
  focal_embedding = get_embedding(focal_pt)

  relevance_out = dict()
  for count, node in enumerate(nodes): 
    node_embedding = persona.a_mem.embeddings[node.embedding_key]
    relevance_out[node.node_id] = cos_sim(node_embedding, focal_embedding)

  return relevance_out


def new_retrieve(persona, focal_points, n_count=30): 
  """
  给定当前persona和焦点（焦点是正在检索的事件或思考），我们检索每个焦点的一组节点，并返回一个字典。

  输入: 
    persona: 我们正在检索其记忆的当前persona对象。 
    focal_points: 焦点列表（当前检索的事件或思考的描述字符串）。 
    n_count: 整数。要检索的最大节点数。
  输出: 
    retrieved: 一个字典，其键是焦点字符串，其值是代理的关联记忆中节点对象的列表。

  示例输入:
    persona = <persona>对象 
    focal_points = ["你好吗？", "简在池塘里游泳"]
  """
  # <retrieved>是我们要返回的主字典
  retrieved = dict() 
  for focal_pt in focal_points: 
    # 获取代理记忆中的所有节点（思考和事件），并按创建日期排序。
    # 你也可以想象获取原始对话，但现在。 
    nodes = [[i.last_accessed, i]
              for i in persona.a_mem.seq_event + persona.a_mem.seq_thought
              if "空闲" not in i.embedding_key]
    nodes = sorted(nodes, key=lambda x: x[0])
    nodes = [i for created, i in nodes]

    # 计算组件字典并将其归一化。
    recency_out = extract_recency(persona, nodes)
    recency_out = normalize_dict_floats(recency_out, 0, 1)
    importance_out = extract_importance(persona, nodes)
    importance_out = normalize_dict_floats(importance_out, 0, 1)  
    relevance_out = extract_relevance(persona, nodes, focal_pt)
    relevance_out = normalize_dict_floats(relevance_out, 0, 1)

    # 计算最终得分，结合组件值。
    # 注意: 尝试不同的权重。[1, 1, 1]倾向于工作得相当好，但在将来，这些权重可能应该通过类似RL的过程来学习，
    # 也许通过RL类似的过程学习。
    # gw = [1, 1, 1]
    # gw = [1, 2, 1]
    gw = [0.5, 3, 2]
    master_out = dict()
    for key in recency_out.keys(): 
      master_out[key] = (persona.scratch.recency_w*recency_out[key]*gw[0] 
                     + persona.scratch.relevance_w*relevance_out[key]*gw[1] 
                     + persona.scratch.importance_w*importance_out[key]*gw[2])

    master_out = top_highest_x_values(master_out, len(master_out.keys()))
    for key, val in master_out.items(): 
      print (persona.a_mem.id_to_node[key].embedding_key, val)
      print (persona.scratch.recency_w*recency_out[key]*1, 
             persona.scratch.relevance_w*relevance_out[key]*1, 
             persona.scratch.importance_w*importance_out[key]*1)

    # 提取最高x个值。
    # <master_out>具有节点id的键和浮点数的值。一旦我们获得了最高x个值，我们想将节点id转换为节点，并返回节点列表。
    master_out = top_highest_x_values(master_out, n_count)
    master_nodes = [persona.a_mem.id_to_node[key] 
                    for key in list(master_out.keys())]

    for n in master_nodes: 
      n.last_accessed = persona.scratch.curr_time
      
    retrieved[focal_pt] = master_nodes

  return retrieved
