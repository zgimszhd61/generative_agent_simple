
"""
作者: Joon Sung Park (joonspk@stanford.edu)
文件: converse.py
描述: 一个用于生成对话的额外认知模块。
"""

import sys
import datetime
sys.path.append('../')  # 添加模块搜索路径

# 从自定义的模块中导入所需函数和类
from opensource.generative_agent_simple.backend.global_methods import *
from persona.memory_structures.spatial_memory import *
from persona.memory_structures.associative_memory import *
from persona.memory_structures.scratch import *
from persona.cognitive_modules.retrieve import *
from persona.prompt_template.run_gpt_prompt import *

def generate_agent_chat_summarize_ideas(init_persona, target_persona, retrieved, curr_context):
    """生成并总结对话主意。

    参数:
    init_persona: 初始个人对象
    target_persona: 目标个人对象
    retrieved: 检索到的信息
    curr_context: 当前上下文信息

    返回:
    summarized_idea: 总结的对话主意
    """
    all_embedding_keys = [i.embedding_key for val in retrieved.values() for i in val]
    all_embedding_key_str = "\n".join(all_embedding_keys)

    try:
        summarized_idea = run_gpt_prompt_agent_chat_summarize_ideas(init_persona, target_persona, all_embedding_key_str, curr_context)[0]
    except:
        summarized_idea = ""

    return summarized_idea

def generate_summarize_agent_relationship(init_persona, target_persona, retrieved):
    """生成并总结个人关系。

    参数:
    init_persona: 初始个人对象
    target_persona: 目标个人对象
    retrieved: 检索到的信息

    返回:
    summarized_relationship: 总结的个人关系
    """
    all_embedding_keys = [i.embedding_key for val in retrieved.values() for i in val]
    all_embedding_key_str = "\n".join(all_embedding_keys)

    summarized_relationship = run_gpt_prompt_agent_chat_summarize_relationship(init_persona, target_persona, all_embedding_key_str)[0]
    return summarized_relationship

def generate_agent_chat(maze, init_persona, target_persona, curr_context, init_summ_idea, target_summ_idea):
    """生成对话。

    参数:
    maze: 迷宫对象
    init_persona: 初始个人对象
    target_persona: 目标个人对象
    curr_context: 当前上下文信息
    init_summ_idea: 初始总结的主意
    target_summ_idea: 目标总结的主意

    返回:
    summarized_idea: 生成的对话
    """
    summarized_idea = run_gpt_prompt_agent_chat(maze, init_persona, target_persona, curr_context, init_summ_idea, target_summ_idea)[0]

    for i in summarized_idea:
        print(i)
    
    return summarized_idea

def agent_chat_v1(maze, init_persona, target_persona):
    """版本1的对话生成函数。

    参数:
    maze: 迷宫对象
    init_persona: 初始个人对象
    target_persona: 目标个人对象

    返回:
    生成的对话
    """
    curr_context = (f"{init_persona.scratch.name} "
                    f"在 {init_persona.scratch.act_description} 时 "
                    f"看到 {target_persona.scratch.name} "
                    f"{target_persona.scratch.act_description}。\n")
    curr_context += (f"{init_persona.scratch.name} 正在考虑与 {target_persona.scratch.name} 开始对话。")

    summarized_ideas = []
    part_pairs = [(init_persona, target_persona), (target_persona, init_persona)]

    for p_1, p_2 in part_pairs:
        focal_points = [f"{p_2.scratch.name}"]
        retrieved = new_retrieve(p_1, focal_points, 50)
        relationship = generate_summarize_agent_relationship(p_1, p_2, retrieved)
        focal_points = [f"{relationship}", f"{p_2.scratch.name} 是 {p_2.scratch.act_description}"]
        retrieved = new_retrieve(p_1, focal_points, 25)
        summarized_idea = generate_agent_chat_summarize_ideas(p_1, p_2, retrieved, curr_context)
        summarized_ideas.append(summarized_idea)

    return generate_agent_chat(maze, init_persona, target_persona, curr_context, summarized_ideas[0], summarized_ideas[1])

def generate_one_utterance(maze, init_persona, target_persona, retrieved, curr_chat):
    """生成一次对话。

    参数:
    maze: 迷宫对象
    init_persona: 初始个人对象
    target_persona: 目标个人对象
    retrieved: 检索到的信息
    curr_chat: 当前对话内容

    返回:
    utterance: 生成的话语
    end: 对话是否结束
    """
    curr_context = (f"{init_persona.scratch.name} "
                    f"在 {init_persona.scratch.act_description} 时 "
                    f"看到 {target_persona.scratch.name} "
                    f"{target_persona.scratch.act_description}。\n")
    curr_context += (f"{init_persona.scratch.name} 正在与 {target_persona.scratch.name} 开始对话。")

    x = run_gpt_generate_iterative_chat_utt(maze, init_persona, target_persona, retrieved, curr_context, curr_chat)[0]

    return x["utterance"], x["end"]

def agent_chat_v2(maze, init_persona, target_persona):
    """版本2的对话生成函数。

    参数:
    maze: 迷宫对象
    init_persona: 初始个人对象
    target_persona: 目标个人对象

    返回:
    生成的对话
    """
    curr_chat = []

    for i in range(8):
        focal_points = [f"{target_persona.scratch.name}"]
        retrieved = new_retrieve(init_persona, focal_points, 50)
        relationship = generate_summarize_agent_relationship(init_persona, target_persona, retrieved)
        last_chat = "".join([": ".join(i) + "\n" for i in curr_chat[-4:]])

        if last_chat:
            focal_points = [f"{relationship}", f"{target_persona.scratch.name} 是 {target_persona.scratch.act_description}", last_chat]
        else:
            focal_points = [f"{relationship}", f"{target_persona.scratch.name} 是 {target_persona.scratch.act_description}"]

        retrieved = new_retrieve(init_persona, focal_points, 15)
        utt, end = generate_one_utterance(maze, init_persona, target_persona, retrieved, curr_chat)

        curr_chat.append([init_persona.scratch.name, utt])
        if end:
            break

        focal_points = [f"{init_persona.scratch.name}"]
        retrieved = new_retrieve(target_persona, focal_points, 50)
        relationship = generate_summarize_agent_relationship(target_persona, init_persona, retrieved)
        last_chat = "".join([": ".join(i) + "\n" for i in curr_chat[-4:]])

        if last_chat:
            focal_points = [f"{relationship}", f"{init_persona.scratch.name} 是 {init_persona.scratch.act_description}", last_chat]
        else:
            focal_points = [f"{relationship}", f"{init_persona.scratch.name} 是 {init_persona.scratch.act_description}"]

        retrieved = new_retrieve(target_persona, focal_points, 15)
        utt, end = generate_one_utterance(maze, target_persona, init_persona, retrieved, curr_chat)

        curr_chat.append([target_persona.scratch.name, utt])
        if end:
            break

    for row in curr_chat:
        print(row)

    return curr_chat

# 生成摘要的函数，根据给定的角色、节点和问题
def generate_summarize_ideas(persona, nodes, question):
    statements = ""
    for n in nodes:
        statements += f"{n.embedding_key}\n"  # 提取节点的嵌入键
    summarized_idea = run_gpt_prompt_summarize_ideas(persona, statements, question)[0]  # 运行摘要生成函数
    return summarized_idea

# 生成下一行对话的函数
def generate_next_line(persona, interlocutor_desc, curr_convo, summarized_idea):
    prev_convo = ""  # 原始对话
    for row in curr_convo: 
        prev_convo += f'{row[0]}: {row[1]}\n'  # 将对话行连接起来

    next_line = run_gpt_prompt_generate_next_convo_line(persona, 
                                                        interlocutor_desc, 
                                                        prev_convo, 
                                                        summarized_idea)[0]  # 运行生成下一行对话函数
    return next_line

# 生成内心想法的函数
def generate_inner_thought(persona, whisper):
    inner_thought = run_gpt_prompt_generate_whisper_inner_thought(persona, whisper)[0]  # 运行生成内心想法函数
    return inner_thought

# 生成动作事件三元组的函数
def generate_action_event_triple(act_desp, persona): 
    if debug: 
        print ("GNS FUNCTION: <generate_action_event_triple>")  # 如果是调试模式，打印调试信息
    return run_gpt_prompt_event_triple(act_desp, persona)[0]  # 运行生成动作事件三元组函数

# 生成情感得分的函数
def generate_poig_score(persona, event_type, description): 
    if debug: 
        print ("GNS FUNCTION: <generate_poig_score>")  # 如果是调试模式，打印调试信息

    if "is idle" in description: 
        return 1  # 如果描述中包含"is idle"，返回得分为1

    if event_type == "event" or event_type == "thought": 
        return run_gpt_prompt_event_poignancy(persona, description)[0]  # 运行生成情感得分函数
    elif event_type == "chat": 
        return run_gpt_prompt_chat_poignancy(persona, 
                           persona.scratch.act_description)[0]  # 运行生成情感得分函数

# 通过私语加载历史的函数
def load_history_via_whisper(personas, whispers):
    for count, row in enumerate(whispers): 
        persona = personas[row[0]]
        whisper = row[1]

        thought = generate_inner_thought(persona, whisper)  # 生成内心想法

        created = persona.scratch.curr_time
        expiration = persona.scratch.curr_time + datetime.timedelta(days=30)
        s, p, o = generate_action_event_triple(thought, persona)  # 生成动作事件三元组
        keywords = set([s, p, o])
        thought_poignancy = generate_poig_score(persona, "event", whisper)  # 生成情感得分
        thought_embedding_pair = (thought, get_embedding(thought))
        persona.a_mem.add_thought(created, expiration, s, p, o, 
                                  thought, keywords, thought_poignancy, 
                                  thought_embedding_pair, None)

# 开始对话会话的函数
def open_convo_session(persona, convo_mode): 
    if convo_mode == "analysis": 
        curr_convo = []
        interlocutor_desc = "Interviewer"

        while True: 
            line = input("Enter Input: ")  # 输入对话行
            if line == "end_convo": 
                break

            if int(run_gpt_generate_safety_score(persona, line)[0]) >= 8: 
                print (f"{persona.scratch.name} is a computational agent, and as such, it may be inappropriate to attribute human agency to the agent in your communication.")  # 如果安全得分大于等于8，打印警告信息        

            else: 
                retrieved = new_retrieve(persona, [line], 50)[line]  # 重新检索相关信息
                summarized_idea = generate_summarize_ideas(persona, retrieved, line)  # 生成摘要
                curr_convo += [[interlocutor_desc, line]]  # 添加对话行

                next_line = generate_next_line(persona, interlocutor_desc, curr_convo, summarized_idea)  # 生成下一行对话
                curr_convo += [[persona.scratch.name, next_line]]  # 添加对话行

    elif convo_mode == "whisper": 
        whisper = input("Enter Input: ")  # 输入私语
        thought = generate_inner_thought(persona, whisper)  # 生成内心想法

        created = persona.scratch.curr_time
        expiration = persona.scratch.curr_time + datetime.timedelta(days=30)
        s, p, o = generate_action_event_triple(thought, persona)  # 生成动作事件三元组
        keywords = set([s, p, o])
        thought_poignancy = generate_poig_score(persona, "event", whisper)  # 生成情感得分
        thought_embedding_pair = (thought, get_embedding(thought))
        persona.a_mem.add_thought(created, expiration, s, p, o, 
                                  thought, keywords, thought_poignancy, 
                                  thought_embedding_pair, None)