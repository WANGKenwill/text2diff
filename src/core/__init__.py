import os
import openai
import ell
import sys

#免费中文大模型
MODEL_NAME = "glm-4-flash"
api_key = os.getenv("ZHIPU_API_KEY")

client = openai.OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4/"
) 
ell.config.register_model(MODEL_NAME, client)

# MODEL_NAME = "deepseek-chat"
# api_key = os.getenv("DEEPSEEK_API_KEY")

# client = openai.OpenAI(
#     api_key=api_key,
#     base_url="https://api.deepseek.com"
# ) 
# ell.config.register_model(MODEL_NAME, client)


#有OPENAI API KEY的可以换成OPENAI的模型
#由于默认client就是openai的，所以只需要修改MODEL_NAME即可，无需额外调用register_model

# MODEL_NAME = "gpt-4o-mini"

ell.init(store='./logdir', autocommit=True, verbose=True)

#把当前可用的model打印出来
print(f"ell init success, current model: {MODEL_NAME}")

