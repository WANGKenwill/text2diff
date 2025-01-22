[中文](README.md) | English

# text2diff: Modify Text with Natural Language Descriptions
A tool that leverages LLM capabilities to convert natural language descriptions of modifications into text diff data and visualize the changes.

## Introduction
- This project is experimental. Suggestions and code contributions are welcome!
- Core functionality: Modify text through natural language descriptions and visualize the differences before and after modification.

## Features
- Modify text using natural language descriptions, making it more convenient than manual editing and more accessible than writing code.
- Interactive web interface built with Gradio, allowing preview and confirmation of modifications.

## Installation

### Install Dependencies
```bash
# Install main dependencies (for running the main application)
pip install .

# Install development dependencies (for running scripts and tests)
pip install ".[dev]"
```

### Configure LLM API Key
Refer to the [ell documentation - API Key Setup section](https://docs.ell.so/installation.html#api-key-setup).

#### Using OpenAI Models
1. Obtain an API Key from the OpenAI website.
2. Set the environment variable (not recommended to hardcode in the code):
```bash
# Windows (can also add environment variables in system settings)
setx OPENAI_API_KEY=your-api-key
# Mac/Linux
export OPENAI_API_KEY=your-api-key
```

#### Using Zhipu AI Models (similar for others)
1. Obtain an API Key from the Zhipu Open Platform.
2. Set the environment variable (not recommended to hardcode in the code):
```bash
# Windows (can also add environment variables in system settings)
setx ZHIPU_API_KEY=your-api-key
# Mac/Linux
export ZHIPU_API_KEY=your-api-key
```

### Modify Model Configuration
1. Change the `MODEL_NAME` variable in `src/core/__init__.py` to switch models.
2. Call `ell.config.register_model()` to register the model.
```python
# Example for Zhipu AI
MODEL_NAME = "glm-4-flash"
api_key = os.getenv("ZHIPU_API_KEY")

client = openai.OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)
ell.config.register_model(MODEL_NAME, client)

# If using OpenAI models, no need to register the model.
```

### Run the Program
```bash
python app.py
```
You should see the following output in the terminal:
```
ell init success, current model: gpt-4o-mini
* Running on local URL:  http://127.0.0.1:7860
```
Open your browser and visit the URL above to use the application.

## Usage Instructions

1. **Input Original Text**
   - Enter the text to be modified in the "原文" tab.

2. **Describe Modifications**
   - Use natural language to describe how you want to modify the text in the text box below.
   - For example: "Change 'We' to 'They'".

3. **Preview Modifications**
   - Click the "AI修订" button, and the system will generate modification suggestions based on your description.
   - The revised result will be displayed in the "修订" tab, with differences highlighted.

4. **Confirm Modifications**
   - If satisfied with the revision, click the "确认修改" button to apply the changes.

## Roadmap
1. Add support for chunking long texts.
2. Add more natural language positioning instructions (e.g., targeting text by paragraph or line number).
3. Add support for more natural language instructions that declare requirements without directly providing revised content.
4. Support more text input formats (Markdown, Word, etc.).
5. Support more export formats (Markdown, Word, etc.).

## License
This project is licensed under the [MIT License](LICENSE).