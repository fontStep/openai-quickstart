from book import ContentType

class Model:
    #创建文本翻译prompt
    def make_text_prompt(self, text: str, target_language: str) -> str:
        
        prompt = f"""  
            You are a highly skilled AI trained in language translation.   
            I would like you to translate the following text enclosed in double quotes into {target_language} language,   
            ensuring that the translation is colloquial and authentic.   
            Only give me the output and nothing else.   
            Do not wrap responses in  double quotes.
            Return in original format.\n  
            "{text}"  
            """ 
        return prompt

    #构建table 翻译 prompt
    def make_table_prompt(self, table: str, target_language: str) -> str:
        
        prompt = f"""  
            You are a highly skilled AI trained in language translation.   
            I would like you to translate the following text enclosed in double quotes into {target_language} language,   
            ensuring that the translation is colloquial and authentic.   
            Only give me the output and nothing else.   
            Do not wrap responses in double quotes.
            Return in original format.  
            The contents of each column are separated by commas, and the contents of each row are separated by newlines.
            "{table}"  
            """
        return prompt

    #提供对外翻译的接口
    def translate_prompt(self, content, target_language: str) -> str:
        if content.content_type == ContentType.TEXT:
            return self.make_text_prompt(content.original, target_language)
        elif content.content_type == ContentType.TABLE:
            return self.make_table_prompt(content.get_original_as_str(), target_language)
    #翻译的接口
    def make_request(self, prompt):
        raise NotImplementedError("子类必须实现 make_request 方法")
