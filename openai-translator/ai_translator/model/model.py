from book import ContentType

class Model:
    #创建文本翻译prompt
    def make_text_prompt(self, text: str, target_language: str) -> str:
        return f"翻译为{target_language}：{text}"

    #构建table 翻译 prompt
    def make_table_prompt(self, table: str, target_language: str) -> str:
        return f"翻译为{target_language}，每列内容用逗号分隔,每行内容之间用换行符分隔 \n{table}"

    #提供对外翻译的接口
    def translate_prompt(self, content, target_language: str) -> str:
        if content.content_type == ContentType.TEXT:
            return self.make_text_prompt(content.original, target_language)
        elif content.content_type == ContentType.TABLE:
            return self.make_table_prompt(content.get_original_as_str(), target_language)
    #翻译的接口
    def make_request(self, prompt):
        raise NotImplementedError("子类必须实现 make_request 方法")
