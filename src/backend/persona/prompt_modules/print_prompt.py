"""
作者: Joon Sung Park (joonspk@stanford.edu)

文件: print_prompt.py
描述: 在 verbose 设置为 True 时打印提示信息。
"""
import sys
sys.path.append('../')

import json
import numpy
import datetime
import random

from opensource.generative_agent_simple.backend.global_methods import *
from opensource.generative_agent_simple.backend.gpt_structure import *
from utils import *

##############################################################################
#                       人设 第一章: 提示结构                                 #
##############################################################################

def print_run_prompts(prompt_template=None, 
                      persona=None, 
                      gpt_param=None, 
                      prompt_input=None,
                      prompt=None, 
                      output=None): 
    """
    打印运行提示信息

    参数:
    prompt_template: str, 提示模板
    persona: obj, 人设
    gpt_param: obj, GPT 参数
    prompt_input: str, 提示输入
    prompt: str, 提示
    output: str, 输出
    """
    print (f"=== {prompt_template}")
    print ("~~~ 人设    ---------------------------------------------------")
    print (persona.name, "\n")
    print ("~~~ GPT 参数 ----------------------------------------------------")
    print (gpt_param, "\n")
    print ("~~~ 提示输入    ----------------------------------------------")
    print (prompt_input, "\n")
    print ("~~~ 提示    ----------------------------------------------------")
    print (prompt, "\n")
    print ("~~~ 输出    ----------------------------------------------------")
    print (output, "\n") 
    print ("=== END ==========================================================")
    print ("\n\n\n")
