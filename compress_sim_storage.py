import shutil
import json
from global_methods import *  # 假设这里是导入了一些全局方法

def compress(sim_code):
    # 设置原始模拟数据存储路径和压缩后存储路径
    sim_storage = f"../environment/frontend_server/storage/{sim_code}"
    compressed_storage = f"../environment/frontend_server/compressed_storage/{sim_code}"
    persona_folder = sim_storage + "/personas"  # 人物信息存储路径
    move_folder = sim_storage + "/movement"      # 移动信息存储路径
    meta_file = sim_storage + "/reverie/meta.json"  # 元数据文件路径

    # 获取所有人物名称
    persona_names = []
    for i in find_filenames(persona_folder, ""): 
        x = i.split("/")[-1].strip()
        if x[0] != ".": 
            persona_names += [x]

    # 获取最大移动次数
    max_move_count = max([int(i.split("/")[-1].split(".")[0]) 
                        for i in find_filenames(move_folder, "json")])
    
    persona_last_move = dict()  # 记录每个人物的上一次移动信息
    master_move = dict()        # 存储压缩后的移动信息
    for i in range(max_move_count+1): 
        master_move[i] = dict()
        with open(f"{move_folder}/{str(i)}.json") as json_file:  
            i_move_dict = json.load(json_file)["persona"]
            for p in persona_names: 
                move = False
                if i == 0: 
                    move = True
                elif (i_move_dict[p]["movement"] != persona_last_move[p]["movement"]
                    or i_move_dict[p]["pronunciatio"] != persona_last_move[p]["pronunciatio"]
                    or i_move_dict[p]["description"] != persona_last_move[p]["description"]
                    or i_move_dict[p]["chat"] != persona_last_move[p]["chat"]): 
                    move = True

                if move: 
                    # 更新上一次移动信息并添加到压缩后的移动信息中
                    persona_last_move[p] = {"movement": i_move_dict[p]["movement"],
                                            "pronunciatio": i_move_dict[p]["pronunciatio"], 
                                            "description": i_move_dict[p]["description"], 
                                            "chat": i_move_dict[p]["chat"]}
                    master_move[i][p] = {"movement": i_move_dict[p]["movement"],
                                        "pronunciatio": i_move_dict[p]["pronunciatio"], 
                                        "description": i_move_dict[p]["description"], 
                                        "chat": i_move_dict[p]["chat"]}

    # 创建压缩后存储路径
    create_folder_if_not_there(compressed_storage)
    # 将压缩后的移动信息写入文件
    with open(f"{compressed_storage}/master_movement.json", "w") as outfile:
        outfile.write(json.dumps(master_move, indent=2))

    # 复制元数据文件和人物信息到压缩后的存储路径
    shutil.copyfile(meta_file, f"{compressed_storage}/meta.json")
    shutil.copytree(persona_folder, f"{compressed_storage}/personas/")

if __name__ == '__main__':
    # 调用compress函数，传入模拟代码
    compress("July1_the_ville_isabella_maria_klaus-step-3-9")
