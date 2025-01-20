# text2diff：自然语言描述修改文本
一个利用LLM能力将自然语言修改描述转换为文本差异（diff）并可视化展示的工具

## 简介
- 本项目是实验性工程，欢迎提出建议和贡献代码
- 核心功能：通过自然语言描述来修改文本，并可视化展示修改前后的差异

## 功能特点
- 可视化展示文本修改前后的差异
- 支持通过自然语言描述来修改文本
- 修改过程可预览、可确认
- 基于Gradio构建的交互式Web界面

## 安装

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置LLM的API Key
参考[ell文档-配置API Key部分](https://docs.ell.so/installation.html#api-key-setup)

#### 使用OpenAI模型
1. 从OpenAI官网获取API Key
2. 设置环境变量（不建议直接写在代码里）
```
#Windows  也可在系统设置里添加环境变量
setx OPENAI_API_KEY=your-api-key
#Mac/Linux
export OPENAI_API_KEY=your-api-key
```

#### 使用智谱AI模型（其它的类似）
1. 从智谱开放平台获取API Key
2. 设置环境变量（不建议直接写在代码里）
```
#Windows  也可在系统设置里添加环境变量
setx ZHIPU_API_KEY=your-api-key
#Mac/Linux
export ZHIPU_API_KEY=your-api-key
```

### 修改模型配置
1. 在`core/__init__.py`中修改`MODEL_NAME`变量即可切换模型
2. 调用`ell.config.register_model()`注册模型
```
#以智谱AI为例
MODEL_NAME = "glm-4-flash"
api_key = os.getenv("ZHIPU_API_KEY")

client = openai.OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4/"
) 
ell.config.register_model(MODEL_NAME, client)

#如果使用OpenAI模型，可无需注册模型
```

### 运行程序
```bash
python app.py
```
可以看到终端显示
```
ell init success, current model: gpt-4o-mini
* Running on local URL:  http://127.0.0.1:7860
```
打开浏览器访问上面的网址即可使用

## 使用说明

1. **输入原文**
   - 在"原文"标签页中输入或粘贴需要修改的文本
   - 文本区域支持多行输入，适合处理较长的文档

2. **描述修改**
   - 在下方文本框中用自然语言描述你希望如何修改文本
   - 例如："将第一段改写得更简洁"，"将所有'我们'改为'他们'"

3. **预览修改**
   - 点击"AI修订"按钮，系统将根据你的描述生成修改建议
   - 修改结果会显示在"修订"标签页中，并以高亮方式展示差异

4. **确认修改**
   - 如果对修改结果满意，可以点击"确认修改"按钮应用修改
   - 修改后的文本将成为新的原文，可以继续在此基础上进行修改

## RoadMap
1. 支持更多格式的文本输入（Markdown、Word等）
2. 增加修改历史记录功能
3. 支持多轮修改对话
4. 增加修改建议的撤销/重做功能
5. 支持导出修改前后的对比文档
6. 增加对超长文本的分块处理支持
7. 支持自定义修改提示词模板

## License
本项目采用 [MIT License](LICENSE) 开源协议。