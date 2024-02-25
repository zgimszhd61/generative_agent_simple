"""
作者: Joon Sung Park (joonspk@stanford.edu)

文件: plan.py
描述: 定义了生成式智能体的“计划”模块。
"""
import datetime
import math
import random 
import sys
import time
sys.path.append('../../')

from opensource.generative_agent_simple.backend.global_methods import *
from persona.prompt_template.run_gpt_prompt import *
from persona.cognitive_modules.retrieve import *
from persona.cognitive_modules.converse import *

##############################################################################
# 第二章: 生成
##############################################################################

def generate_wake_up_hour(persona):
  """
  生成角色醒来的时间。这是生成角色每日计划的一个重要部分。

  角色状态: 身份稳定集, 生活方式, 名字

  输入: 
    persona: Persona类实例 
  输出: 
    表示角色醒来小时的整数
  示例输出: 
    8
  """
  if debug: print ("GNS FUNCTION: <generate_wake_up_hour>")
  return int(run_gpt_prompt_wake_up_hour(persona)[0])


def generate_first_daily_plan(persona, wake_up_hour): 
  """
  生成角色的每日计划。基本上是跨越一天的长期规划。返回一个列表，包含角色今天将要采取的行动。
  通常以以下形式呈现: '在早上6:00醒来并完成早晨的日常任务', '在早上7:00吃早餐',.. 
  注意，这些行动不带句号。

  角色状态: 身份稳定集, 生活方式, 当前日期, 名字

  输入: 
    persona: Persona类实例 
    wake_up_hour: 一个整数，表示角色醒来的小时数 
                  (例如，8)
  输出: 
    大致行动的每日计划列表。
  示例输出: 
    ['在早上6:00醒来并完成早晨的日常任务', 
     '在早上6:30吃早餐并刷牙',
     '从早上8:00开始绘画项目直到中午12:00', 
     '在中午12:00吃午餐', 
     '在下午2:00至4:00休息并看电视', 
     '从下午4:00至6:00继续绘画项目', 
     '在晚上6:00吃晚餐', '从晚上7:00至8:00看电视']
  """
  if debug: print ("GNS FUNCTION: <generate_first_daily_plan>")
  return run_gpt_prompt_daily_plan(persona, wake_up_hour)[0]


def generate_hourly_schedule(persona, wake_up_hour): 
  """
  基于每日要求，逐小时创建一个小时计划。每个小时的行动形式如下: "她在床上睡觉"
  
  输出基本上是为了完成这样的短语，“x在...”

  角色状态: 身份稳定集, 每日计划

  输入: 
    persona: Persona类实例 
    wake_up_hour: 角色的整数形式的醒来小时数。  
  输出: 
    包含活动及其持续时间（分钟）的列表: 
  示例输出: 
    [['睡觉', 360], ['醒来并开始早晨的日常任务', 60], 
     ['吃早餐', 60],..
  """
  if debug: print ("GNS FUNCTION: <generate_hourly_schedule>")

  hour_str = ["00:00 AM", "01:00 AM", "02:00 AM", "03:00 AM", "04:00 AM", 
              "05:00 AM", "06:00 AM", "07:00 AM", "08:00 AM", "09:00 AM", 
              "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", 
              "03:00 PM", "04:00 PM", "05:00 PM", "06:00 PM", "07:00 PM",
              "08:00 PM", "09:00 PM", "10:00 PM", "11:00 PM"]
  n_m1_activity = []
  diversity_repeat_count = 3
  for i in range(diversity_repeat_count): 
    n_m1_activity_set = set(n_m1_activity)
    if len(n_m1_activity_set) < 5: 
      n_m1_activity = []
      for count, curr_hour_str in enumerate(hour_str): 
        if wake_up_hour > 0: 
          n_m1_activity += ["睡觉"]
          wake_up_hour -= 1
        else: 
          n_m1_activity += [run_gpt_prompt_generate_hourly_schedule(
                          persona, curr_hour_str, n_m1_activity, hour_str)[0]]
  
  # 第1步。将每小时计划压缩为以下格式: 
  # 整数表示小时数。它们应该加起来为24。 
  # [['睡觉', 6], ['醒来并开始早晨的日常任务', 1], 
  # ['吃早餐', 1], ['准备好一天的工作', 1], 
  # ['工作绘画', 2], ['休息一下', 1], 
  # ['吃午餐', 1], ['工作绘画', 3], 
  # ['休息一下', 2], ['工作绘画', 2], 
  # ['放松并看电视', 1], ['上床睡觉', 1], ['睡觉', 2]]
  _n_m1_hourly_compressed = []
  prev = None 
  prev_count = 0
  for i in n_m1_activity: 
    if i != prev:
      prev_count = 1 
      _n_m1_hourly_compressed += [[i, prev_count]]
      prev = i
    else: 
      if _n_m1_hourly_compressed: 
        _n_m1_hourly_compressed[-1][1] += 1

  # 第2步。从小时级别扩展到分钟级别
  # [['睡觉', 360], ['醒来并开始早晨的日常任务', 60], 
  # ['吃早餐', 60],..
  n_m1_hourly_compressed = []
  for task, duration in _n_m1_hourly_compressed: 
    n_m1_hourly_compressed += [[task, duration*60]]

  return n_m1_hourly_compressed


def generate_task_decomp(persona, task, duration): 
  """
  给定任务描述，进行任务分解。

  角色状态: 身份稳定集, 当前日期, 名字

  输入: 
    persona: Persona类实例 
    task: 手头任务的描述，字符串形式
          (例如，"醒来并开始早晨的日常任务")
    duration: 整数，表示任务持续的分钟数
  输出: 
    包含分解任务描述及任务持续时间的列表列表
  示例输出: 
    [['去洗手间', 5], ['穿衣服', 5], 
     ['吃早餐', 15], ['查看电子邮件', 5], 
     ['准备好一天的工作', 15], 
     ['开始绘画', 15]] 

  """
  if debug: print ("GNS FUNCTION: <generate_task_decomp>")
  return run_gpt_prompt_task_decomp(persona, task, duration)[0]


def generate_action_sector(act_desp, persona, maze): 
  """TODO 
  给定角色和任务描述，选择行动区域。 

  角色状态: 身份稳定集, n-1天计划, 每日计划

  输入: 
    act_desp: 新行动的描述 (例如，"睡觉")
    persona: Persona类实例 
  输出: 
    行动区域 (例如，"卧室 2")
  示例输出: 
    "卧室 2"
  """
  if debug: print ("GNS FUNCTION: <generate_action_sector>")
  return run_gpt_prompt_action_sector(act_desp, persona, maze)[0]


def generate_action_arena(act_desp, persona, maze, act_world, act_sector): 
  """TODO 
  给定角色和任务描述，选择行动区域。 

  角色状态: 身份稳定集, n-1天计划, 每日计划

  输入: 
    act_desp: 新行动的描述 (例如，"睡觉")
    persona: Persona类实例 
  输出: 
    行动区域 (例如，"卧室 2")
  示例输出: 
    "卧室 2"
  """
  if debug: print ("GNS FUNCTION: <generate_action_arena>")
  return run_gpt_prompt_action_arena(act_desp, persona, maze, act_world, act_sector)[0]


def generate_action_game_object(act_desp, act_address, persona, maze):
  """TODO
  给定行动描述和行动地址（我们期望行动发生的地址），选择游戏对象之一。 

  角色状态: 身份稳定集, n-1天计划, 每日计划

  输入: 
    act_desp: 行动的描述 (例如，"睡觉")
    act_address: 行动将发生的区域: 
               (例如，"dolores double studio:double studio:卧室 2")
    persona: Persona类实例 
  输出: 
    act_game_object: 
  示例输出: 
    "床"
  """
  if debug: print ("GNS FUNCTION: <generate_action_game_object>")
  if not persona.s_mem.get_str_accessible_arena_game_objects(act_address): 
    return "<随机>"
  return run_gpt_prompt_action_game_object(act_desp, persona, maze, act_address)[0]


def generate_action_pronunciatio(act_desp, persona): 
  """TODO 
  给定行动描述，通过一些快速提示创建一个表情符号字符串描述。 

  实际上不需要来自角色的任何信息。 

  输入: 
    act_desp: 行动的描述 (例如，"睡觉")
    persona: Persona类实例
  输出: 
    一个表情符号字符串，将行动描述转换成表情符号。
  示例输出: 
    "🧈🍞"
  """
  if debug: print ("GNS FUNCTION: <generate_action_pronunciatio>")
  try: 
    x = run_gpt_prompt_pronunciatio(act_desp, persona)[0]
  except: 
    x = "🙂"

  if not x: 
    return "🙂"
  return x


def generate_action_event_triple(act_desp, persona): 
  """TODO 

  输入: 
    act_desp: 行动的描述 (例如，"睡觉")
    persona: Persona类实例
  输出: 
    将行动描述转换成的一串表情符号。
  示例输出: 
    "🧈🍞"
  """
  if debug: print ("GNS FUNCTION: <generate_action_event_triple>")
  return run_gpt_prompt_event_triple(act_desp, persona)[0]


def generate_act_obj_desc(act_game_object, act_desp, persona): 
  if debug: print ("GNS FUNCTION: <generate_act_obj_desc>")
  return run_gpt_prompt_act_obj_desc(act_game_object, act_desp, persona)[0]


def generate_act_obj_event_triple(act_game_object, act_obj_desc, persona): 
  if debug: print ("GNS FUNCTION: <generate_act_obj_event_triple>")
  return run_gpt_prompt_act_obj_event_triple(act_game_object, act_obj_desc, persona)[0]


def generate_convo(maze, init_persona, target_persona): 
  curr_loc = maze.access_tile(init_persona.scratch.curr_tile)

  # convo = run_gpt_prompt_create_conversation(init_persona, target_persona, curr_loc)[0]
  # convo = agent_chat_v1(maze, init_persona, target_persona)
  convo = agent_chat_v2(maze, init_persona, target_persona)
  all_utt = ""

  for row in convo: 
    speaker = row[0]
    utt = row[1]
    all_utt += f"{speaker}: {utt}\n"

  convo_length = math.ceil(int(len(all_utt)/8) / 30)

  if debug: print ("GNS FUNCTION: <generate_convo>")
  return convo, convo_length


def generate_convo_summary(persona, convo): 
  convo_summary = run_gpt_prompt_summarize_conversation(persona, convo)[0]
  return convo_summary


def generate_decide_to_talk(init_persona, target_persona, retrieved): 
  x =run_gpt_prompt_decide_to_talk(init_persona, target_persona, retrieved)[0]
  if debug: print ("GNS FUNCTION: <generate_decide_to_talk>")

  if x == "yes": 
    return True
  else: 
    return False


def generate_decide_to_react(init_persona, target_persona, retrieved): 
  if debug: print ("GNS FUNCTION: <generate_decide_to_react>")
  return run_gpt_prompt_decide_to_react(init_persona, target_persona, retrieved)[0]

import datetime

def generate_new_decomp_schedule(persona, inserted_act, inserted_act_dur, start_hour, end_hour):
    """
    生成新的分解日程。

    Args:
    - persona: <Persona> 实例，表示要编辑日程的个人。
    - inserted_act: 插入的活动描述。
    - inserted_act_dur: 插入的活动持续时间。
    - start_hour: 开始时间（小时）。
    - end_hour: 结束时间（小时）。

    Returns:
    - 生成的新分解日程。
    """
    # 设置函数的核心变量
    p = persona  # 正在编辑日程的个人
    today_min_pass = (int(p.scratch.curr_time.hour) * 60 + int(p.scratch.curr_time.minute) + 1)  # 当天已经过去的分钟数

    # 创建主要活动持续时间和截断活动持续时间
    main_act_dur = []
    truncated_act_dur = []
    dur_sum = 0  # 持续时间总和
    count = 0  # 枚举计数
    truncated_fin = False

    # 遍历每个活动和其持续时间
    for act, dur in p.scratch.f_daily_schedule:
        if (dur_sum >= start_hour * 60) and (dur_sum < end_hour * 60):
            main_act_dur.append([act, dur])
            if dur_sum <= today_min_pass:
                truncated_act_dur.append([act, dur])
            elif dur_sum > today_min_pass and not truncated_fin:
                truncated_act_dur.append([p.scratch.f_daily_schedule[count][0], dur_sum - today_min_pass])
                truncated_act_dur[-1][-1] -= (dur_sum - today_min_pass)
                truncated_fin = True
        dur_sum += dur
        count += 1

    persona_name = persona.name
    main_act_dur = main_act_dur

    # 修改最后一个活动的描述以反映人物的行动
    x = truncated_act_dur[-1][0].split("(")[0].strip() + "（前往" + truncated_act_dur[-1][0].split("(")[-1][:-1] + "）"
    truncated_act_dur[-1][0] = x

    if "(" in truncated_act_dur[-1][0]:
        inserted_act = truncated_act_dur[-1][0].split("(")[0].strip() + "（" + inserted_act + "）"

    truncated_act_dur.append([inserted_act, inserted_act_dur])

    # 设置开始和结束时间
    start_time_hour = datetime.datetime(2022, 10, 31, 0, 0) + datetime.timedelta(hours=start_hour)
    end_time_hour = datetime.datetime(2022, 10, 31, 0, 0) + datetime.timedelta(hours=end_hour)

    # 返回新生成的分解日程
    return run_gpt_prompt_new_decomp_schedule(persona, main_act_dur, truncated_act_dur, start_time_hour, end_time_hour, inserted_act, inserted_act_dur)[0]

def revise_identity(persona):
    """
    修订个人身份。
    """
    # 生成关键字和状态的提取
    p_name = persona.scratch.name
    focal_points = [f"{p_name} {persona.scratch.get_str_curr_date_str()} 的计划。", f"{p_name} 生活中的重要事件。"]
    retrieved = new_retrieve(persona, focal_points)
    statements = "[Statements]\n"
    for key, val in retrieved.items():
        for i in val: 
            statements += f"{i.created.strftime('%A %B %d -- %H:%M %p')}: {i.embedding_key}\n"

    # 获取计划和思考的输入
    plan_prompt = statements + "\n"
    plan_prompt += f"考虑以上陈述，{p_name} 规划 {persona.scratch.curr_time.strftime('%A %B %d')} 的时候，有什么值得记住的吗？"
    plan_prompt += f"如果有任何调度信息，请尽可能具体（包括日期、时间和地点，如果在陈述中说明）。\n\n"
    plan_prompt += f"{p_name} 视角下的回应。"
    plan_note = ChatGPT_single_request(plan_prompt)

    thought_prompt = statements + "\n"
    thought_prompt += f"考虑以上陈述，我们如何总结 {p_name} 近期对这些日子的感受？\n\n"
    thought_prompt += f"{p_name} 视角下的回应。"
    thought_note = ChatGPT_single_request(thought_prompt)

    currently_prompt = f"{(persona.scratch.curr_time - datetime.timedelta(days=1)).strftime('%A %B %d')} 时的 {p_name} 状态：\n"
    currently_prompt += f"{persona.scratch.currently}\n\n"
    currently_prompt += f"{(persona.scratch.curr_time - datetime.timedelta(days=1)).strftime('%A %B %d')} 结束时 {p_name} 的思考：\n" 
    currently_prompt += (plan_note + thought_note).replace('\n', '') + "\n\n"
    currently_prompt += f"{persona.scratch.curr_time.strftime('%A %B %d')} 现在进行中。考虑以上内容，写出 {p_name} 在 {persona.scratch.curr_time.strftime('%A %B %d')} 的状态，反映其对前一天结束时思考的想法。"
    currently_prompt += f"如果有任何调度信息，请尽可能具体（包括日期、时间和地点，如果在陈述中说明）。\n\n"
    currently_prompt += "按以下格式输入：状态：<新状态>"

    new_currently = ChatGPT_single_request(currently_prompt)
    persona.scratch.currently = new_currently

    daily_req_prompt = persona.scratch.get_str_iss() + "\n"
    daily_req_prompt += f"{persona.scratch.curr_time.strftime('%A %B %d')} 是 {persona.scratch.name} 今天的计划大纲（包括一天中的时间，例如中午 12:00 吃午饭，晚上 7 到 8 点看电视）。\n\n"
    daily_req_prompt += "遵循以下格式（列表应包含 4~6 项但不要超过）：\n1. 在 <时间> 醒来并完成早晨例行活动。2. ..."

    new_daily_req = ChatGPT_single_request(daily_req_prompt)
    new_daily_req = new_daily_req.replace('\n', ' ')
    persona.scratch.daily_plan_req = new_daily_req

def _long_term_planning(persona, new_day): 
    """
    制定个人的长期计划。
    """
    # 创建日程和每小时的计划
    wake_up_hour = generate_wake_up_hour(persona)

    if new_day == "First day": 
        persona.scratch.daily_req = generate_first_daily_plan(persona, wake_up_hour)
    elif new_day == "New day":
        revise_identity(persona)
        persona.scratch.daily_req = persona.scratch.daily_req

    persona.scratch.f_daily_schedule = generate_hourly_schedule(persona, wake_up_hour)
    persona.scratch.f_daily_schedule_hourly_org = persona.scratch.f_daily_schedule[:]

    thought = f"{persona.scratch.name} {persona.scratch.curr_time.strftime('%A %B %d')} 的计划："
    for i in persona.scratch.daily_req: 
        thought += f" {i},"
    thought = thought[:-1] + "."
    created = persona.scratch.curr_time
    expiration = persona.scratch.curr_time + datetime.timedelta(days=30)
    s, p, o = persona.scratch.name, "计划", persona.scratch.curr_time.strftime('%A %B %d')
    keywords = set(["计划"])
    thought_poignancy = 5
    thought_embedding_pair = (thought, get_embedding(thought))
    persona.a_mem.add_thought(created, expiration, s, p, o, thought, keywords, thought_poignancy, thought_embedding_pair, None)

def _determine_action(persona, maze): 
    """
    为个人创建下一个行动序列。
    """
    def determine_decomp(act_desp, act_dura):
        """
        确定是否需要分解行动。
        """
        if "sleep" not in act_desp and "bed" not in act_desp: 
            return True
        elif "sleeping" in act_desp or "asleep" in act_desp or "in bed" in act_desp:
            return False
        elif "sleep" in act_desp or "bed" in act_desp: 
            if act_dura > 60: 
                return False
        return True

    curr_index = persona.scratch.get_f_daily_schedule_index()
    curr_index_60 = persona.scratch.get_f_daily_schedule_index(advance=60)

    if curr_index == 0:
        act_desp, act_dura = persona.scratch.f_daily_schedule[curr_index]
        if act_dura >= 60: 
            if determine_decomp(act_desp, act_dura): 
                persona.scratch.f_daily_schedule[curr_index:curr_index+1] = generate_task_decomp(persona, act_desp, act_dura)
        if curr_index_60 + 1 < len(persona.scratch.f_daily_schedule):
            act_desp, act_dura = persona.scratch.f_daily_schedule[curr_index_60+1]
            if act_dura >= 60: 
                if determine_decomp(act_desp, act_dura): 
                    persona.scratch.f_daily_schedule[curr_index_60+1:curr_index_60+2] = generate_task_decomp(persona, act_desp, act_dura)

    if curr_index_60 < len(persona.scratch.f_daily_schedule):
        if persona.scratch.curr_time.hour < 23:
            act_desp, act_dura = persona.scratch.f_daily_schedule[curr_index_60]
            if act_dura >= 60: 
                if determine_decomp(act_desp, act_dura): 
                    persona.scratch.f_daily_schedule[curr_index_60:curr_index_60+1] = generate_task_decomp(persona, act_desp, act_dura)

    for i in persona.scratch.f_daily_schedule: 
        print (i)
    print (curr_index)
    print (len(persona.scratch.f_daily_schedule))
    print (persona.scratch.name)
    print ("------")

    x_emergency = 0
    for i in persona.scratch.f_daily_schedule: 
        x_emergency += i[1]
    if 1440 - x_emergency > 0: 
        print ("x_emergency__AAA", x_emergency)
    persona.scratch.f_daily_schedule += [["sleeping", 1440 - x_emergency]]

    act_desp, act_dura = persona.scratch.f_daily_schedule[curr_index] 



    # Finding the target location of the action and creating action-related
    # variables.
    act_world = maze.access_tile(persona.scratch.curr_tile)["world"]
    # act_sector = maze.access_tile(persona.scratch.curr_tile)["sector"]
    act_sector = generate_action_sector(act_desp, persona, maze)
    act_arena = generate_action_arena(act_desp, persona, maze, act_world, act_sector)
    act_address = f"{act_world}:{act_sector}:{act_arena}"
    act_game_object = generate_action_game_object(act_desp, act_address,
                                                    persona, maze)
    new_address = f"{act_world}:{act_sector}:{act_arena}:{act_game_object}"
    act_pron = generate_action_pronunciatio(act_desp, persona)
    act_event = generate_action_event_triple(act_desp, persona)
    # Persona's actions also influence the object states. We set those up here. 
    act_obj_desp = generate_act_obj_desc(act_game_object, act_desp, persona)
    act_obj_pron = generate_action_pronunciatio(act_obj_desp, persona)
    act_obj_event = generate_act_obj_event_triple(act_game_object, 
                                                    act_obj_desp, persona)

    # Adding the action to persona's queue. 
    persona.scratch.add_new_action(new_address, 
                                    int(act_dura), 
                                    act_desp, 
                                    act_pron, 
                                    act_event,
                                    None,
                                    None,
                                    None,
                                    None,
                                    act_obj_desp, 
                                    act_obj_pron, 
                                    act_obj_event)

import random
import datetime

def _choose_retrieved(persona, retrieved): 
    """
    选择一个事件作为反应的对象。

    参数：
        persona: 当前的<Persona>实例，我们要确定其行动。
        retrieved: 从Persona的联想记忆中检索到的<ConceptNode>字典，
                   其结构如下所示:
                   dictionary[event.description] = 
                     {["curr_event"] = <ConceptNode>, 
                      ["events"] = [<ConceptNode>, ...], 
                      ["thoughts"] = [<ConceptNode>, ...] }
    """
    # 我们不想采取自身事件...目前不需要
    copy_retrieved = retrieved.copy()
    for event_desc, rel_ctx in copy_retrieved.items(): 
        curr_event = rel_ctx["curr_event"]
        if curr_event.subject == persona.name: 
            del retrieved[event_desc]

    # 总是优先选择与persona无关的事件
    priority = []
    for event_desc, rel_ctx in retrieved.items(): 
        curr_event = rel_ctx["curr_event"]
        if (":" not in curr_event.subject 
            and curr_event.subject != persona.name): 
            priority += [rel_ctx]
    if priority: 
        return random.choice(priority)

    # 跳过空闲事件
    for event_desc, rel_ctx in retrieved.items(): 
        curr_event = rel_ctx["curr_event"]
        if "is idle" not in event_desc: 
            priority += [rel_ctx]
    if priority: 
        return random.choice(priority)
    return None


def _should_react(persona, retrieved, personas): 
    """
    确定Persona应该展示何种形式的反应。

    参数：
        persona: 当前的<Persona>实例，我们要确定其行动。
        retrieved: 从Persona的联想记忆中检索到的<ConceptNode>字典，
                   其结构如下所示:
                   dictionary[event.description] = 
                     {["curr_event"] = <ConceptNode>, 
                      ["events"] = [<ConceptNode>, ...], 
                      ["thoughts"] = [<ConceptNode>, ...] }
        personas: 包含所有persona名称为键，<Persona>实例为值的字典。
    """
    # 准备与对话有关的两个内部函数
    def lets_talk(init_persona, target_persona, retrieved):
        # 检查是否有必要对话
        if (not target_persona.scratch.act_address 
            or not target_persona.scratch.act_description
            or not init_persona.scratch.act_address
            or not init_persona.scratch.act_description): 
            return False

        # 如果有任一参与者正在睡觉，则不对话
        if ("sleeping" in target_persona.scratch.act_description 
            or "sleeping" in init_persona.scratch.act_description): 
            return False

        # 如果当前时间是23点，则不对话
        if init_persona.scratch.curr_time.hour == 23: 
            return False

        # 如果目标persona正在等待，则不对话
        if "<waiting>" in target_persona.scratch.act_address: 
            return False

        # 如果有任一参与者正在与其他persona聊天，则不对话
        if (target_persona.scratch.chatting_with 
            or init_persona.scratch.chatting_with): 
            return False

        # 如果与目标persona聊天的缓冲区计数大于0，则不对话
        if (target_persona.name in init_persona.scratch.chatting_with_buffer
            and init_persona.scratch.chatting_with_buffer[target_persona.name] > 0): 
            return False

        # 调用生成的决定对话函数，确定是否对话
        if generate_decide_to_talk(init_persona, target_persona, retrieved): 
            return True

        return False

    def lets_react(init_persona, target_persona, retrieved): 
        # 检查是否有必要做出反应
        if (not target_persona.scratch.act_address 
            or not target_persona.scratch.act_description
            or not init_persona.scratch.act_address
            or not init_persona.scratch.act_description): 
            return False

        # 如果有任一参与者正在睡觉，则不做出反应
        if ("sleeping" in target_persona.scratch.act_description 
            or "sleeping" in init_persona.scratch.act_description): 
            return False

        # 如果当前时间是23点，则不做出反应
        if init_persona.scratch.curr_time.hour == 23: 
            return False

        # 如果目标persona正在等待，则不做出反应
        if "waiting" in target_persona.scratch.act_description: 
            return False

        # 如果初始persona的计划路径为空，则不做出反应
        if init_persona.scratch.planned_path == []:
            return False

        # 如果两个persona的地址不同，则不做出反应
        if (init_persona.scratch.act_address 
            != target_persona.scratch.act_address): 
            return False

        # 调用生成的决定做出反应函数，确定如何做出反应
        react_mode = generate_decide_to_react(init_persona, target_persona, retrieved)

        # 根据不同的反应模式做出不同的反应
        if react_mode == "1": 
            # 如果需要等待，则返回等待直到某个时间点的信息
            wait_until = ((target_persona.scratch.act_start_time 
                + datetime.timedelta(minutes=target_persona.scratch.act_duration - 1))
                .strftime("%B %d, %Y, %H:%M:%S"))
            return f"wait: {wait_until}"
        elif react_mode == "2":
            # 如果需要做其他事情，则返回False
            return False
        else:
            # 其他情况返回False
            return False

    # 如果当前正在和其他persona聊天，默认为不做出反应 
    if persona.scratch.chatting_with: 
        return False
    # 如果正在等待某个事件开始，默认为不做出反应
    if "<waiting>" in persona.scratch.act_address: 
        return False

    # 从检索到的事件中选择一个事件作为重点关注对象
    curr_event = retrieved["curr_event"]
    if ":" not in curr_event.subject: 
        # 这是一个persona事件
        if lets_talk(persona, personas[curr_event.subject], retrieved):
            return f"chat with {curr_event.subject}"
        react_mode = lets_react(persona, personas[curr_event.subject], retrieved)
        return react_mode
    return False


def _create_react(persona, inserted_act, inserted_act_dur,
                  act_address, act_event, chatting_with, chat, chatting_with_buffer,
                  chatting_end_time, 
                  act_pronunciation, act_obj_description, act_obj_pronunciation, 
                  act_obj_event, act_start_time=None): 
    """
    创建一个新的反应行为。

    参数：
        persona: 当前的<Persona>实例，我们要创建反应行为。
        inserted_act: 要插入的行为的描述。
        inserted_act_dur: 插入的行为的持续时间。
        act_address: 行为的地址。
        act_event: 行为的事件。
        chatting_with: 正在与之聊天的persona的名称。
        chat: 聊天内容。
        chatting_with_buffer: 聊天缓冲区。
        chatting_end_time: 聊天结束时间。
        act_pronunciation: 行为的发音。
        act_obj_description: 行为的对象描述。
        act_obj_pronunciation: 行为的对象发音。
        act_obj_event: 行为的对象事件。
        act_start_time: 行为的开始时间。
    """
    p = persona 

    # 计算起始和结束小时
    min_sum = sum(p.scratch.f_daily_schedule_hourly_org[i][1] for i in range(p.scratch.get_f_daily_schedule_hourly_org_index()))
    start_hour = int(min_sum / 60)

    if (p.scratch.f_daily_schedule_hourly_org[p.scratch.get_f_daily_schedule_hourly_org_index()][1] >= 120):
        end_hour = start_hour + p.scratch.f_daily_schedule_hourly_org[p.scratch.get_f_daily_schedule_hourly_org_index()][1] / 60
    elif (p.scratch.f_daily_schedule_hourly_org[p.scratch.get_f_daily_schedule_hourly_org_index()][1] + 
          p.scratch.f_daily_schedule_hourly_org[p.scratch.get_f_daily_schedule_hourly_org_index() + 1][1]): 
        end_hour = start_hour + ((p.scratch.f_daily_schedule_hourly_org[p.scratch.get_f_daily_schedule_hourly_org_index()][1] + 
                  p.scratch.f_daily_schedule_hourly_org[p.scratch.get_f_daily_schedule_hourly_org_index() + 1][1]) / 60)
    else: 
        end_hour = start_hour + 2
    end_hour = int(end_hour)

    # 找到新行为应该插入的位置
    dur_sum = 0
    count = 0 
    start_index = None
    end_index = None
    for act, dur in p.scratch.f_daily_schedule: 
        if dur_sum >= start_hour * 60 and start_index is None:
            start_index = count
        if dur_sum >= end_hour * 60 and end_index is None: 
            end_index = count
        dur_sum += dur
        count += 1

    # 生成新的计划表，并插入新的反应行为
    ret = generate_new_decomp_schedule(p, inserted_act, inserted_act_dur, 
                                       start_hour, end_hour)
    p.scratch.f_daily_schedule[start_index:end_index] = ret
    p.scratch.add_new_action(act_address,
                             inserted_act_dur,
                             inserted_act,
                             act_pronunciation,
                             act_event,
                             chatting_with,
                             chat,
                             chatting_with_buffer,
                             chatting_end_time,
                             act_obj_description,
                             act_obj_pronunciation,
                             act_obj_event,
                             act_start_time)


def _chat_react(maze, persona, focused_event, reaction_mode, personas):
    """
    创建一个对话反应。

    参数：
        maze: 当前世界的<Maze>实例。
        persona: 当前的<Persona>实例。
        focused_event: 重点关注的事件。
        reaction_mode: 反应模式。
        personas: 包含所有persona名称为键，<Persona>实例为值的字典。
    """
    # 获取对话的两个persona实例
    init_persona = persona
    target_persona = personas[reaction_mode[9:].strip()]
    curr_personas = [init_persona, target_persona]

    # 生成对话内容及持续时间
    convo, duration_min = generate_convo(maze, init_persona, target_persona)
    convo_summary = generate_convo_summary(init_persona, convo)
    inserted_act = convo_summary
    inserted_act_dur = duration_min

    act_start_time = target_persona.scratch.act_start_time

    curr_time = target_persona.scratch.curr_time
    if curr_time.second != 0: 
        temp_curr_time = curr_time + datetime.timedelta(seconds=60 - curr_time.second)
        chatting_end_time = temp_curr_time + datetime.timedelta(minutes=inserted_act_dur)
    else: 
        chatting_end_time = curr_time + datetime.timedelta(minutes=inserted_act_dur)

    # 根据对话参与者的不同角色，创建对应的反应
    for role, p in [("init", init_persona), ("target", target_persona)]: 
        if role == "init": 
            act_address = f"<persona> {target_persona.name}"
            act_event = (p.name, "chat with", target_persona.name)
            chatting_with = target_persona.name
            chatting_with_buffer = {}
            chatting_with_buffer[target_persona.name] = 800
        elif role == "target": 
            act_address = f"<persona> {init_persona.name}"
            act_event = (p.name, "chat with", init_persona.name)
            chatting_with = init_persona.name
            chatting_with_buffer = {}
            chatting_with_buffer[init_persona.name] = 800

        act_pronunciation = "💬" 
        act_obj_description = None
        act_obj_pronunciation = None
        act_obj_event = (None, None, None)

        # 创建新的反应
        _create_react(p, inserted_act, inserted_act_dur,
                      act_address, act_event, chatting_with, convo, chatting_with_buffer, chatting_end_time,
                      act_pronunciation, act_obj_description, act_obj_pronunciation, 
                      act_obj_event, act_start_time)


def _wait_react(persona, reaction_mode): 
    """
    创建一个等待反应。

    参数：
        persona: 当前的<Persona>实例。
        reaction_mode: 反应模式。
    """
    p = persona

    # 解析反应模式中的等待时间
    inserted_act = f'waiting to start {p.scratch.act_description.split("(")[-1][:-1]}'
    end_time = datetime.datetime.strptime(reaction_mode[6:].strip(), "%B %d, %Y, %H:%M:%S")
    inserted_act_dur = (end_time.minute + end_time.hour * 60) - (p.scratch.curr_time.minute + p.scratch.curr_time.hour * 60) + 1

    act_address = f"<waiting> {p.scratch.curr_tile[0]} {p.scratch.curr_tile[1]}"
    act_event = (p.name, "waiting to start", p.scratch.act_description.split("(")[-1][:-1])
    chatting_with = None
    chat = None
    chatting_with_buffer = None
    chatting_end_time = None

    act_pronunciation = "⌛" 
    act_obj_description = None
    act_obj_pronunciation = None
    act_obj_event = (None, None, None)

    # 创建新的反应
    _create_react(p, inserted_act, inserted_act_dur,
                  act_address, act_event, chatting_with, chat, chatting_with_buffer, chatting_end_time,
                  act_pronunciation, act_obj_description, act_obj_pronunciation, 
                  act_obj_event)


def plan(persona, maze, personas, new_day, retrieved): 
    """
    人物的主要认知功能。根据检索到的记忆和感知以及迷宫和新的一天状态，
    进行长期和短期规划。

    参数： 
        maze: 当前世界的<Maze>实例。
        personas: 包含所有persona名称为键，<Persona>实例为值的字典。
        new_day: 表示是否是“新的一天”周期的布尔值或字符串。
        retrieved: 从Persona的联想记忆中检索到的<ConceptNode>字典。
    返回：
        persona.scratch.act_address: persona的目标行动地址。
    """ 
    # 部分1：生成每小时的日程安排
    if new_day: 
        _long_term_planning(persona, new_day)

    # 部分2：如果当前行动已结束，则创建新的计划
    if persona.scratch.act_check_finished(): 
        _determine_action(persona, maze)

    # 部分3：如果感知到需要响应的事件，检索相关信息
    # 步骤1：选择要重点关注的事件
    focused_event = False
    if retrieved.keys(): 
        focused_event = _choose_retrieved(persona, retrieved)
  
    # 步骤2：确定是否有必要做出反应
    if focused_event: 
        reaction_mode = _should_react(persona, focused_event, personas)
        if reaction_mode: 
            # 如果需要对话，则生成对话内容
            if reaction_mode[:9] == "chat with":
                _chat_react(maze, persona, focused_event, reaction_mode, personas)
            elif reaction_mode[:4] == "wait": 
                _wait_react(persona, reaction_mode)

    # 步骤3：清理与对话相关的状态
    if persona.scratch.act_event[1] != "chat with":
        persona.scratch.chatting_with = None
        persona.scratch.chat = None
        persona.scratch.chatting_end_time = None

    # 更新聊天缓冲区的计数
    curr_persona_chat_buffer = persona.scratch.chatting_with_buffer
    for persona_name, buffer_count in curr_persona_chat_buffer.items():
        if persona_name != persona.scratch.chatting_with: 
            persona.scratch.chatting_with_buffer[persona_name] -= 1

    return persona.scratch.act_address
