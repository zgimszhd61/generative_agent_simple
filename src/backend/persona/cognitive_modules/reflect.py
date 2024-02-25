"""
作者：朱恩成
文件：reflect.py
描述：定义了生成式代理的“反思”模块。
"""
import sys
sys.path.append('../../')

import datetime
import random

from numpy import dot
from numpy.linalg import norm

from opensource.generative_agent_simple.backend.global_methods import *
from persona.prompt_template.run_gpt_prompt import *
from persona.prompt_template.gpt_structure import *
from persona.cognitive_modules.retrieve import *

def generate_focal_points(persona, n=3): 
    """
    生成关注焦点。
    
    参数：
        persona: 当前的Persona对象
        n: 生成的关注焦点数量，默认为3
        
    返回：
        生成的关注焦点列表
    """
    if debug: 
        print ("GNS FUNCTION: <generate_focal_points>")
  
    # 获取所有非闲置事件和思考节点
    nodes = [[i.last_accessed, i]
                for i in persona.a_mem.seq_event + persona.a_mem.seq_thought
                if "idle" not in i.embedding_key]

    # 按最后访问时间排序
    nodes = sorted(nodes, key=lambda x: x[0])
    nodes = [i for created, i in nodes]

    # 构建待输入的语句
    statements = ""
    for node in nodes[-1 * persona.scratch.importance_ele_n:]: 
        statements += node.embedding_key + "\n"

    # 运行GPT模型生成关注焦点
    return run_gpt_prompt_focal_pt(persona, statements, n)[0]


def generate_insights_and_evidence(persona, nodes, n=5): 
    """
    生成见解和证据。
    
    参数：
        persona: 当前的Persona对象
        nodes: 用于生成见解和证据的节点列表
        n: 生成的见解数量，默认为5
        
    返回：
        生成的见解和证据字典
    """
    if debug: 
        print ("GNS FUNCTION: <generate_insights_and_evidence>")

    # 构建待输入的语句
    statements = ""
    for count, node in enumerate(nodes): 
        statements += f'{str(count)}. {node.embedding_key}\n'

    # 运行GPT模型生成见解和指导
    ret = run_gpt_prompt_insight_and_guidance(persona, statements, n)[0]

    try: 
        # 将生成的证据转换为节点ID
        for thought, evi_raw in ret.items(): 
            evidence_node_id = [nodes[i].node_id for i in evi_raw]
            ret[thought] = evidence_node_id
        return ret
    except: 
        return {"this is blank": "node_1"} 


def generate_action_event_triple(act_desp, persona): 
    """
    生成动作事件三元组。
    
    参数：
        act_desp: 动作描述（例如，“睡觉”）
        persona: 当前的Persona对象
        
    返回：
        生成的动作事件三元组的字符串表示
    """
    if debug: 
        print ("GNS FUNCTION: <generate_action_event_triple>")
    return run_gpt_prompt_event_triple(act_desp, persona)[0]


def generate_poig_score(persona, event_type, description): 
    """
    生成事件或思考的强烈程度得分。
    
    参数：
        persona: 当前的Persona对象
        event_type: 事件类型（"event"、"thought"或"chat"）
        description: 事件或思考的描述
        
    返回：
        生成的强烈程度得分
    """
    if debug: 
        print ("GNS FUNCTION: <generate_poig_score>")

    if "is idle" in description: 
        return 1

    if event_type == "event" or event_type == "thought": 
        return run_gpt_prompt_event_poignancy(persona, description)[0]
    elif event_type == "chat": 
        return run_gpt_prompt_chat_poignancy(persona, 
                               persona.scratch.act_description)[0]


def generate_planning_thought_on_convo(persona, all_utt):
    """
    在对话上生成规划思考。
    
    参数：
        persona: 当前的Persona对象
        all_utt: 所有对话内容
        
    返回：
        生成的规划思考
    """
    if debug: 
        print ("GNS FUNCTION: <generate_planning_thought_on_convo>")
    return run_gpt_prompt_planning_thought_on_convo(persona, all_utt)[0]


def generate_memo_on_convo(persona, all_utt):
    """
    在对话上生成备忘录。
    
    参数：
        persona: 当前的Persona对象
        all_utt: 所有对话内容
        
    返回：
        生成的备忘录
    """
    if debug: 
        print ("GNS FUNCTION: <generate_memo_on_convo>")
    return run_gpt_prompt_memo_on_convo(persona, all_utt)[0]


def run_reflect(persona):
    """
    运行反思过程。生成关注焦点、检索相关节点，并生成见解和思考。

    参数：
        persona: 当前的Persona对象
    返回：
        无
    """
    # 生成关注焦点
    focal_points = generate_focal_points(persona, 3)
    # 检索与每个关注焦点相关的节点
    retrieved = new_retrieve(persona, focal_points)

    # 对于每个关注焦点，生成见解并保存到代理的内存中
    for focal_pt, nodes in retrieved.items(): 
        xx = [i.embedding_key for i in nodes]
        for xxx in xx: print (xxx)

        thoughts = generate_insights_and_evidence(persona, nodes, 5)
        for thought, evidence in thoughts.items(): 
            created = persona.scratch.curr_time
            expiration = persona.scratch.curr_time + datetime.timedelta(days=30)
            s, p, o = generate_action_event_triple(thought, persona)
            keywords = set([s, p, o])
            thought_poignancy = generate_poig_score(persona, "thought", thought)
            thought_embedding_pair = (thought, get_embedding(thought))

            persona.a_mem.add_thought(created, expiration, s, p, o, 
                                      thought, keywords, thought_poignancy, 
                                      thought_embedding_pair, evidence)


def reflection_trigger(persona): 
    """
    确定是否触发反思。

    参数：
        persona: 当前的Persona对象
    返回：
        如果触发反思则返回True，否则返回False
    """
    print (persona.scratch.name, "persona.scratch.importance_trigger_curr::", persona.scratch.importance_trigger_curr)
    print (persona.scratch.importance_trigger_max)

    if (persona.scratch.importance_trigger_curr <= 0 and 
        [] != persona.a_mem.seq_event + persona.a_mem.seq_thought): 
        return True 
    return False


def reset_reflection_counter(persona): 
    """
    重置反思触发计数器。

    参数：
        persona: 当前的Persona对象
    返回：
        无
    """
    persona_imt_max = persona.scratch.importance_trigger_max
    persona.scratch.importance_trigger_curr = persona_imt_max
    persona.scratch.importance_ele_n = 0


def reflect(persona):
    """
    Persona的主要反思模块。首先检查触发条件是否满足，如果满足则运行反思并重置相关计数器。

    参数：
        persona: 当前的Persona对象
    返回：
        无
    """
    if reflection_trigger(persona): 
        run_reflect(persona)
        reset_reflection_counter(persona)

    if persona.scratch.chatting_end_time: 
        if persona.scratch.curr_time + datetime.timedelta(0,10) == persona.scratch.chatting_end_time: 
            all_utt = ""
            if persona.scratch.chat: 
                for row in persona.scratch.chat:  
                    all_utt += f"{row[0]}: {row[1]}\n"

            evidence = [persona.a_mem.get_last_chat(persona.scratch.chatting_with).node_id]

            planning_thought = generate_planning_thought_on_convo(persona, all_utt)
            planning_thought = f"For {persona.scratch.name}'s planning: {planning_thought}"

            created = persona.scratch.curr_time
            expiration = persona.scratch.curr_time + datetime.timedelta(days=30)
            s, p, o = generate_action_event_triple(planning_thought, persona)
            keywords = set([s, p, o])
            thought_poignancy = generate_poig_score(persona, "thought", planning_thought)
            thought_embedding_pair = (planning_thought, get_embedding(planning_thought))

            persona.a_mem.add_thought(created, expiration, s, p, o, 
                                      planning_thought, keywords, thought_poignancy, 
                                      thought_embedding_pair, evidence)

            memo_thought = generate_memo_on_convo(persona, all_utt)
            memo_thought = f"{persona.scratch.name} {memo_thought}"

            created = persona.scratch.curr_time
            expiration = persona.scratch.curr_time + datetime.timedelta(days=30)
            s, p, o = generate_action_event_triple(memo_thought, persona)
            keywords = set([s, p, o])
            thought_poignancy = generate_poig_score(persona, "thought", memo_thought)
            thought_embedding_pair = (memo_thought, get_embedding(memo_thought))

            persona.a_mem.add_thought(created, expiration, s, p, o, 
                                      memo_thought, keywords, thought_poignancy, 
                                      thought_embedding_pair, evidence)