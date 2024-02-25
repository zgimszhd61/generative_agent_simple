"""
作者: Joon Sung Park (joonspk@stanford.edu)

文件: gpt_structure.py
描述: 调用 OpenAI API 的包装函数。
"""
import json
import random
import openai
import time 

from utils import *  # 导入自定义的工具函数
openai.api_key = openai_api_key  # 设置 OpenAI API 密钥

def ChatGPT_request(prompt): 
  """
  给定提示和 GPT 参数字典，向 OpenAI 服务器发出请求并返回响应。 
  参数:
    prompt: 字符串提示
  返回: 
    GPT-3 的响应字符串。 
  """
  # temp_sleep()
  try: 
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",  # 使用的 GPT 模型
    messages=[{"role": "user", "content": prompt}]  # 消息列表，用户角色的消息
    )
    return completion["choices"][0]["message"]["content"]  # 返回响应内容
  
  except: 
    print ("ChatGPT ERROR")
    return "ChatGPT ERROR"  # 处理异常情况，返回错误信息

prompt = """
---
Character 1: Maria Lopez is working on her physics degree and streaming games on Twitch to make some extra money. She visits Hobbs Cafe for studying and eating just about everyday.
Character 2: Klaus Mueller is writing a research paper on the effects of gentrification in low-income communities.

Past Context: 
138 minutes ago, Maria Lopez and Klaus Mueller were already conversing about conversing about Maria's research paper mentioned by Klaus This context takes place after that conversation.

Current Context: Maria Lopez was attending her Physics class (preparing for the next lecture) when Maria Lopez saw Klaus Mueller in the middle of working on his research paper at the library (writing the introduction).
Maria Lopez is thinking of initating a conversation with Klaus Mueller.
Current Location: library in Oak Hill College

(This is what is in Maria Lopez's head: Maria Lopez should remember to follow up with Klaus Mueller about his thoughts on her research paper. Beyond this, Maria Lopez doesn't necessarily know anything more about Klaus Mueller) 

(This is what is in Klaus Mueller's head: Klaus Mueller should remember to ask Maria Lopez about her research paper, as she found it interesting that he mentioned it. Beyond this, Klaus Mueller doesn't necessarily know anything more about Maria Lopez) 

Here is their conversation. 

Maria Lopez: "
---
将上述提示的响应输出为 JSON。输出应为一个列表的列表，内部列表的形式为 ["<Name>", "<Utterance>"]。输出多个话语，直到对话自然结束。
示例输出 JSON:
{"output": "[["Jane Doe", "Hi!"], ["John Doe", "Hello there!"] ... ]"}
"""

print (ChatGPT_request(prompt))
