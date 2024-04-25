from langchain.prompts  import (SystemMessagePromptTemplate,HumanMessagePromptTemplate,ChatPromptTemplate)
from langchain_community.llms.chatglm3 import ChatGLM3
from cutsom_chatglm import CutsomChatGLM3

from langchain_community.llms import ChatGLM
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os

if __name__ == "__main__":
        print(os.getenv("ZHIPUAI_API_KEY"))
        verbose=True
        model_name='glm-4'
        # 翻译任务指令始终由 System 角色承担
        template = (
                    """You are a translation expert, proficient in various languages. \n
                    Translates {source_language} to {target_language}. Translation style preservation {translation_style}\n
                    Please strictly ensure that the output format remains unchanged
                    """
            )
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)

                # 待翻译文本由 Human 角色输入
        human_template = "{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

                # 使用 System 和 Human 角色的提示模板构造 ChatPromptTemplate
        chat_prompt_template = ChatPromptTemplate.from_messages(
                    [system_message_prompt, human_message_prompt]
                )
                
        endpoint_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

        # messages = [
        #     AIMessage(content="我将从美国到中国来旅游，出行前希望了解中国的城市"),
        #     AIMessage(content="欢迎问我任何问题。"),
        # ]

        print("model_name",model_name)

        llm = CutsomChatGLM3(
            endpoint_url=endpoint_url,
            max_tokens=2000,
            model_name=model_name,
        )
        # chat = ChatZhipuAI(model_name=model_name, temperature=0, verbose=verbose)
                    

        chain = LLMChain(llm=llm, prompt=chat_prompt_template, verbose=verbose)
        
        result = chain.invoke({
                "text": 'This dataset contains two test samples provided by ChatGPT, an AI language model by OpenAI',
                "source_language": 'English',
                "target_language": 'Chinese',
                "translation_style":'novel'
            })
        
        print("result",result)
        
        
        