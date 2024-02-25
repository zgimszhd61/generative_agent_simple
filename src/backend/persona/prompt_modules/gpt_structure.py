import json
import random
import openai
import time 

from utils import *

openai.api_key = openai_api_key

def temp_sleep(seconds=0.1):
    """
    临时休眠函数，用于模拟请求间隔。
    """
    time.sleep(seconds)

def ChatGPT_single_request(prompt): 
    """
    向 OpenAI 发送单个请求并返回响应。
    """
    temp_sleep()

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt}]
    )
    return completion["choices"][0]["message"]["content"]


# ============================================================================
# #####################[SECTION 1: CHATGPT-3 结构] ######################
# ============================================================================

def GPT4_request(prompt): 
    """
    给定提示和 GPT 参数字典，向 OpenAI 发送请求并返回响应。
    """
    temp_sleep()

    try: 
        completion = openai.ChatCompletion.create(
        model="gpt-4", 
        messages=[{"role": "user", "content": prompt}]
        )
        return completion["choices"][0]["message"]["content"]

    except: 
        print ("ChatGPT ERROR")
        return "ChatGPT ERROR"


def ChatGPT_request(prompt): 
    """
    给定提示和 GPT 参数字典，向 OpenAI 发送请求并返回响应。
    """
    try: 
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt}]
        )
        return completion["choices"][0]["message"]["content"]

    except: 
        print ("ChatGPT ERROR")
        return "ChatGPT ERROR"


def GPT4_safe_generate_response(prompt, 
                                   example_output,
                                   special_instruction,
                                   repeat=3,
                                   fail_safe_response="error",
                                   func_validate=None,
                                   func_clean_up=None,
                                   verbose=False): 
    """
    生成 GPT-4 安全响应。
    """
    prompt = 'GPT-3 提示：\n"""\n' + prompt + '\n"""\n'
    prompt += f"以 JSON 格式输出上述提示的响应。{special_instruction}\n"
    prompt += "示例输出 JSON:\n"
    prompt += '{"output": "' + str(example_output) + '"}'

    if verbose: 
        print ("CHAT GPT 提示")
        print (prompt)

    for i in range(repeat): 

        try: 
            curr_gpt_response = GPT4_request(prompt).strip()
            end_index = curr_gpt_response.rfind('}') + 1
            curr_gpt_response = curr_gpt_response[:end_index]
            curr_gpt_response = json.loads(curr_gpt_response)["output"]

            if func_validate(curr_gpt_response, prompt=prompt): 
                return func_clean_up(curr_gpt_response, prompt=prompt)

            if verbose: 
                print ("---- 重复次数: \n", i, curr_gpt_response)
                print (curr_gpt_response)
                print ("~~~~")

        except: 
            pass

    return False


def ChatGPT_safe_generate_response(prompt, 
                                   example_output,
                                   special_instruction,
                                   repeat=3,
                                   fail_safe_response="error",
                                   func_validate=None,
                                   func_clean_up=None,
                                   verbose=False): 
    """
    生成 ChatGPT 安全响应。
    """
    prompt = '"""\n' + prompt + '\n"""\n'
    prompt += f"以 JSON 格式输出上述提示的响应。{special_instruction}\n"
    prompt += "示例输出 JSON:\n"
    prompt += '{"output": "' + str(example_output) + '"}'

    if verbose: 
        print ("CHAT GPT 提示")
        print (prompt)

    for i in range(repeat): 

        try: 
            curr_gpt_response = ChatGPT_request(prompt).strip()
            end_index = curr_gpt_response.rfind('}') + 1
            curr_gpt_response = curr_gpt_response[:end_index]
            curr_gpt_response = json.loads(curr_gpt_response)["output"]

            if func_validate(curr_gpt_response, prompt=prompt): 
                return func_clean_up(curr_gpt_response, prompt=prompt)

            if verbose: 
                print ("---- 重复次数: \n", i, curr_gpt_response)
                print (curr_gpt_response)
                print ("~~~~")

        except: 
            pass

    return False


def ChatGPT_safe_generate_response_OLD(prompt, 
                                   repeat=3,
                                   fail_safe_response="error",
                                   func_validate=None,
                                   func_clean_up=None,
                                   verbose=False): 
    """
    生成旧版 ChatGPT 安全响应。
    """
    if verbose: 
        print ("CHAT GPT 提示")
        print (prompt)

    for i in range(repeat): 
        try: 
            curr_gpt_response = ChatGPT_request(prompt).strip()
            if func_validate(curr_gpt_response, prompt=prompt): 
                return func_clean_up(curr_gpt_response, prompt=prompt)
            if verbose: 
                print (f"---- 重复次数: {i}")
                print (curr_gpt_response)
                print ("~~~~")

        except: 
            pass
    print ("安全响应触发") 
    return fail_safe_response


# ============================================================================
# ###################[SECTION 2: 原始 GPT-3 结构] ###################
# ============================================================================

def GPT_request(prompt, gpt_parameter): 
    """
    给定提示和 GPT 参数字典，向 OpenAI 发送请求并返回响应。
    """
    temp_sleep()
    try: 
        response = openai.Completion.create(
                    model=gpt_parameter["engine"],
                    prompt=prompt,
                    temperature=gpt_parameter["temperature"],
                    max_tokens=gpt_parameter["max_tokens"],
                    top_p=gpt_parameter["top_p"],
                    frequency_penalty=gpt_parameter["frequency_penalty"],
                    presence_penalty=gpt_parameter["presence_penalty"],
                    stream=gpt_parameter["stream"],
                    stop=gpt_parameter["stop"],)
        return response.choices[0].text
    except: 
        print ("TOKEN LIMIT EXCEEDED")
        return "TOKEN LIMIT EXCEEDED"


def generate_prompt(curr_input, prompt_lib_file): 
    """
    生成提示。
    """
    if type(curr_input) == type("string"): 
        curr_input = [curr_input]
    curr_input = [str(i) for i in curr_input]

    f = open(prompt_lib_file, "r")
    prompt = f.read()
    f.close()
    for count, i in enumerate(curr_input):   
        prompt = prompt.replace(f"!<INPUT {count}>!", i)
    if "<commentblockmarker>###</commentblockmarker>" in prompt: 
        prompt = prompt.split("<commentblockmarker>###</commentblockmarker>")[1]
    return prompt.strip()


def safe_generate_response(prompt, 
                           gpt_parameter,
                           repeat=5,
                           fail_safe_response="error",
                           func_validate=None,
                           func_clean_up=None,
                           verbose=False): 
    """
    生成安全响应。
    """
    if verbose: 
        print (prompt)

    for i in range(repeat): 
        curr_gpt_response = GPT_request(prompt, gpt_parameter)
        if func_validate(curr_gpt_response, prompt=prompt): 
            return func_clean_up(curr_gpt_response, prompt=prompt)
        if verbose: 
            print ("---- 重复次数: ", i, curr_gpt_response)
            print (curr_gpt_response)
            print ("~~~~")
    return fail_safe_response


def get_embedding(text, model="text-embedding-ada-002"):
    """
    获取文本嵌入。
    """
    text = text.replace("\n", " ")
    if not text: 
        text = "this is blank"
    return openai.Embedding.create(
            input=[text], model=model)['data'][0]['embedding']


if __name__ == '__main__':
    gpt_parameter = {"engine": "text-davinci-003", "max_tokens": 50, 
                   "temperature": 0, "top_p": 1, "stream": False,
                   "frequency_penalty": 0, "presence_penalty": 0, 
                   "stop": ['"']}
    curr_input = ["driving to a friend's house"]
    prompt_lib_file = "prompt_template/test_prompt_July5.txt"
    prompt = generate_prompt(curr_input, prompt_lib_file)

    def __func_validate(gpt_response): 
        if len(gpt_response.strip()) <= 1:
            return False
        if len(gpt_response.strip().split(" ")) > 1: 
            return False
        return True

    def __func_clean_up(gpt_response):
        cleaned_response = gpt_response.strip()
        return cleaned_response

    output = safe_generate_response(prompt, 
                                 gpt_parameter,
                                 5,
                                 "rest",
                                 __func_validate,
                                 __func_clean_up,
                                 True)

    print (output)
