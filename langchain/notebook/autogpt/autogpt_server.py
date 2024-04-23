import gradio as gr
import os
import sys

from langchain_experimental.autonomous_agents import AutoGPT
from langchain_openai import ChatOpenAI
from langchain.tools import Tool , WriteFileTool,ReadFileTool

from langchain.utilities import SerpAPIWrapper

import faiss
from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore

from langchain_openai import OpenAIEmbeddings

# OpenAI Embedding 模型
embeddings_model = OpenAIEmbeddings()

# OpenAI Embedding 向量维数
embedding_size = 1536
# 使用 Faiss 的 IndexFlatL2 索引
index = faiss.IndexFlatL2(embedding_size)
# 实例化 Faiss 向量数据库
vectorstore = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {})

search = SerpAPIWrapper()
tools = [
    Tool(
        name="search",
        func=search.run,
        description="useful for when you need to answer questions about current events. You should ask targeted questions",
    ),
    ReadFileTool(),
]


def init_autogpt(model_name:str='gpt-3.5-turbo'):
    global AGENT  
    AGENT = AutoGPT.from_llm_and_tools(
    ai_name="Jarvis",
    ai_role="Assistant",
    tools=tools,
    llm=ChatOpenAI(model_name=model_name, temperature=0, verbose=True),
    memory=vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": 0.8}),# 实例化 Faiss 的 VectorStoreRetriever
    )
    AGENT.chain.verbose = True
    
    

def chat(message,history):
    response = AGENT.run(message)
    print(f"response:{response}")
    return "123"

def launch_gradio():
    demo = gr.ChatInterface(
        fn=chat,
        title="聊天",
        # retry_btn=None,
        # undo_btn=None,
        chatbot=gr.Chatbot(height=600),
    )

    demo.launch(share=True, server_name="0.0.0.0")    
    pass

if __name__ == "__main__":
    
    init_autogpt()
    
    # 启动 Gradio 服务
    launch_gradio()

