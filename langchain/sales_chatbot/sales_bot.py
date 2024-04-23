import gradio as gr

from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
import os

import random
import time

from enum import Enum, unique, auto


def initialize_sales_bot(vector_store_dir: str="real_estates_sale"):
    print(f"vector_store_dir:{vector_store_dir}")
    db = FAISS.load_local(vector_store_dir, OpenAIEmbeddings(),allow_dangerous_deserialization=True)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0,base_url=os.getenv("OPENAI_BASE_URL"))
    
    global SALES_BOT    
    SALES_BOT = RetrievalQA.from_chain_type(llm,
                                           retriever=db.as_retriever(search_type="similarity_score_threshold",
                                                                     search_kwargs={"score_threshold": 0.8}))
    # 返回向量数据库的检索结果
    SALES_BOT.return_source_documents = True

    return SALES_BOT
def sales_chat(message,chat_history,enable_chat_checkbox):
    print(f"[message]{message}")
    print(f"[chat_history]{chat_history}")
    print(f"[enable_chat_checkbox]{enable_chat_checkbox}")
    # TODO: 从命令行参数中获取
    enable_chat = enable_chat_checkbox

    ans = SALES_BOT({"query": message})
    # 如果检索出结果，或者开了大模型聊天模式
    # 返回 RetrievalQA combine_documents_chain 整合的结果
    if ans["source_documents"] or enable_chat:
        print(f"[result]{ans['result']}")
        print(f"[source_documents]{ans['source_documents']}")
        chat_history.append((message,ans["result"]))
        return "", chat_history
    # 否则输出套路话术
    else:
         chat_history.append((message,"这个问题我要问问领导"))
         return "", chat_history
   
@unique
class Scene_enum(Enum):
    房产 = "real_estates_sale"
    冰箱 = "refrigerator_sales"
    数学培训 = "math_sales"

def change_scene(scene):
    print('scene:',scene)
    initialize_sales_bot(scene)
    #清空历史消息
    # chatbot = []
    return []
    

def launch_gradio():   
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Row():
                    scene_radio = gr.Radio(
                        [(member.name, member.value) for member in Scene_enum],
                        label="切换场景",
                        info="选择一个要咨询的场景",
                        value=Scene_enum.房产
                    )
                    enable_chat_checkbox = gr.Checkbox(
                        label="激活 AI", info="通过 AI 更好的回答问题", value=False
                    )
        with gr.Row():
            with gr.Column():
                chatbot = gr.Chatbot(height=600)
                message = gr.Textbox(placeholder="请输入问题", lines=1)
                submit = gr.Button("提交")
                clear = gr.ClearButton([message, chatbot]) 
                
        scene_radio.change(fn=change_scene, inputs=[scene_radio],outputs=chatbot)
        
        submit.click(fn=sales_chat, inputs=[message,chatbot,enable_chat_checkbox],outputs=[message,chatbot])
        
                           
    demo.launch(share=False)            

if __name__ == "__main__":
    # 初始化房产销售机器人
    initialize_sales_bot()
    # 启动 Gradio 服务
    launch_gradio()
