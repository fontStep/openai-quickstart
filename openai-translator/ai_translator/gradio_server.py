

import gradio as gr
import os
import sys

#将当前脚本文件所在目录添加到 Python 解释器的模块搜索路径中。

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

current_directory = os.path.dirname(__file__)

from utils import ArgumentParser, ConfigLoader, LOG
from model import GLMModel, OpenAIModel
from translator import PDFTranslator





def translator(pdf_file,model_type,open_ai_key,target_language,output_format,model_name):

    api_key = open_ai_key

    

    if model_type == 'GLMModel':
        model = GLMModel(model_url=model_name)
    elif model_type == 'OpenAIModel':
        model = OpenAIModel(model=model_name, api_key=api_key)    

    #需要翻译的文件路径
    pdf_file_path = pdf_file.name
    
    file_name = os.path.basename(pdf_file_path)
    
    output_file_name  = file_name.replace('.pdf', f'_translated.pdf')
    
    # LOG.info(f'文件名：{file.filename}')
    output_file_path = os.path.join( os.path.dirname(current_directory),"tests",output_file_name )
    
    
    #翻译后的输出格式
    file_format = output_format

    # 实例化 PDFTranslator 类，并调用 translate_pdf() 方法
    translator = PDFTranslator(model)
    output_file_path = translator.translate_pdf(pdf_file_path, file_format,target_language,output_file_path)    
    return output_file_path

def create_translation_interface():
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column(scale=6):
                pdf_file = gr.File(label="上传PDF文件", file_types=[".pdf"])
                out_file = gr.File(label="下载翻译文件")
            with gr.Column(scale=5):
                with gr.Row():                                   
                    model_type = gr.Dropdown(["OpenAIModel", "GLMModel"], label="model type", value="OpenAIModel", info="Will select model_type as transformer")
                    model_name = gr.Dropdown(["gpt-3.5-turbo"], label="model name", value="gpt-3.5-turbo", info="Will select model_name as transformer")
                with gr.Row():    
                    open_ai_key = gr.Textbox(label="openai api key", info=" openAI API key")
                    target_language = gr.Dropdown(["Chinese", "English", "Japanese"], label="target language",value='English')
                with gr.Row():
                    
                    output_format = gr.Dropdown(["PDF", "markdown"], label="Output file format", value = "PDF")
                    submit = gr.Button("Submit")
                    submit.click(
                        translator, 
                        inputs=[
                            pdf_file,
                            model_type,
                            open_ai_key,
                            target_language,
                            output_format,
                            model_name
                        ], 
                        outputs=[out_file]
                        )
    return demo




if __name__ == '__main__':
    translation_interface = create_translation_interface()
    translation_interface.launch()

    
