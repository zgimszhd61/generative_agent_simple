import json
import datetime

class Scratch: 
    def __init__(self, f_saved): 
        # 人物参数
        # <vision_r>表示人物周围可见的瓷砖数量。
        self.vision_r = 4
        # <att_bandwidth> 待办
        self.att_bandwidth = 3
        # <retention> 待办
        self.retention = 5

        # 世界信息
        # 感知到的世界时间
        self.curr_time = None
        # 人物当前的 x、y 瓷砖坐标
        self.curr_tile = None
        # 感知到的世界每日需求
        self.daily_plan_req = None
        
        # 人物核心身份
        # 人物的基本信息
        self.name = None
        self.first_name = None
        self.last_name = None
        self.age = None
        # L0 永久核心特征
        self.innate = None
        # L1 稳定特征
        self.learned = None
        # L2 外部实施
        self.currently = None
        self.lifestyle = None
        self.living_area = None

        # 反思变量
        self.concept_forget = 100
        self.daily_reflection_time = 60 * 3
        self.daily_reflection_size = 5
        self.overlap_reflect_th = 2
        self.kw_strg_event_reflect_th = 4
        self.kw_strg_thought_reflect_th = 4

        # 新的反思变量
        self.recency_w = 1
        self.relevance_w = 1
        self.importance_w = 1
        self.recency_decay = 0.99
        self.importance_trigger_max = 150
        self.importance_trigger_curr = self.importance_trigger_max
        self.importance_ele_n = 0 
        self.thought_count = 5

        # 人物规划
        # <daily_req> 是人物今天想要实现的各种目标的列表。
        self.daily_req = []
        # <f_daily_schedule> 表示长期规划的一种形式。这列出了人物的日常计划。
        self.f_daily_schedule = []
        # <f_daily_schedule_hourly_org> 是 f_daily_schedule 的复制，但保留了每小时的原始非分解版本。
        self.f_daily_schedule_hourly_org = []
        
        # 当前行动
        # <address> 是行动发生的字符串地址。
        self.act_address = None
        # <start_time> 是行动开始的 Python datetime 实例。
        self.act_start_time = None
        # <duration> 是行动持续的分钟数。
        self.act_duration = None
        # <description> 是行动的字符串描述。
        self.act_description = None
        # <pronunciatio> 是 self.description 的描述表达。目前以表情符号实现。
        self.act_pronunciatio = None
        # <event_form> 表示人物当前参与的事件三元组。
        self.act_event = (self.name, None, None)

        # <obj_description> 是对象行动的字符串描述。
        self.act_obj_description = None
        # <obj_pronunciatio> 是对象行动的描述表达。目前以表情符号实现。
        self.act_obj_pronunciatio = None
        # <obj_event_form> 表示对象行动当前参与的事件三元组。
        self.act_obj_event = (self.name, None, None)

        # <chatting_with> 是当前人物正在与之聊天的人物的字符串名称。如果不存在，则为 None。
        self.chatting_with = None
        # <chat> 是保存两个人物之间对话的列表。它的形式是：[["Dolores Murphy", "Hi"], ["Maeve Jenson", "Hi"] ...]
        self.chat = None
        # <chatting_with_buffer> 是一个字典，保存了当前聊天的人物名称及其视野范围内的时间。
        # 例如，{"Dolores Murphy": 4}
        self.chatting_with_buffer = dict()
        self.chatting_end_time = None

        # <path_set> 如果我们已经计算了人物执行此动作的路径，则为 True。该路径存储在人物的 scratch.planned_path 中。
        self.act_path_set = False
        # <planned_path> 是描述人物执行 <curr_action> 所采取的路径的 x y 坐标元组（瓷砖）的列表。
        # 列表不包括人物当前的瓷砖，包括目的地瓷砖。
        self.planned_path = []

        if check_if_file_exists(f_saved): 
            # 如果有一个引导文件，就在这里加载它。
            scratch_load = json.load(open(f_saved))

            self.vision_r = scratch_load["vision_r"]
            self.att_bandwidth = scratch_load["att_bandwidth"]
            self.retention = scratch_load["retention"]

            if scratch_load["curr_time"]: 
                self.curr_time = datetime.datetime.strptime(scratch_load["curr_time"], "%B %d, %Y, %H:%M:%S")
            else: 
                self.curr_time = None
            self.curr_tile = scratch_load["curr_tile"]
            self.daily_plan_req = scratch_load["daily_plan_req"]

            self.name = scratch_load["name"]
            self.first_name = scratch_load["first_name"]
            self.last_name = scratch_load["last_name"]
            self.age = scratch_load["age"]
            self.innate = scratch_load["innate"]
            self.learned = scratch_load["learned"]
            self.currently = scratch_load["currently"]
            self.lifestyle = scratch_load["lifestyle"]
            self.living_area = scratch_load["living_area"]

            self.concept_forget = scratch_load["concept_forget"]
            self.daily_reflection_time = scratch_load["daily_reflection_time"]
            self.daily_reflection_size = scratch_load["daily_reflection_size"]
            self.overlap_reflect_th = scratch_load["overlap_reflect_th"]
            self.kw_strg_event_reflect_th = scratch_load["kw_strg_event_reflect_th"]
            self.kw_strg_thought_reflect_th = scratch_load["kw_strg_thought_reflect_th"]

            self.recency_w = scratch_load["recency_w"]
            self.relevance_w = scratch_load["relevance_w"]
            self.importance_w = scratch_load["importance_w"]
            self.recency_decay = scratch_load["recency_decay"]
            self.importance_trigger_max = scratch_load["importance_trigger_max"]
            self.importance_trigger_curr = scratch_load["importance_trigger_curr"]
            self.importance_ele_n = scratch_load["importance_ele_n"]
            self.thought_count = scratch_load["thought_count"]

            self.daily_req = scratch_load["daily_req"]
            self.f_daily_schedule = scratch_load["f_daily_schedule"]
            self.f_daily_schedule_hourly_org = scratch_load["f_daily_schedule_hourly_org"]

            self.act_address = scratch_load["act_address"]
            if scratch_load["act_start_time"]: 
                self.act_start_time = datetime.datetime.strptime(scratch_load["act_start_time"], "%B %d, %Y, %H:%M:%S")
            else: 
                self.curr_time = None
            self.act_duration = scratch_load["act_duration"]
            self.act_description = scratch_load["act_description"]
            self.act_pronunciatio = scratch_load["act_pronunciatio"]
            self.act_event = tuple(scratch_load["act_event"])

            self.act_obj_description = scratch_load["act_obj_description"]
            self.act_obj_pronunciatio = scratch_load["act_obj_pronunciatio"]
            self.act_obj_event = tuple(scratch_load["act_obj_event"])

            self.chatting_with = scratch_load["chatting_with"]
            self.chat = scratch_load["chat"]
            self.chatting_with_buffer = scratch_load["chatting_with_buffer"]
            if scratch_load["chatting_end_time"]: 
                self.chatting_end_time = datetime.datetime.strptime(scratch_load["chatting_end_time"], "%B %d, %Y, %H:%M:%S")
            else:
                self.chatting_end_time = None

            self.act_path_set = scratch_load["act_path_set"]
            self.planned_path = scratch_load["planned_path"]


    def save(self, out_json):
        """
        保存人物的 scratch。 

        INPUT: 
          out_json: 我们将保存人物状态的文件。 
        OUTPUT: 
          None
        """
        scratch = dict() 
        scratch["vision_r"] = self.vision_r
        scratch["att_bandwidth"] = self.att_bandwidth
        scratch["retention"] = self.retention

        scratch["curr_time"] = self.curr_time.strftime("%B %d, %Y, %H:%M:%S")
        scratch["curr_tile"] = self.curr_tile
        scratch["daily_plan_req"] = self.daily_plan_req

        scratch["name"] = self.name
        scratch["first_name"] = self.first_name
        scratch["last_name"] = self.last_name
        scratch["age"] = self.age
        scratch["innate"] = self.innate
        scratch["learned"] = self.learned
        scratch["currently"] = self.currently
        scratch["lifestyle"] = self.lifestyle
        scratch["living_area"] = self.living_area

        scratch["concept_forget"] = self.concept_forget
        scratch["daily_reflection_time"] = self.daily_reflection_time
        scratch["daily_reflection_size"] = self.daily_reflection_size
        scratch["overlap_reflect_th"] = self.overlap_reflect_th
        scratch["kw_strg_event_reflect_th"] = self.kw_strg_event_reflect_th
        scratch["kw_strg_thought_reflect_th"] = self.kw_strg_thought_reflect_th

        scratch["recency_w"] = self.recency_w
        scratch["relevance_w"] = self.relevance_w
        scratch["importance_w"] = self.importance_w
        scratch["recency_decay"] = self.recency_decay
        scratch["importance_trigger_max"] = self.importance_trigger_max
        scratch["importance_trigger_curr"] = self.importance_trigger_curr
        scratch["importance_ele_n"] = self.importance_ele_n
        scratch["thought_count"] = self.thought_count

        scratch["daily_req"] = self.daily_req
        scratch["f_daily_schedule"] = self.f_daily_schedule
        scratch["f_daily_schedule_hourly_org"] = self.f_daily_schedule_hourly_org

        scratch["act_address"] = self.act_address
        scratch["act_start_time"] = self.act_start_time.strftime("%B %d, %Y, %H:%M:%S") if self.act_start_time else None
        scratch["act_duration"] = self.act_duration
        scratch["act_description"] = self.act_description
        scratch["act_pronunciatio"] = self.act_pronunciatio
        scratch["act_event"] = self.act_event

        scratch["act_obj_description"] = self.act_obj_description
        scratch["act_obj_pronunciatio"] = self.act_obj_pronunciatio
        scratch["act_obj_event"] = self.act_obj_event

        scratch["chatting_with"] = self.chatting_with
        scratch["chat"] = self.chat
        scratch["chatting_with_buffer"] = self.chatting_with_buffer
        scratch["chatting_end_time"] = self.chatting_end_time.strftime("%B %d, %Y, %H:%M:%S") if self.chatting_end_time else None

        scratch["act_path_set"] = self.act_path_set
        scratch["planned_path"] = self.planned_path

        with open(out_json, "w") as outfile:
            json.dump(scratch, outfile, indent=2)

    def get_f_daily_schedule_index(self, advance=0):
        # 获取当前时间到当天零点的分钟数
        today_min_elapsed = 0
        today_min_elapsed += self.curr_time.hour * 60
        today_min_elapsed += self.curr_time.minute
        today_min_elapsed += advance

        x = 0
        # 计算每日计划的总时长
        for task, duration in self.f_daily_schedule:
            x += duration

        # 初始化当前索引
        curr_index = 0
        elapsed = 0
        # 遍历每日计划并确定当前索引
        for task, duration in self.f_daily_schedule:
            elapsed += duration
            if elapsed > today_min_elapsed:
                return curr_index
            curr_index += 1

        return curr_index


    def get_f_daily_schedule_hourly_org_index(self, advance=0):
        # 获取当前时间到当天零点的分钟数
        today_min_elapsed = 0
        today_min_elapsed += self.curr_time.hour * 60
        today_min_elapsed += self.curr_time.minute
        today_min_elapsed += advance

        # 初始化当前索引
        curr_index = 0
        elapsed = 0
        # 遍历每小时的计划并确定当前索引
        for task, duration in self.f_daily_schedule_hourly_org:
            elapsed += duration
            if elapsed > today_min_elapsed:
                return curr_index
            curr_index += 1
        return curr_index


    def get_str_iss(self): 
        # 返回用户信息的字符串表示
        commonset = ""
        commonset += f"姓名：{self.name}\n"
        commonset += f"年龄：{self.age}\n"
        commonset += f"天赋特质：{self.innate}\n"
        commonset += f"学习特质：{self.learned}\n"
        commonset += f"当前状态：{self.currently}\n"
        commonset += f"生活方式：{self.lifestyle}\n"
        commonset += f"每日计划要求：{self.daily_plan_req}\n"
        commonset += f"当前日期：{self.curr_time.strftime('%A %B %d')}\n"
        return commonset


    # 下面的函数命名和功能注释略，因为功能直接可见于函数名和代码中的注释
    def get_str_name(self): 
        return self.name

    def get_str_firstname(self): 
        return self.first_name

    def get_str_lastname(self): 
        return self.last_name

    def get_str_age(self): 
        return str(self.age)

    def get_str_innate(self): 
        return self.innate

    def get_str_learned(self): 
        return self.learned

    def get_str_currently(self): 
        return self.currently

    def get_str_lifestyle(self): 
        return self.lifestyle

    def get_str_daily_plan_req(self): 
        return self.daily_plan_req

    def get_str_curr_date_str(self): 
        return self.curr_time.strftime("%A %B %d")

    def get_curr_event(self):
        if not self.act_address: 
            return (self.name, None, None)
        else: 
            return self.act_event

    def get_curr_event_and_desc(self): 
        if not self.act_address: 
            return (self.name, None, None, None)
        else: 
            return (self.act_event[0], 
                    self.act_event[1], 
                    self.act_event[2],
                    self.act_description)

    def get_curr_obj_event_and_desc(self): 
        if not self.act_address: 
            return ("", None, None, None)
        else: 
            return (self.act_address, 
                    self.act_obj_event[1], 
                    self.act_obj_event[2],
                    self.act_obj_description)

    def add_new_action(self, 
                       action_address, 
                       action_duration,
                       action_description,
                       action_pronunciatio, 
                       action_event,
                       chatting_with, 
                       chat, 
                       chatting_with_buffer,
                       chatting_end_time,
                       act_obj_description, 
                       act_obj_pronunciatio, 
                       act_obj_event, 
                       act_start_time=None): 
        self.act_address = action_address
        self.act_duration = action_duration
        self.act_description = action_description
        self.act_pronunciatio = action_pronunciatio
        self.act_event = action_event

        self.chatting_with = chatting_with
        self.chat = chat 
        if chatting_with_buffer: 
            self.chatting_with_buffer.update(chatting_with_buffer)
        self.chatting_end_time = chatting_end_time

        self.act_obj_description = act_obj_description
        self.act_obj_pronunciatio = act_obj_pronunciatio
        self.act_obj_event = act_obj_event
        
        self.act_start_time = self.curr_time
        
        self.act_path_set = False

    def act_time_str(self): 
        return self.act_start_time.strftime("%H:%M %p")

    def act_check_finished(self): 
        if not self.act_address: 
            return True
            
        if self.chatting_with: 
            end_time = self.chatting_end_time
        else: 
            x = self.act_start_time
            if x.second != 0: 
                x = x.replace(second=0)
                x = (x + datetime.timedelta(minutes=1))
            end_time = (x + datetime.timedelta(minutes=self.act_duration))

        if end_time.strftime("%H:%M:%S") == self.curr_time.strftime("%H:%M:%S"): 
            return True
        return False

    def act_summarize(self):
        exp = dict()
        exp["persona"] = self.name
        exp["address"] = self.act_address
        exp["start_datetime"] = self.act_start_time
        exp["duration"] = self.act_duration
        exp["description"] = self.act_description
        exp["pronunciatio"] = self.act_pronunciatio
        return exp

    def act_summary_str(self):
        start_datetime_str = self.act_start_time.strftime("%A %B %d -- %H:%M %p")
        ret = f"[{start_datetime_str}]\n"
        ret += f"活动：{self.name} 正在{self.act_description}\n"
        ret += f"地点：{self.act_address}\n"
        ret += f"持续时间（分钟）：{str(self.act_duration)} 分钟\n"
        return ret

    def get_str_daily_schedule_summary(self): 
        ret = ""
        curr_min_sum = 0
        for row in self.f_daily_schedule: 
            curr_min_sum += row[1]
            hour = int(curr_min_sum/60)
            minute = curr_min_sum%60
            ret += f"{hour:02}:{minute:02} || {row[0]}\n"
        return ret

    def get_str_daily_schedule_hourly_org_summary(self): 
        ret = ""
        curr_min_sum = 0
        for row in self.f_daily_schedule_hourly_org: 
            curr_min_sum += row[1]
            hour = int(curr_min_sum/60)
            minute = curr_min_sum%60
            ret += f"{hour:02}:{minute:02} || {row[0]}\n"
        return ret
