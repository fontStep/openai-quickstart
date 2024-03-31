import os
import sys

#将当前脚本文件所在目录添加到 Python 解释器的模块搜索路径中。

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import ArgumentParser, ConfigLoader, LOG
from model import GLMModel, OpenAIModel
from translator import PDFTranslator


if __name__ == '__main__':
    #初始化命令行参数解析器
    argument_parser = ArgumentParser()
    #加载命令行参数
    args = argument_parser.parse_arguments()
    LOG.info(f"args: {args}")
    #加载配置文件
    config_loader = ConfigLoader(args.config)

    config = config_loader.load_config()

    model_name = args.openai_model if args.openai_model else config['OpenAIModel']['model']
    api_key = args.openai_api_key if args.openai_api_key else config['OpenAIModel']['api_key']
    open_ai_base_url = args.openai_base_url if args.openai_base_url else config['OpenAIModel']['base_url']
    model = OpenAIModel(model=model_name, api_key=api_key,base_url=open_ai_base_url)

    #需要翻译的文件路径
    pdf_file_path = args.book if args.book else config['common']['book']
    #翻译后的输出格式
    file_format = args.file_format if args.file_format else config['common']['file_format']

    # 实例化 PDFTranslator 类，并调用 translate_pdf() 方法
    translator = PDFTranslator(model)
    translator.translate_pdf(pdf_file_path, file_format)

    
