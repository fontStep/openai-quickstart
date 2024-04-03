from flask import Flask, request, render_template, send_file,jsonify
import gradio as gr
import os
import sys
import json

#将当前脚本文件所在目录添加到 Python 解释器的模块搜索路径中。
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import ArgumentParser, ConfigLoader, LOG
from model import GLMModel, OpenAIModel
from translator import PDFTranslator


app = Flask(__name__)
current_directory = os.path.dirname(__file__)

# 设置文件上传目录
STORE_FOLDER = 'tests'
app.config['STORE_FOLDER'] = STORE_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # 检查请求中是否包含文件
    if 'file' not in request.files:
        return render_template('index.html', message='未找到文件！')

    file = request.files['file']
    
    LOG.info(request.form)

    # 如果用户未选择文件，也返回提示信息
    if file.filename == '':
        return render_template('index.html', message='未选择文件！')
    
    output_format=request.form.get('output_format')
    
    if output_format == 'PDF':
       output_file_name  = file.filename.replace('.pdf', f'_translated.pdf')
    if output_format == 'Markdown':
       output_file_name  = file.filename.replace('.pdf', f'_translated.md') 
   
    
    # LOG.info(f'文件名：{file.filename}')
    output_file_path = os.path.join( os.path.dirname(current_directory),app.config['STORE_FOLDER'],output_file_name )
    
    store_file_path = os.path.join(os.path.dirname(current_directory),app.config['STORE_FOLDER'], file.filename)

    # 将文件保存到服务器
    file.save(store_file_path)
    
 
    translate_pdf(store_file_path=store_file_path,output_file_path=output_file_path)
    
    LOG.info(f'翻译完成，结果保存在 {output_file_path}')

    return  jsonify({'message': '文件上传成功！', 'file_name': output_file_name})  

def translate_pdf(store_file_path,output_file_path):
    
    model_type= request.form.get('model_type')
    
    model_name= request.form.get('model_name')
    
    api_key= request.form.get('api_key')
    
    output_format=request.form.get('output_format')

    target_language =request.form.get('target_language')
    
    if model_type == 'GLMModel':
        model = GLMModel(model_url=model_name)
    elif model_type == 'OpenAIModel':
        model = OpenAIModel(model=model_name, api_key=api_key)    
    
    # 实例化 PDFTranslator 类，并调用 translate_pdf() 方法
    translator = PDFTranslator(model)
    
    translator.translate_pdf(store_file_path, output_format,target_language,output_file_path)
       

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    LOG.info(f'下载文件：{filename}')
    # 检查文件是否存在
    filepath = os.path.join( os.path.dirname(current_directory),app.config['STORE_FOLDER'],filename )
    # 检查文件是否存在  
    if os.path.isfile(filepath):  
        # 使用 send_file 发送文件内容  
        
        LOG.info(f'下载文件：{filepath}')
        return send_file(filepath, as_attachment=True, download_name=filename)  
    else:  
        # 如果文件不存在，返回 404 错误  
        return "File not found", 404

if __name__ == '__main__':
    # 确保上传目录存在
    os.makedirs(STORE_FOLDER, exist_ok=True)
    # 启动应用
    app.run(debug=True)
