"""
一个简单的demo，调用CharacterGLM实现角色扮演，调用CogView生成图片，调用ChatGLM生成CogView所需的prompt。

依赖：
pyjwt
requests
streamlit
zhipuai
python-dotenv

运行方式：
```bash
streamlit run characterglm_api_demo_streamlit.py
```
"""

import requests
import time
import os
import random
import itertools
from typing import Literal, TypedDict, List, Union, Iterator, Optional
import json
import jwt

import streamlit as st
from dotenv import load_dotenv
import re


# 通过.env文件设置环境变量
# reference: https://github.com/theskumar/python-dotenv
load_dotenv()


## 数据类型 #####
class BaseMsg(TypedDict):
    pass


class TextMsg(BaseMsg):
    role: Literal["user", "assistant"]
    content: str


class ImageMsg(BaseMsg):
    role: Literal["image"]
    image: st.elements.image.ImageOrImageList
    caption: Optional[Union[str, List[str]]]


Msg = Union[TextMsg, ImageMsg]
TextMsgList = List[TextMsg]
MsgList = List[Msg]


class CharacterMeta(TypedDict):
    user_info: str  # 用户人设
    bot_info: str   # 角色人设
    bot_name: str   # bot扮演的角色的名字
    user_name: str  # 用户的名字


def filter_text_msg(messages: MsgList) -> TextMsgList:
    return [m for m in messages if m["role"] != "image"]




## api ##
# 智谱开放平台API key，参考 https://open.bigmodel.cn/usercenter/apikeys
API_KEY: str = os.getenv("ZHIPU_API_KEY")


class ApiKeyNotSet(ValueError):
    pass


def verify_api_key_not_empty():
    if not API_KEY:
        raise ApiKeyNotSet
def clear_file(file_path: str = 'chat_history.txt'):
    """
    清空指定文件的内容，若未提供文件路径，则默认清空'chat_history.txt'。

    参数:
    file_path (str): 要清空的文件路径，默认为'chat_history.txt'。

    返回:
    None
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            pass  # 不写入任何内容，只是打开并立即关闭，实现清空文件
        print(f"文件{file_path}的内容已被清空")
    except IOError as e:
        print(f"清空文件时发生错误: {e}")

# 初始化角色信息
def init_user_info(novel_content:str):
     """ 初始化人物信息 """
     if st.session_state["init_status"] !='init':
         pass
    #  print("初始化人物信息")
     from zhipuai import ZhipuAI
     client = ZhipuAI(api_key=API_KEY) # 请填写您自己的APIKey
     system_prompt = """
        你是一名作家，善于从文本中提取出人物的名称和人物人设,我需要你提取出人物的名称和人物人设,人物人设需要丰满些
        请以json的格式返回给我，
        我需要的字段是：人物名称、人物人设；如果人物名称和人物人设都没有，请不要输出。
        格式为
        {
            "人物名称": [],
            "人物人设": []
        }
        返回示例：
        {
            "人物名称": ["张三","李四"],
            "人物人设": ["张三是一个人，他很帅", "李四是一个人，他很美"]
        }
     """
     user_prompt = novel_content
     response = client.chat.completions.create(
         
        model="glm-4",  # 填写需要调用的模型名称
        messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )
     
     
     content = response.choices[0].message.content
    # 使用正则表达式匹配{}之间的内容
    #  print("人物信息结果:",content)
     pattern = re.compile(r'{.*?}', re.DOTALL)  # 匹配最短的大括号内容，包括换行符
     matches = pattern.findall(content)
     json_string=matches[0]
    # 使用json.loads()函数解析JSON字符串
     parsed_json = json.loads(json_string)
    # 打印解析后的JSON对象
    #  print("parsed_json:",parsed_json)
     st.session_state["meta"] = {
        "user_info": parsed_json["人物人设"][0],
        "bot_info": parsed_json["人物人设"][1],
        "bot_name":parsed_json["人物名称"][1],
        "user_name": parsed_json["人物名称"][0],
    }
    
 #初始化小说信息   
def init_novel_content():
     """ 初始化小说内容 """
    #  print("初始化小说内容")
     if st.session_state['init_status'] !='init':
        pass
     novel_system_prompt="""
     你是一名AI小说作家，擅长写言情小说
     """
     novel_user_prompt = """
        请帮我写一篇小说片段，要求
        1. 片段中只能有两个人物
        2. 片段描写不能包含敏感词，片段中人物描述需得体，不能太简单。
        3. 片段描写需要体现人物人设和人物姓名
    """
     from zhipuai import ZhipuAI
     client = ZhipuAI(api_key=API_KEY) # 请填写您自己的APIKey
     response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[
        {"role": "system", "content": novel_system_prompt},
        {"role": "user", "content": novel_user_prompt},
        ],
        temperature=0.01
     )
    #  print("小说内容：",response.choices[0].message.content)
     st.session_state["novel"] = response.choices[0].message.content
     return response.choices[0].message.content
 
#初始化原信息
def init_meta():
    if "init_status" not in st.session_state:
        st.session_state["init_status"] = "init"
       # 初始化
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "meta" not in st.session_state:
        st.session_state["meta"] = {
            
            "user_info": "",
            "bot_info": "",
            "bot_name":"",
            "user_name": "",
        }
    if "novel" not in st.session_state:
        st.session_state["novel"] =""
    if "stop_chat_flag" not in st.session_state:
        st.session_state["stop_chat_flag"] = False
    
    
            
    if st.session_state["init_status"] == "init":
        novel_content = init_novel_content()
        init_user_info(novel_content)
        # init_novel_content()
        st.session_state["init_status"] = "finish"
        clear_file()
init_meta()


def generate_token(apikey: str, exp_seconds: int):
    # reference: https://open.bigmodel.cn/dev/api#nosdk
    try:
        id, secret = apikey.split(".")
    except Exception as e:
        raise Exception("invalid apikey", e)
 
    payload = {
        "api_key": id,
        "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
        "timestamp": int(round(time.time() * 1000)),
    }
 
    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )


def get_characterglm_response(messages: TextMsgList, meta: CharacterMeta):
    """ 通过http调用characterglm """
    # print(f"get_characterglm_response,TextMsgList:{TextMsg},meta:{meta}")
    # Reference: https://open.bigmodel.cn/dev/api#characterglm
    verify_api_key_not_empty()
    url = "https://open.bigmodel.cn/api/paas/v3/model-api/charglm-3/sse-invoke"
    resp = requests.post(
        url,
        headers={"Authorization": generate_token(API_KEY, 1800)},
        json=dict(
            model="charglm-3",
            meta=meta,
            prompt=messages,
            incremental=True)
    )
    resp.raise_for_status()
    
    # 解析响应（非官方实现）
    sep = b':'
    last_event = None
    for line in resp.iter_lines():
        if not line or line.startswith(sep):
            continue
        field, value = line.split(sep, maxsplit=1)
        if field == b'event':
            last_event = value
        elif field == b'data' and last_event == b'add':
            yield value.decode()



### UI ###
st.set_page_config(page_title="CharacterGLM API Demo", page_icon="🤖", layout="wide")


def update_api_key(key: Optional[str] = None):
    global API_KEY
    key = key or st.session_state["API_KEY"]
    if key:
        API_KEY = key

# API_KEY 输入框
# print(f'api_key = {os.getenv("ZHIPUAI_API_KEY")}')
api_key = st.sidebar.text_input("API_KEY", value=os.getenv("ZHIPUAI_API_KEY"), key="API_KEY", type="password", on_change=update_api_key)

update_api_key(api_key)





def init_session():
    st.session_state["history"] = []


# 4个输入框，设置meta的4个字段
meta_labels = {
    "bot_name": "角色名",
    "user_name": "用户名", 
    "bot_info": "角色人设",
    "user_info": "用户人设",
}


# 显示小说
with st.container():
    cols1 = st.columns(1)
    cols1[0].text_area(label="小说", value=st.session_state["novel"], key="novel", help="小说")

# 2x2 layout
with st.container():
    col1, col2 = st.columns(2)
    with col1:    
        st.text_input(label="角色名",value=st.session_state["meta"]["bot_name"] ,key="bot_name", on_change=lambda : st.session_state["meta"].update(bot_name=st.session_state["bot_name"]), help="模型所扮演的角色的名字，不可以为空")
        st.text_area(label="角色人设", value=st.session_state["meta"]["bot_info"] ,key="bot_info", on_change=lambda : st.session_state["meta"].update(bot_info=st.session_state["bot_info"]), help="角色的详细人设信息，不可以为空")       
    with col2:
        st.text_input(label="用户名", value=st.session_state["meta"]["user_name"], key="user_name", on_change=lambda : st.session_state["meta"].update(user_name=st.session_state["user_name"]), help="用户的名字，默认为用户")
        st.text_area(label="用户人设", value=st.session_state["meta"]["user_info"], key="user_info", on_change=lambda : st.session_state["meta"].update(user_info=st.session_state["user_info"]), help="用户的详细人设信息，可以为空")
        

def verify_meta() -> bool:
    # 检查`角色名`和`角色人设`是否空，若为空，则弹出提醒
    if st.session_state["meta"]["bot_name"] == "" or st.session_state["meta"]["bot_info"] == "":
        st.error("角色名和角色人设不能为空")
        return False
    else:
        return True
    
button_labels = {
    # "clear_history": "清空对话历史",
    "stop_chat": "停止对话"
}

# 在同一行排列按钮
with st.container():
    n_button = len(button_labels)
    cols = st.columns(n_button)
    button_key_to_col = dict(zip(button_labels.keys(), cols))

    # with button_key_to_col["clear_history"]:
    #     clear_history = st.button(button_labels["clear_history"], key="clear_history")
    #     if clear_history:
    #         init_session()
    #         st.rerun()
    with button_key_to_col["stop_chat"]:
        stop_chat = st.button(button_labels["stop_chat"], key="stop_chat") 
        if stop_chat:
            st.session_state['stop_chat_flag'] = not st.session_state['stop_chat_flag']     

# 展示对话历史
for msg in st.session_state["history"]:
    if msg["role"] == "user":
        with st.chat_message(name="user", avatar="user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message(name="assistant", avatar="assistant"):
            st.markdown(msg["content"])
    else:
        raise Exception("Invalid role")





with st.chat_message(name="user", avatar="user"):
    input_placeholder = st.empty()
with st.chat_message(name="assistant", avatar="assistant"):
    message_placeholder = st.empty()


def output_stream_response(response_stream: Iterator[str], placeholder):
    content = ""
    for content in itertools.accumulate(response_stream):
        placeholder.markdown(content)
    return content


### UI ###

def get_characterglm_response_assistant():
    response_stream = get_characterglm_response(filter_text_msg(st.session_state["history"]), meta=st.session_state["meta"])
    bot_response = output_stream_response(response_stream, message_placeholder)
    if not bot_response:
        message_placeholder.markdown("生成出错")
        st.session_state["history"].pop()
    else:
        st.session_state["history"].append(TextMsg({"role": "assistant", "content": bot_response}))
        write_to_file(content=st.session_state["meta"]["bot_name"]+":"+bot_response)
    return bot_response    

def get_characterglm_response_user():
    # st.session_state["history"].append(TextMsg({"role": "user", "content": bot_response}))
    response_stream = get_characterglm_response(filter_text_msg(st.session_state["history"]), meta=st.session_state["meta"])
    bot_response = output_stream_response(response_stream, input_placeholder)
    if not bot_response:
        input_placeholder.markdown("生成出错")
        st.session_state["history"].pop()
    else:
        st.session_state["history"].append(TextMsg({"role": "user", "content": bot_response}))
        write_to_file(content=st.session_state["meta"]["user_name"]+":"+bot_response)
 
 
 
def generate_opening_remark() -> str:
    system_prompt="""
    
        你是一个著名的小说作家，擅长写言情小说,现在你需要根据小说的内容和角色编写一句开场白
    """
    user_prompt = f"""
    
        小说内容：{st.session_state["novel"]}
        角色：{st.session_state["meta"]["user_name"]}
        
    """
    from zhipuai import ZhipuAI
    client = ZhipuAI(api_key=API_KEY) # 请填写您自己的APIKey
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
        ],
        temperature=0.01
    )  
    return response.choices[0].message.content

def write_to_file(file_path: str = 'chat_history.txt',content: str=''):
    """
    向指定文件写入内容，若未提供文件路径，则默认写入到'chat_history.txt'。

    参数:
    file_path (str): 要写入的文件路径，默认为'chat_history.txt'。
    content (str): 要写入文件的内容。

    返回:
    None
    """
    try:
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(content+"\n")
        # print(f"内容已成功写入文件: {file_path}")
    except IOError as e:
        print(f"写入文件时发生错误: {e}")


def start_chat():
    opening_remark = generate_opening_remark()
    st.session_state["history"].append(TextMsg({"role": "user", "content": opening_remark}))
    write_to_file(content=st.session_state["meta"]["user_name"]+":"+opening_remark)
    
    input_placeholder.markdown(opening_remark)
    loop_count =0
    while not st.session_state["stop_chat_flag"] :
        # 生成角色回复
       get_characterglm_response_assistant()
       # 生成用户回复
       get_characterglm_response_user()
    
       loop_count += 1
       
start_chat()      