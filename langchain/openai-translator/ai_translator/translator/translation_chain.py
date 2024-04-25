from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatZhipuAI

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from translator.cutsom_chatglm import CutsomChatGLM3

from utils import LOG

class TranslationChain:
    def __init__(self, model_name: str = "gpt-3.5-turbo", verbose: bool = True):
        
        # 翻译任务指令始终由 System 角色承担
        template = (
            """You are a translation expert, proficient in various languages. \n
            and proficient in all kinds of style translation. Please use style: '{translation_style}'
            Translates {source_language} to {target_language}. 
            Please do not return untranslated content
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
        
        LOG.info(f"Initializing translation chain with model {model_name}")

        if(model_name.find('gpt')!=-1):
            chat = ChatOpenAI(model_name=model_name, temperature=0, verbose=verbose)
        else:
            chat = CutsomChatGLM3(
            endpoint_url="https://open.bigmodel.cn/api/paas/v4/chat/completions",
            max_tokens=1024,
            model_name=model_name
            )
            # chat = CustomChatZhipuAI(model_name=model_name,temperature=0,verbose=True)
        
        self.chain = LLMChain(llm=chat, prompt=chat_prompt_template, verbose=verbose)

    def run(self, text: str, source_language: str, target_language: str,translation_style:str) -> (str, bool):
        result = ""
        try:
            result = self.chain.invoke({
                "text": text,
                "source_language": source_language,
                "target_language": target_language,
                "translation_style":translation_style
            })['text']
        except Exception as e:
            LOG.error(f"An error occurred during translation: {e}")
            return result, False

        return result, True